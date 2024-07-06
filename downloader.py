import os
import re
import hashlib
import uuid
import pathlib
import subprocess
import tempfile
from typing import Union, Optional

import requests
import wget
import ffmpeg
from moviepy.editor import VideoFileClip
from moviepy.video.fx.colorx import colorx
from abc import ABC, abstractmethod


class VideoDownloader(ABC):
    class VideoDownloader(ABC):
        @abstractmethod
        def get_download_url(self, video_url: str) -> Optional[str]:
            pass
        pass

    def download_file(self, url: str) -> Optional[list]:
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
            return [os.path.abspath(video_path), filename]
        except Exception as e:
            print(f"Failed to download video from {url}: {e}")
            return None

    def adjust(self, video_path: str, saturation: float) -> Union[bool, None]:
        try:
            # Check if ffmpeg is installed
            try:
                subprocess.run(["ffmpeg", "-version"],
                               check=True, capture_output=True)
            except FileNotFoundError:
                raise RuntimeError(
                    "ffmpeg is not installed or not found in the system path.")

            # Step 1: Clean Metadata
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix='.mp4').name
            ffmpeg_cmd = (
                ffmpeg
                .input(video_path)
                .output(temp_file, map_metadata=-1, c='copy')
            )
            ffmpeg_cmd.run(quiet=True, overwrite_output=True)
            print(f"Metadata cleaned and saved to: {temp_file}")

            # Step 2: Change MD5 Hash (by modifying the video content slightly, here we add 5% saturation)
            clip = VideoFileClip(temp_file)
            new_clip = clip.fx(colorx, saturation)
            final_temp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix='.mp4').name
            new_clip.write_videofile(final_temp_file)
            print(f"Video with increased saturation saved to: {
                  final_temp_file}")

            # Step 3: Compute and change MD5 hash
            with open(final_temp_file, 'rb') as f:
                file_content = f.read()
                md5_hash = hashlib.md5(file_content).hexdigest()
                print(f"MD5 Hash of the modified video: {md5_hash}")

            # Get original file name without extension
            original_filename = os.path.splitext(
                os.path.basename(video_path))[0]

            # Rename the modified file to include the original file's name
            new_path = f"videos/{original_filename}.mp4"
            os.remove(video_path)
            os.rename(final_temp_file, new_path)
            print(f"Final video saved to: {new_path}")

            # Clean up temporary files
            os.remove(temp_file)

            # Delete the original video file

            print(f"Deleted original video: {video_path}")

            return True

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
