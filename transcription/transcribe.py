import os
import json
import sys
import gc
import uuid
import traceback
import warnings
from datetime import datetime
from dotenv import load_dotenv
import whisperx
from emotionIntegration import FirebaseLogger

warnings.filterwarnings("ignore", category=UserWarning, module="pyannote.audio.core.io")

fb_logger = FirebaseLogger("../Integration/service-account.json") 
load_dotenv()

LANGUAGE   = "sv"
OUTPUT_DIR = "output"

def error_exit(message, details=None, session_id=None):
    """Visa felmeddelande i JSON-format och avsluta"""
    error_data = {
        "status": "error",
        "error": message,
        "timestamp": datetime.now().isoformat()
    }
    if session_id:
        error_data["sessionId"] = session_id
    if details:
        error_data["details"] = details
    
    print(json.dumps(error_data, ensure_ascii=False))
    
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        error_path = os.path.join(OUTPUT_DIR, f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(error_path, "w", encoding="utf-8") as f:
            json.dump(error_data, f, ensure_ascii=False, indent=2)
        print(f"Error saved to: {error_path}", file=sys.stderr)
    except Exception as e:
        print(f"Failed to save error file: {str(e)}", file=sys.stderr)
    
    sys.exit(1)

def warning_msg(message, session_id=None):
    """Visa varning i JSON-format"""
    warning_data = {
        "status": "warning",
        "warning": message,
        "timestamp": datetime.now().isoformat()
    }
    if session_id:
        warning_data["sessionId"] = session_id
    print(json.dumps(warning_data, ensure_ascii=False), file=sys.stderr)


HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    error_exit("HF_TOKEN not found in .env file", "Please create a .env file with your Hugging Face token")

if len(sys.argv) < 2:
    error_exit("Missing audio file argument", "Usage: python transcribe.py <audio_file> [session_id]")

# session_id kan skickas in som andra argument, annars genereras unikt ID
if len(sys.argv) > 2:
    session_id = sys.argv[2]
else:
    session_id = str(uuid.uuid4())
    warning_msg(f"No session ID provided, using generated: {session_id}")

audio_filename = sys.argv[1]

input_folder = os.path.join(os.path.dirname(__file__), "input")
AUDIO_FILE = os.path.join(input_folder, audio_filename)

if not os.path.exists(AUDIO_FILE):
    error_exit(f"Audio file not found: {audio_filename}\nExpected location: {input_folder}", session_id=session_id)

if not os.path.isfile(AUDIO_FILE):
    error_exit(f"Not a file: {AUDIO_FILE}", session_id=session_id)

file_size = os.path.getsize(AUDIO_FILE)
if file_size > 100 * 1024 * 1024:
    error_exit(f"Audio file too large: {file_size / 1024 / 1024:.1f}MB (max 100MB)", session_id=session_id)

if file_size == 0:
    error_exit(f"Audio file is empty: {AUDIO_FILE}", session_id=session_id)

try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
except Exception as e:
    error_exit(f"Cannot create output directory: {OUTPUT_DIR}", str(e), session_id)

DEVICE       = "cuda"      # or "cpu"
COMPUTE_TYPE = "float16"   # or "int8" for CPU
BATCH_SIZE   = 16

# CUDA kanske inte finns, faller tillbaka till CPU om så är fallet
if DEVICE == "cuda":
    try:
        import torch
        if not torch.cuda.is_available():
            warning_msg("CUDA not available, falling back to CPU", session_id)
            DEVICE = "cpu"
            COMPUTE_TYPE = "int8"
            BATCH_SIZE = 1
    except ImportError:
        warning_msg("PyTorch not installed, will use CPU", session_id)
        DEVICE = "cpu"
        COMPUTE_TYPE = "int8"
        BATCH_SIZE = 1

print(f"Using device: {DEVICE}", file=sys.stderr)

try:
    print("Loading audio...")
    audio = whisperx.load_audio(AUDIO_FILE)
    audio_duration = len(audio) / 16000
    print(f"Audio duration: {audio_duration:.2f} seconds", file=sys.stderr)

    # Varning för mycket korta ljudfiler där diarization kan vara opålitlig
    if audio_duration < 10:
        warning_msg(f"Audio duration is very short: {audio_duration:.2f} seconds - transcription may be inaccurate.", session_id)

    # Steg 1: Transkribera
    print("Loading Whisper model...")
    model = whisperx.load_model("large-v3-turbo", DEVICE, compute_type=COMPUTE_TYPE)

    print("Transcribing...", file=sys.stderr)
    result = model.transcribe(audio, language=LANGUAGE, batch_size=BATCH_SIZE)

    if not result.get("segments") or len(result["segments"]) == 0:
        warning_msg("No speech found in audio", session_id)
        result["segments"] = []

    gc.collect()
    if DEVICE == "cuda":
        torch.cuda.empty_cache()
    del model

    # Steg 2: Align (förbättra tidsstämplar)
    print("Aligning...")
    try: 
        model_a, metadata = whisperx.load_align_model(
            language_code=result["language"],
            device=DEVICE,
            model_name="WAV2VEC2_ASR_LARGE_LV60K_960H"
        )
        result = whisperx.align(
            result["segments"], model_a, metadata, audio, DEVICE, return_char_alignments=False
        )
    except Exception as e:
        warning_msg(f"Alignment failed, continuing without alignment: {str(e)}", session_id)

    gc.collect()
    if DEVICE == "cuda":
        torch.cuda.empty_cache()
    if 'model_a' in locals():
        del model_a

    # Steg 3: Klassificera segment (fråga = vuxen, svar = barn)
    raw_segments = []

    for seg in result.get("segments", []):
        if not seg.get("words"):
            continue

        text = " ".join([w["word"] for w in seg["words"]]).strip()

        if text.endswith("?"):
            seg_type = "question"
            speaker = "vuxen"
        elif len(raw_segments) > 0 and raw_segments[-1]["type"] == "question":
            seg_type = "answer"
            speaker = "barn"
        else:
            seg_type = "statement"
            speaker = "vuxen"

        raw_segments.append({
            "speaker": speaker,
            "text": text,
            "type": seg_type,
            "startMs": round(seg["words"][0]["start"] * 1000),
            "endMs": round(seg["words"][-1]["end"] * 1000),
        })

    # Steg 4: Bygg exchanges (fråga/svar-block)
    exchanges = []
    exchange_id = 1
    i = 0

    while i < len(raw_segments):
        if raw_segments[i]["type"] == "question":
            question = {
                "text": raw_segments[i]["text"],
                "speaker": raw_segments[i]["speaker"],
                "startMs": raw_segments[i]["startMs"],
                "endMs": raw_segments[i]["endMs"],
            }

            answer = None
            if i + 1 < len(raw_segments) and raw_segments[i+1]["type"] == "answer":
                answer = {
                    "text": raw_segments[i+1]["text"],
                    "speaker": raw_segments[i+1]["speaker"],
                    "startMs": raw_segments[i+1]["startMs"],
                    "endMs": raw_segments[i+1]["endMs"],
                }
                i += 2
            else:
                i += 1

            exchanges.append({
                "exchangeId": exchange_id,
                "question": question,
                "answer": answer
            })
            exchange_id += 1
        else:
            i += 1

    if len(exchanges) == 0:
        warning_msg("No exchanges found after processing", session_id)

    # Steg 5: Bygg komplett utdata
    output_data = {
        "status": "success",
        "sessionId": session_id,
        "eventType": "transcript_final",
        "language": LANGUAGE,
        "exchanges": exchanges
    }

    # Steg 6: Spara JSON
    base = os.path.splitext(os.path.basename(AUDIO_FILE))[0]
    json_path = os.path.join(OUTPUT_DIR, f"{base}.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # Steg 7: Skicka till Firebase och skriv ut
    if exchanges:
        first = exchanges[0]
        fb_logger.sync_conversation_start({
            "segments": [
                {"text": first["question"]["text"]},
                {"text": first["answer"]["text"] if first["answer"] else ""}
            ]
        })

    print(json.dumps(output_data, ensure_ascii=False))
    print(f"\n  Saved: {json_path}", file=sys.stderr)
    print(f"  Session ID: {session_id}", file=sys.stderr)
    print(f"  Exchanges: {len(exchanges)}", file=sys.stderr)

except Exception as e:
    error_exit("An unexpected error occurred", traceback.format_exc(), session_id)