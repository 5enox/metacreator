from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import re
import os
import uuid
import subprocess
import pathlib
import wget


# def get_tiktok_video_download_url(video_url: str) -> str:
#     """
#     Extracts the download URL from a TikTok video URL.

#     Args:
#     - video_url (str): TikTok video URL.

#     Returns:
#     - str: Download URL for the video.
#     """
#     try:
#         # Extract video ID from TikTok video URL
#         match = re.search(r'/(\d+)$', video_url)
#         if not match:
#             raise ValueError("Invalid TikTok video URL format")

#         video_id = match.group(1)
#         download_url = f"https://tikcdn.io/ssstik/{video_id}"

#         # Return the final download URL
#         return download_url

#     except ValueError as e:
#         print(f"Error extracting download URL: {e}")
#         return ""


# def download_file(url: str) -> str:
#     """
#     Downloads a file from the given URL and saves it.

#     Args:
#     - url (str): URL of the file to download.

#     Returns:
#     - str: Absolute path of the downloaded file.
#     """
#     output_directory = "videos"
#     pathlib.Path(output_directory).mkdir(parents=True, exist_ok=True)

#     try:
#         filename = str(uuid.uuid4()) + ".mp4"
#         video_path = os.path.join(output_directory, filename)

#         # Download the file and save it to the specified directory
#         wget.download(url, out=video_path)

#         # Return the full path of the downloaded file
#         return os.path.abspath(video_path)

#     except Exception as e:
#         print(f"Failed to download video from {url}: {e}")
#         return ""


def remove_metadata(video_path: str) -> bool:
    """
    Removes metadata from a video file using ffmpeg.

    Args:
    - video_path (str): Path to the video file.

    Returns:
    - bool: True if metadata removal was successful, False otherwise.
    """
    parser = createParser(video_path)
    metadata = extractMetadata(parser)

    if metadata is not None:
        for line in metadata.exportPlaintext():
            if line.startswith("Metadata:"):
                os.system(
                    f"exiftool -{line.split(':')[1].split(' ')[1]}={line.split(':')[1].split(' ')[2]}")
                return True
    return True


res = remove_metadata(
    r'C:\Users\5enox\Desktop\CODE\upwork\tiktok_downloader\videos\53ebd00d-f8f1-4125-afd1-f40ae531f36a.mp4')

print(res)
