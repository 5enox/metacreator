from abc import ABC, abstractmethod
import os
import re
import requests
import uuid
import wget
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import subprocess
import pathlib
from typing import Optional


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

    def remove_metadata(self, video_path: str) -> bool:
        """
        Removes metadata from a video file using ffmpeg.

        Args:
        - video_path (str): Path to the video file.

        Returns:
        - bool: True if metadata removal was successful, False otherwise.
        """
        try:
            parser = createParser(video_path)
            metadata = extractMetadata(parser)

            if metadata is not None:
                for line in metadata.exportPlaintext():
                    if line.startswith("Metadata:"):
                        os.system(
                            f"exiftool -{line.split(':')[1].split(' ')[1]}={line.split(':')[1].split(' ')[2]}")
                        return True
            return True
        except Exception as e:
            print(f"Failed to remove metadata: {e}")
            return False


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
