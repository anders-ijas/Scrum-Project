import os
import json
import sys
import gc
import uuid
from dotenv import load_dotenv
import whisperx
from whisperx.diarize import DiarizationPipeline

# Load environment variables
load_dotenv()

# Config
HF_TOKEN = os.getenv("HF_TOKEN")
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

DEVICE       = "cuda"      # or "cpu"
COMPUTE_TYPE = "float16"   # or "int8" for CPU
BATCH_SIZE   = 16          # Adjust based on GPU memory

# Load audio
print("Loading audio...")
audio = whisperx.load_audio(AUDIO_FILE)
audio_duration = len(audio) / 16000
if audio_duration < 10:
    print(f"Warning: short audio ({audio_duration:.2f}s) diarization may be inaccurate.")

# 1. Transcribe
print("Loading Whisper model...")
model = whisperx.load_model("large-v3-turbo", DEVICE, compute_type=COMPUTE_TYPE)
print("Transcribing...")
result = model.transcribe(audio, language=LANGUAGE, batch_size=BATCH_SIZE)

gc.collect()
del model

# 2. Align (improves word timestamps)
print("Aligning...")
model_a, metadata = whisperx.load_align_model(
    language_code=result["language"],
    device=DEVICE,
    model_name="WAV2VEC2_ASR_LARGE_LV60K_960H"
)
result = whisperx.align(
    result["segments"], model_a, metadata, audio, DEVICE, return_char_alignments=False
)

gc.collect()
del model_a

# 3. Diarize (identify speakers)
print("Diarizing...")
diarize_model = DiarizationPipeline(
    model_name="pyannote/speaker-diarization-community-1",
    token=HF_TOKEN,
    device=DEVICE,
)
diarize_segments = diarize_model(audio, min_speakers=2, max_speakers=2)
result = whisperx.assign_word_speakers(diarize_segments, result)

# 4. Map speakers to friendly names
speaker_map = {}
speaker_index = 0
speaker_names = ["vuxen", "barn", "okänd_1", "okänd_2"]

for seg in result["segments"]:
    for word in seg.get("words", []):
        speaker = word.get("speaker", "UNKNOWN")
        if speaker not in speaker_map:
            if speaker_index < len(speaker_names):
                speaker_map[speaker] = speaker_names[speaker_index]
            else:
                speaker_map[speaker] = f"okänd_{speaker_index}"
            speaker_index += 1

# 5. Build transcript (sentence level)
transcript = []
for seg in result["segments"]:
    if not seg.get("words"):
        continue
    
    speaker_raw = seg["words"][0].get("speaker", "UNKNOWN")
    speaker_name = speaker_map.get(speaker_raw, speaker_raw)
    
    sentence_text = " ".join([w["word"] for w in seg["words"]])
    start_time = seg["words"][0]["start"]
    end_time = seg["words"][-1]["end"]
    
    transcript.append({
        "speaker": speaker_name,
        "text": sentence_text.strip(),
        "start": round(start_time, 3),
        "end": round(end_time, 3),
        "duration": round(end_time - start_time, 3)
    })

# 6. Build complete output
# SESSION_ID sätts av den som startar sessionen (inte här).
# Samma ID används av emotion och alignment. Fallback endast för testning.
session_id = os.getenv("SESSION_ID", str(uuid.uuid4()))

segments = []
for i, seg in enumerate(transcript):
    segments.append({
        "segmentId": f"seg_{i+1:03}",
        "speakerLabel": next((k for k, v in speaker_map.items() if v == seg["speaker"]), "UNKNOWN"),
        "role": seg["speaker"],
        "text": seg["text"],
        "startMs": round(seg["start"] * 1000),
        "endMs": round(seg["end"] * 1000),
        "durationMs": round(seg["duration"] * 1000)
    })

output_data = {
    "sessionId": session_id,
    "eventType": "transcript_final",
    "language": LANGUAGE,
    "durationMs": round(audio_duration * 1000),
    "speakers": {
        label: {"role": role}
        for label, role in speaker_map.items()
    },
    "segments": segments
}

# 7. Save JSON output
base = os.path.splitext(os.path.basename(AUDIO_FILE))[0]
json_path = os.path.join(OUTPUT_DIR, f"{base}.json")

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\n  Saved: {json_path}")
print(f"    Session: {output_data['sessionId']}")
print(f"    Duration: {output_data['durationMs']}ms")
print(f"    Segments: {len(segments)}")
print(f"    Speakers: {list(speaker_map.values())}")