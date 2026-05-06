# Audio Transcription

Transcribe audio files and structure conversations as question/answer exchanges using Whisper and WhisperX.

This is a module within the larger project. It handles audio transcription and conversation structuring independently.

**Features:**
- High-quality transcription (Whisper large-v3-turbo model)
- Word-level alignment
- Automatic question/answer exchange detection

**Output format:**
- **JSON**: Transcription structured as exchanges with timestamps

## Prerequisites

- **Python 3.12** (required; does not work with Python 3.14)
- **FFmpeg 7.x** (required for audio processing)
- CPU or CUDA capable GPU (optional, but recommended)

## Setup

### 1. Install FFmpeg

**Windows (using winget):**
```bash
winget install "FFmpeg (Essentials Build)" --version 7.1
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
py -3.12 -m venv venv
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

### 4. Get Hugging Face token

Required for the word-level alignment model.

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

Place audio files in the `transcription/input/` folder, then run:

```bash
python transcribe.py <audio_filename>
```

**Examples:**
```bash
python transcribe.py meeting.mp3
python transcribe.py lecture.wav
```

**Supported formats:** MP3, WAV

### Output

Files are saved in `transcription/output/`:
- `filename.json` - Transcription structured as exchanges

### How it works

The script classifies each segment based on content:
- Segments ending with `?` → question → vuxen
- Segment following a question → answer → barn
- Everything else → statement → vuxen

Questions and answers are grouped into exchanges for easy alignment with emotion data.

### Performance notes

- For **CPUs**: `int8` is faster but slightly less accurate
- For **GPUs**: Use `float16` or `float32` for better quality
- Models are automatically downloaded on first run (~1-2 GB)

## Troubleshooting

### "FFmpeg not found" or "FileNotFoundError"
- FFmpeg is not installed or not in your PATH
- Make sure you installed FFmpeg 7.x (not 8.x)
- Restart your terminal after installing

### "HF_TOKEN not found"
- Make sure `.env` file exists in the `transcription/` directory
- Verify the token is correctly set

### Audio won't load
- Try converting to MP3 or WAV format
- Check file isn't corrupted
- Make sure the file is placed in the `input/` folder