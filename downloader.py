import re
import os
import uuid
import subprocess
import pathlib
import wget


def get_tiktok_video_download_url(video_url: str) -> str:
    """
    Extracts the download URL from a TikTok video URL.

    Args:
    - video_url (str): TikTok video URL.

    Returns:
    - str: Download URL for the video.
    """
    try:
        # Extract video ID from TikTok video URL
        match = re.search(r'/(\d+)$', video_url)
        if not match:
            raise ValueError("Invalid TikTok video URL format")

        video_id = match.group(1)
        download_url = f"https://tikcdn.io/ssstik/{video_id}"

        # Return the final download URL
        return download_url

    except ValueError as e:
        print(f"Error extracting download URL: {e}")
        return ""


def download_file(url: str) -> str:
    """
    Downloads a file from the given URL and saves it.

    Args:
    - url (str): URL of the file to download.

    Returns:
    - str: Absolute path of the downloaded file.
    """
    output_directory = "videos"
    pathlib.Path(output_directory).mkdir(parents=True, exist_ok=True)

    try:
        filename = str(uuid.uuid4()) + ".mp4"
        video_path = os.path.join(output_directory, filename)

        # Download the file and save it to the specified directory
        wget.download(url, out=video_path)

        # Return the full path of the downloaded file
        return os.path.abspath(video_path)

    except Exception as e:
        print(f"Failed to download video from {url}: {e}")
        return ""


def remove_metadata(video_path: str) -> bool:
    """
    Removes metadata from a video file using ffmpeg.

    Args:
    - video_path (str): Path to the video file.

    Returns:
    - bool: True if metadata removal was successful, False otherwise.
    """
    try:
        # Command to run with ffmpeg to strip metadata
        command = [r"C:\ffmpeg\bin\ffmpeg.exe", "-i", str(video_path), "-map_metadata",
                   "-1", "-c:v", "copy", "-c:a", "copy", str(video_path)]

        # Run the command synchronously
        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)

        # Check the result
        if result.returncode != 0:
            print(f"Error occurred: {result.stderr}")
            return False
        else:
            print("Metadata removed successfully")
            return True

    except Exception as e:
        print(f"Failed to remove metadata from {video_path}: {e}")
        return False
