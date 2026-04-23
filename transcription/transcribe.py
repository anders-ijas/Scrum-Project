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
from whisperx.diarize import DiarizationPipeline

warnings.filterwarnings("ignore", category=UserWarning, module="pyannote.audio.core.io")

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

AUDIO_FILE = sys.argv[1]

if not os.path.exists(AUDIO_FILE):
    error_exit(f"Audio file not found: {AUDIO_FILE}", session_id=session_id)

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
        warning_msg(f"Audio duration is very short: {audio_duration:.2f} seconds - diarization may be inaccurate.", session_id)

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

    # Steg 3: Diarize (bestäm vem som talar när)
    print("Diarizing...", file=sys.stderr)
    try:
        diarize_model = DiarizationPipeline(
            model_name="pyannote/speaker-diarization-community-1",
            token=HF_TOKEN,
            device=DEVICE,
        )
        diarize_segments = diarize_model(audio, min_speakers=2, max_speakers=2)
        result = whisperx.assign_word_speakers(diarize_segments, result)
        print("AI diarization completed", file=sys.stderr)
    except Exception as e:
        warning_msg(f"Diarization failed: {str(e)}", session_id)

    # Steg 4: ge talarna läsbara namn (vuxen, barn, okänd) baserat på diarization och textinnehåll
    speaker_map = {}
    speaker_index = 0
    speaker_names = ["vuxen", "barn", "okänd_1", "okänd_2"]

    for seg in result["segments"]:
        for word in seg.get("words", []):
            speaker = word.get("speaker", "UNKNOWN")
            if speaker not in speaker_map and speaker != "UNKNOWN":
                if speaker_index < len(speaker_names):
                    speaker_map[speaker] = speaker_names[speaker_index]
                else:
                    speaker_map[speaker] = f"okänd_{speaker_index}"
                speaker_index += 1

    # Steg 4.5: Korrigera - svar ska inte komma från samma talare som frågan
    correction_count = 0
    for i in range(1, len(result["segments"])):
        prev = result["segments"][i-1]
        curr = result["segments"][i]
        
        if not prev.get("words") or not curr.get("words"):
            continue
        
        prev_text = " ".join([w["word"] for w in prev["words"]])
        prev_spk = prev["words"][0].get("speaker", "UNKNOWN")
        curr_spk = curr["words"][0].get("speaker", "UNKNOWN")
        
        if prev_text.strip().endswith("?") and prev_spk == curr_spk:
            # Byt till den andra talaren
            other = None
            for s in result["segments"]:
                if s.get("words"):
                    sp = s["words"][0].get("speaker", "UNKNOWN")
                    if sp != "UNKNOWN" and sp != prev_spk:
                        other = sp
                        break
            if other:
                for w in curr.get("words", []):
                    w["speaker"] = other
                correction_count += 1
    
    if correction_count:
        print(f"Fixed {correction_count} answers from same speaker as question", file=sys.stderr)

    # Steg 4.6: Vem är vuxen? (första frågan avgör)
    adult = None
    for seg in result["segments"]:
        if seg.get("words"):
            text = " ".join([w["word"] for w in seg["words"]])
            if text.strip().endswith("?"):
                adult = seg["words"][0].get("speaker", "UNKNOWN")
                print(f"Adult: {adult}", file=sys.stderr)
                break

    # Steg 5: Bygg transcript
    transcript = []
    vuxen_ord = {"jaha", "okej", "mm", "ja", "nej", "jo", "jaså", "förstår", "precis", "absolut", "bra", "okej då", "men om", "finns det"}
    barn_ord = {"typ", "liksom", "ba", "asså", "kanske", "nja", "va", "vadå", "eh", "öhm", "jag vet inte", "vet inte"}
    
    for seg in result.get("segments", []):
        if not seg.get("words"):
            continue
        
        spk = seg["words"][0].get("speaker", "UNKNOWN")
        text = " ".join([w["word"] for w in seg["words"]]).strip()
        lower = text.lower()
        words = len(text.split())
        
        if adult:
            # Använd första frågan för att bestämma roll
            role = "vuxen" if spk == adult else "barn"
            seg_type = "question" if text.endswith("?") else ("answer" if words <= 4 else "statement")
        else:
            # Fallback
            if text.endswith("?"):
                role, seg_type = "vuxen", "question"
            elif any(w in lower for w in vuxen_ord):
                role, seg_type = "vuxen", "answer"
            elif any(w in lower for w in barn_ord) or words <= 4:
                role, seg_type = "barn", "answer"
            else:
                role, seg_type = "vuxen", "statement"
        
        transcript.append({
            "speaker": role,
            "text": text,
            "type": seg_type,
            "start": round(seg["words"][0]["start"], 3),
            "end": round(seg["words"][-1]["end"], 3),
            "duration": round(seg["words"][-1]["end"] - seg["words"][0]["start"], 3)
        })
        
    if len(transcript) == 0:
        warning_msg("No transcribed segments found after processing", session_id)

    # Steg 6: Formattera segmenten i det önskade JSON-formatet
    segments = []
    for i, seg in enumerate(transcript):
        speaker_label = "UNKNOWN"
        for label, role in speaker_map.items():
            if role == seg["speaker"]:
                speaker_label = label
                break
        segments.append({
            "segmentId": f"seg_{i+1:03d}",
            "speakerLabel": speaker_label,
            "role": seg["speaker"],
            "text": seg["text"],
            "startMs": round(seg["start"] * 1000),
            "endMs": round(seg["end"] * 1000),
            "durationMs": round(seg["duration"] * 1000)
        })

    # Steg 7: Bygg komplett utdata
    output_data = {
        "status": "success",
        "sessionId": session_id,
        "eventType": "transcript_final",
        "language": LANGUAGE,
        "durationMs": round(audio_duration * 1000),
        "speakers": {label: {"role": role} for label, role in speaker_map.items()},
        "segments": segments
    }

    # Steg 8: Spara utdata som JSON-fil
    base = os.path.splitext(os.path.basename(AUDIO_FILE))[0]
    json_path = os.path.join(OUTPUT_DIR, f"{base}.json")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # Steg 9: Skriv ut resultatet i JSON-format till stdout och logga viktig info till stderr
    print(json.dumps(output_data, ensure_ascii=False))
    print(f"\n  Saved: {json_path}", file=sys.stderr)
    print(f"  Session ID: {session_id}", file=sys.stderr)
    print(f"  Duration: {audio_duration:.2f} seconds", file=sys.stderr)
    print(f"  Segments: {len(segments)}", file=sys.stderr)
    print(f"  Speakers: {list(speaker_map.values()) if speaker_map else 'None'}", file=sys.stderr)

except Exception as e:
    error_exit("An unexpected error occurred", traceback.format_exc(), session_id)