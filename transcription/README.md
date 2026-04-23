# Audio Transcription with Speaker Diarization

Transcribe audio files with automatic speaker identification using Whisper, WhisperX, and Pyannote.

This is a module within the larger project. It handles audio transcription and speaker diarization independently.

**Features:**
- High-quality transcription (Whisper large-v3-turbo model)
- Automatic speaker identification (diarization)
- Word-level alignment

**Output format:**
- **JSON**: Complete transcription with word-level timestamps and speaker labels

## Prerequisites

- **Python 3.12** (required; does not work with Python 3.14)
- **FFmpeg** (required for audio processing)
- CPU or CUDA capable GPU (optional, but recommended)

## Setup

### 1. Install FFmpeg

**Windows (using winget):**
```bash
winget install FFmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Verify FFmpeg installation:**
```bash
ffmpeg -version
```

### 2. Create virtual environment

From the `transcription/` directory:

```bash
python -m venv venv
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

### 3. Install dependencies

The project includes three requirements files for different hardware setups:

| File | Purpose |
|------|---------|
| `requirements_common.txt` | Base dependencies (whisperx, python-dotenv) |
| `requirements_cpu.txt` | PyTorch for CPU (works on any computer) |
| `requirements_gpu.txt` | PyTorch for NVIDIA GPU with CUDA 12.6 |

**Choose your hardware (install in this order):**

**For CPU (works on any computer):**
```bash
pip install -r requirements_cpu.txt
pip install -r requirements_common.txt
```

**For GPU (NVIDIA, faster):**
```bash
pip install -r requirements_gpu.txt
pip install -r requirements_common.txt
```

The script automatically detects and uses GPU if available, otherwise falls back to CPU.

### 4. Get Hugging Face token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read access is enough)
3. Copy the token

### 5. Configure environment

Create a `.env` file in the `transcription/` directory:

```
HF_TOKEN=hf_your_actual_token_here
```

**Note:** The `.env` file is in `.gitignore` and should never be committed.

## Usage
```bash
python transcribe.py <audio_file>
```

**Examples:**
```bash
python transcribe.py meeting.mp3
python transcribe.py lectures/lecture_01.wav
```

**Supported formats:** MP3, WAV

### Output

Files are saved in `transcription/output/`:
- `filename.json` - Full transcription data

### Configuration

The script automatically handles device detection and speaker role assignment. No manual configuration needed.

### Automatic features:
- GPU/CPU detection: Automatically uses CUDA if available, otherwise CPU
- Adult speaker identification: Based on the first question in the conversation
- Speaker role assignment: All segments from the adult speaker → "vuxen", others → "barn"
- Segment classification: Question (ends with ?), Answer (short, ≤4 words), Statement (longer)

### Performance notes:

- For **CPUs**: `int8` is faster but slightly less accurate
- For **GPUs**: Use `float16` or `float32` for better quality
- Models are automatically downloaded on first run (~3-5 GB)

## Troubleshooting

### "FFmpeg not found" or "FileNotFoundError"
- FFmpeg is not installed or not in your PATH
- Follow the FFmpeg installation instructions above
- Restart your terminal after installing

### "HF_TOKEN not found"
- Make sure `.env` file exists in the `transcription/` directory
- Verify the token is correctly set
- Make sure `python-dotenv` is installed

### Diarization fails
- Ensure you have proper HF_TOKEN set
- Check internet connection for model download

### Audio won't load
- Try converting to MP3 or WAV format
- Check file isn't corrupted
