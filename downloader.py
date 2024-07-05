import os
import re
import hashlib
import uuid
import tempfile
import pathlib

from abc import ABC, abstractmethod
from typing import Union, Optional

import requests
import wget
import ffmpeg
from moviepy.editor import VideoFileClip
from moviepy.video.fx import colorx


class VideoDownloader(ABC):

    @abstractmethod
    def get_download_url(self, video_url: str) -> Optional[str]:
        pass

    def download_file(self, url: str) -> Optional[str]:
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
            return None

    def adjust(self, video_path: str) -> Union[str, None]:
        """
        Removes metadata from a video file using ffmpeg.

        Args:
        - video_path (str): Path to the video file.

        Returns:
        - bool: True if metadata removal was successful, False otherwise.
        """
        try:
            # Create a temporary file to store the intermediate video
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix='.mp4').name

            # Step 1: Clean Metadata
            ffmpeg.input(video_path).output(temp_file, map_metadata=-1,
                                            c='copy').run(quiet=True, overwrite_output=True)

            # Step 2: Change MD5 Hash (by modifying the video content slightly, here we add 5% saturation)
            with VideoFileClip(temp_file) as clip:
                new_clip = clip.fx(colorx, factor=1.05)
                final_temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix='.mp4').name
                new_clip.write_videofile(
                    final_temp_file, codec='libx264', audio_codec='aac', logger=None)

            # Step 3: Compute and change MD5 hash
            with open(final_temp_file, 'rb') as f:
                file_content = f.read()
                md5_hash = hashlib.md5(file_content).hexdigest()

            new_path = f"{os.path.splitext(video_path)[0]}_modified.mp4"
            os.rename(final_temp_file, new_path)

            # Clean up temporary file
            os.remove(temp_file)

            return new_path

        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return None


class TikTokDownloader(VideoDownloader):

    def get_download_url(self, video_url: str) -> Optional[str]:
        """
        Extracts the download URL from a TikTok video URL.

        Args:
        - video_url (str): TikTok video URL.

        Returns:
        - str: Download URL for the video.
        """
        try:
            match = re.search(r'/(\d+)$', video_url)
            if not match:
                raise ValueError("Invalid TikTok video URL format")

            video_id = match.group(1)
            download_url = f"https://tikcdn.io/ssstik/{video_id}"

            return download_url
        except ValueError as e:
            print(f"Error extracting download URL: {e}")
            return None


class InstagramDownloader(VideoDownloader):

    def get_download_url(self, video_url: str) -> Optional[str]:
        """
        Extracts the download URL from an Instagram video URL.

        Args:
        - video_url (str): Instagram video URL.

        Returns:
        - str: Download URL for the video.
        """
        try:
            url = "https://get.reelsdownloader.io/allinone"
            headers = {
                "Url": video_url,
            }

            response = requests.get(url, headers=headers)
            json_data = response.json()

            if "media" in json_data and len(json_data["media"]) > 0:
                return json_data["media"][0]["url"]
            else:
                return None
        except Exception as e:
            print(f"Error extracting download URL: {e}")
            return None
