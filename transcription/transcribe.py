import os
import json
import sys
from dotenv import load_dotenv
import whisperx
from whisperx.diarize import DiarizationPipeline

# Load environment variables
load_dotenv()

# Config
HF_TOKEN   = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    print("Error: HF_TOKEN not found in .env file")
    sys.exit(1)

LANGUAGE   = "sv"
OUTPUT_DIR = "output"

if len(sys.argv) < 2:
    print("Usage: python transcribe.py <audio_file.mp3>")
    sys.exit(1)

AUDIO_FILE = sys.argv[1]
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Device
DEVICE       = "cpu"
COMPUTE_TYPE = "int8"

# Load audio
audio = whisperx.load_audio(AUDIO_FILE)

# 1. Transcribe
print("Loading Whisper model...")
model = whisperx.load_model("large-v3-turbo", DEVICE, compute_type=COMPUTE_TYPE)
print("Transcribing...")
result = model.transcribe(audio, language=LANGUAGE, batch_size=16)

# 2. Align
print("Aligning...")
align_model, metadata = whisperx.load_align_model(
    language_code=LANGUAGE,
    device=DEVICE,
    model_name="WAV2VEC2_ASR_LARGE_LV60K_960H"
)
result = whisperx.align(
    result["segments"], align_model, metadata, audio, DEVICE
)

# 3. Diarize
print("Diarizing...")
diarize_model = DiarizationPipeline(
    model_name="pyannote/speaker-diarization-community-1",
    token=HF_TOKEN,
    device=DEVICE,
)
diarize_segments = diarize_model(audio, min_speakers=2, max_speakers=2)
result = whisperx.assign_word_speakers(diarize_segments, result)

# 4. Split segments at speaker-change boundaries
def split_on_speaker_change(segments):
    out = []
    for seg in segments:
        words = seg.get("words", [])
        if not words:
            out.append(seg)
            continue
        buf, spk, start = [], words[0].get("speaker", "UNKNOWN"), seg["start"]
        for w in words:
            s = w.get("speaker", spk)
            if s != spk:
                out.append({"speaker": spk, "text": " ".join(x["word"] for x in buf), "start": start, "end": buf[-1].get("end", seg["end"])})
                buf, spk, start = [], s, w.get("start", start)
            buf.append(w)
        if buf:
            out.append({"speaker": spk, "text": " ".join(x["word"] for x in buf), "start": start, "end": seg["end"]})
    return out

# Merge segments that are too short (likely misattributed)
def merge_short_segments(segments, min_duration=0.5):
    """Merge segments shorter than min_duration with adjacent segment of same speaker."""
    if not segments:
        return segments
    
    merged = [segments[0]]
    for seg in segments[1:]:
        duration = seg["end"] - seg["start"]
        # If current segment is too short and same speaker as previous, merge
        if duration < min_duration and seg.get("speaker") == merged[-1].get("speaker"):
            merged[-1]["text"] += " " + seg["text"]
            merged[-1]["end"] = seg["end"]
        else:
            merged.append(seg)
    
    return merged

final_segments = split_on_speaker_change(result["segments"])
final_segments = merge_short_segments(final_segments, min_duration=0.5)

# 5. Write outputs
base = os.path.splitext(os.path.basename(AUDIO_FILE))[0]

# JSON (save original full result + final_segments)
json_path = os.path.join(OUTPUT_DIR, f"{base}.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump({"segments": final_segments}, f, ensure_ascii=False, indent=2)
print(f"Saved: {json_path}")

# TXT
txt_path = os.path.join(OUTPUT_DIR, f"{base}.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    for seg in final_segments:
        speaker = seg.get("speaker", "UNKNOWN")
        text    = seg["text"].strip()
        f.write(f"[{speaker}]: {text}\n")
        print(f"[{speaker}]: {text}")
print(f"Saved: {txt_path}")

# SRT
def fmt_time(seconds: float) -> str:
    h  = int(seconds // 3600)
    m  = int((seconds % 3600) // 60)
    s  = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

srt_path = os.path.join(OUTPUT_DIR, f"{base}.srt")
with open(srt_path, "w", encoding="utf-8") as f:
    for i, seg in enumerate(final_segments, start=1):
        speaker = seg.get("speaker", "UNKNOWN")
        text    = seg["text"].strip()
        start   = fmt_time(seg["start"])
        end     = fmt_time(seg["end"])
        f.write(f"{i}\n{start} --> {end}\n[{speaker}]: {text}\n\n")
print(f"Saved: {srt_path}")