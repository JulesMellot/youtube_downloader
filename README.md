# YouTube Downloader

This Python script allows you to download YouTube videos and playlists in maximum quality by separately downloading video and audio for better quality. It also includes support for embedded subtitles.

## Prerequisites

1. Python 3.6 or higher
2. ffmpeg (for audio/video merging and subtitle integration)
   - On macOS: `brew install ffmpeg`
   - On Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:
```bash
python youtube_downloader.py
```

2. Choose the desired option:
   - 1: To download a single video
   - 2: To download a complete playlist

3. Enter the YouTube URL of the video or playlist

Videos will be downloaded to a `downloads` folder that will be created automatically.

## Features

- Download videos in maximum quality
  - Video in best available resolution
  - Audio in best available quality
  - Automatic merging with ffmpeg
- Embedded subtitles support
  - Automatic download of available subtitles
  - Priority to French subtitles
  - Integration into the video file (VLC compatible)
- Complete playlist downloading
- Preservation of original video titles
- Real-time progress bar
- Error handling
- Simple command-line interface

## Notes

- The script uses pytubefix, a fixed and maintained version of pytube
- Videos are downloaded in MP4 format
- Audio/video merging is done without quality loss
- Subtitles are embedded in the video file and can be enabled/disabled in VLC
- Temporary files are automatically deleted after merging