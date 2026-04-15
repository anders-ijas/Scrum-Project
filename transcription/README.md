# Audio Transcription with Speaker Diarization

Transcribe audio files with automatic speaker identification using Whisper, WhisperX, and Pyannote.

This is a module within the larger project. It handles audio transcription and speaker diarization independently.

**Features:**
- High-quality transcription (Whisper large-v3-turbo model)
- Automatic speaker identification (diarization)
- Word-level alignment
- Multiple output formats: JSON, TXT, SRT

**Output formats:**
- **JSON**: Full segment data with timings and speaker labels
- **TXT**: Human-readable format with speaker labels
- **SRT**: Subtitle format (compatible with video players)

## Prerequisites

- **Python 3.12** (required; does not work with Python 3.14)
- CPU or CUDA capable GPU (optional, but recommended)

## Setup

### 1. Create virtual environment

From the module directory:

```bash
python3.12 -m venv venv
```

**Activate virtual environment:**

**Linux/WSL/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

These packages will be installed:
```
whisperx==3.8.5
python-dotenv==1.0.0
torch==2.8.0
torchaudio==2.8.0
```

### 3. Get Hugging Face token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read access is enough)
3. Copy the token

### 4. Configure environment

Create a `.env` file in the `whisper_transcription/` directory:

```
HF_TOKEN=hf_your_actual_token_here
```

**Note:** The `.env` file is in `.gitignore` and should never be committed.

## Usage

From the project root:

```bash
python whisper_transcription/transcribe.py <audio_file>
```

**Examples:**
```bash
python whisper_transcription/transcribe.py meeting.mp3
python whisper_transcription/transcribe.py lectures/lecture_01.wav
```

**Supported formats:** MP3

### Output

Files are saved in `whisper_transcription/output/`:
- `filename.json` - Full transcription data
- `filename.txt` - Readable text format
- `filename.srt` - Subtitle format

**Example output (TXT):**
```
[SPEAKER_00]: Hello, how are you?
[SPEAKER_01]: I'm doing great, thanks for asking.
[SPEAKER_00]: That's wonderful to hear.
```

## Configuration

Edit the top of `transcribe.py` to adjust:

```python
LANGUAGE = "en"           # Language code: "en", "sv", "fr", etc.
DEVICE = "cpu"            # "cuda" for GPU, "cpu" for CPU
COMPUTE_TYPE = "int8"     # "int8", "float16", "float32"
```

### Performance notes:

- For **CPUs**: `int8` is faster but slightly less accurate
- For **GPUs**: Use `float16` or `float32` for better quality
- Models are automatically downloaded on first run (~3-5 GB)

## Troubleshooting

### "HF_TOKEN not found"
- Make sure `.env` file exists in the `whisper_transcription/` directory
- Verify the token is correctly set
- Make sure `python-dotenv` is installed

### Out of memory errors
- Switch to `DEVICE = "cpu"`
- Or reduce `COMPUTE_TYPE` to `"int8"`

### Diarization fails
- Ensure you have proper HF_TOKEN set
- Check internet connection for model download

### Audio won't load
- Try converting to MP3 or WAV format
- Check file isn't corrupted
