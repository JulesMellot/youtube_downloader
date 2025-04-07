import os
import subprocess
import shutil
from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
import requests

def check_internet_connection():
    """Check internet connection"""
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.RequestException:
        return False

def merge_video_audio(video_path, audio_path, output_path, subtitle_path=None):
    """Merge video and audio, and add subtitles if available"""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if subtitle_path:
        # If subtitles are available, integrate them into the video file
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-i', subtitle_path,
            '-c:v', 'copy',  # Copy video without recoding
            '-c:a', 'aac',
            '-b:a', '320k',  # High quality audio
            '-c:s', 'mov_text',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-map', '2:s:0',
            output_path
        ]
    else:
        # Without subtitles, do a simple merge
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',  # Copy video without recoding
            '-c:a', 'aac',
            '-b:a', '320k',  # High quality audio
            output_path
        ]
    
    try:
        print("Merging files...")
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during merge: {e}")
        return False

def download_video(url, output_dir="downloads"):
    """Download a YouTube video with the best available quality"""
    if not check_internet_connection():
        print("Error: No Internet connection")
        return False

    # Create necessary directories
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Connect to YouTube
        print("Connecting to YouTube...")
        yt = YouTube(url, on_progress_callback=on_progress)
        print(f"Title: {yt.title}")

        # Download video in best H.264 quality
        print("\nDownloading video...")
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not video_stream:
            print("Error: Unable to find a valid video stream")
            return False

        print(f"Selected video quality: {video_stream.resolution}")
        video_path = video_stream.download(output_path=temp_dir)

        # Download audio in best quality
        print("\nDownloading audio...")
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        if not audio_stream:
            print("Error: Unable to find a valid audio stream")
            return False

        print(f"Selected audio quality: {audio_stream.abr}kbps")
        audio_path = audio_stream.download(output_path=temp_dir)

        # Download subtitles if available
        subtitle_path = None
        try:
            captions = yt.captions
            if captions:
                # Try French subtitles first
                subtitle = captions.get('fr') or captions.get('fr-FR')
                if not subtitle:
                    # If no French, take the first available subtitle
                    subtitle = next(iter(captions.values()))
                
                if subtitle:
                    print("\nDownloading subtitles...")
                    subtitle_path = subtitle.download(title=yt.title, output_path=temp_dir)
                    print("Subtitles downloaded successfully")
        except Exception as e:
            print(f"Note: Unable to download subtitles ({e})")

        # Create file paths
        temp_output = os.path.join(temp_dir, f"{yt.title}.mp4")
        final_path = os.path.join(output_dir, f"{yt.title}.mp4")
        
        # Merge video, audio and subtitles
        print("\nMerging files...")
        if merge_video_audio(video_path, audio_path, temp_output, subtitle_path):
            print("Merge successful!")
            
            # Copy final file to downloads folder
            print("Copying final file...")
            shutil.copy2(temp_output, final_path)
            print(f"Final file copied: {final_path}")
            
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir)
                print("Temporary directory deleted")
            except Exception as e:
                print(f"Note: Unable to delete temporary directory ({e})")
            
            return True
        else:
            print("Merge failed, temporary files are kept in 'temp' folder")
            return False

    except Exception as e:
        print(f"Erreur : {e}")
        return False

def download_playlist(url, output_dir="downloads"):
    """Download all videos from a YouTube playlist"""
    if not check_internet_connection():
        print("Error: No Internet connection")
        return False

    try:
        # Create download directory
        os.makedirs(output_dir, exist_ok=True)

        # Get playlist
        print("Retrieving playlist...")
        playlist = Playlist(url)
        print(f"Playlist title: {playlist.title}")
        print(f"Number of videos: {len(playlist.video_urls)}")

        # Download each video
        for i, video_url in enumerate(playlist.video_urls, 1):
            print(f"\nDownloading video {i}/{len(playlist.video_urls)}")
            video = YouTube(video_url)
            output_path = os.path.join(output_dir, f"{video.title}.mp4")
            download_video(video_url, output_dir)

        return True

    except Exception as e:
        print(f"Erreur : {e}")
        return False

def main():
    print("=== YouTube Downloader ===")
    print("1. Download a video")
    print("2. Download a playlist")
    
    choice = input("\nChoice (1 or 2): ")
    url = input("YouTube URL: ")
    
    if choice == "1":
        if download_video(url):
            print("\nDownload completed successfully!")
        else:
            print("\nDownload failed.")
    elif choice == "2":
        if download_playlist(url):
            print("\nPlaylist download completed successfully!")
        else:
            print("\nPlaylist download failed.")
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()