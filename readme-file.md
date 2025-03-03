# YouTube Transcriber and Keyword Analyzer

A Python tool that transcribes YouTube videos, proofreads the transcript, and analyzes keyword frequency.

## Features

- Extract transcripts from any YouTube video URL
- Proofread and correct the transcript text
- Identify keywords that appear more than a specified number of times
- Output results in text or JSON format
- Save results to a file or display in the console

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/youtube-transcriber.git
   cd youtube-transcriber
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python youtube_transcriber.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Options

- `-m, --min-occurrences`: Minimum number of occurrences for keyword analysis (default: 3)
- `-o, --output`: Output format, either 'text' or 'json' (default: text)
- `-f, --file`: Output file path (default: print to console)

### Examples

Basic usage with default settings:
```bash
python youtube_transcriber.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Specify minimum 5 occurrences for keywords and output in JSON format:
```bash
python youtube_transcriber.py "https://www.youtube.com/watch?v=VIDEO_ID" -m 5 -o json
```

Save results to a file:
```bash
python youtube_transcriber.py "https://www.youtube.com/watch?v=VIDEO_ID" -f results.txt
```

## Requirements

- Python 3.6+
- pytube
- youtube-transcript-api
- language-tool-python

## Known Limitations

- Transcripts are only available for videos that have captions enabled
- The quality of transcription depends on the captions provided by YouTube
- Some videos may have restrictions that prevent accessing their transcripts
- The language-tool-python library requires Java to be installed on your system

## License

This project is licensed under the MIT License - see the LICENSE file for details.
