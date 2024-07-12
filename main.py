from urllib.parse import urlparse, urlunparse
import os
import threading
import time
import urllib.parse as parse

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from downloader import TikTokDownloader, InstagramDownloader
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from boto import construct_download_link


app = FastAPI()

origins = [
    "https://www.phantomclip.com/"  # Replace with your allowed domain
    , "https://phantomclip.com/"
]

# Define the CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_methods=["GET", "POST"],  # Add more HTTP methods as needed
    allow_headers=["*"],  # You can also specify headers explicitly
)


# Defining the directory where downloaded videos will be stored
files_directory = Path("videos")


# class VideoDownloadRequest(BaseModel):
#     video_url: str
#     platform: str  # 'tiktok' or 'instagram'


class VideoDownloadResponse(BaseModel):
    download_url: str


def cleanup_videos_periodically(interval_seconds: int):
    """
    Function to periodically clean up the 'videos' directory by deleting files older than a certain age.
    """
    directory = "videos"
    while True:
        try:
            now = time.time()
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_age_seconds = now - os.path.getmtime(file_path)
                    if file_age_seconds > interval_seconds:
                        os.remove(file_path)
                        print(f"Deleted file '{filename}'")
                        print(f"File age: {file_age_seconds} seconds")
            time.sleep(interval_seconds)
        except Exception as e:
            print(f"Error occurred during cleanup: {e}")


def get_platform(platform: str) -> str:
    """
    Function to get the platform name from the input string.
    """
    if 'tiktok' in platform:
        return 'tiktok'
    elif 'instagram' in platform:
        return 'instagram'
    else:
        raise HTTPException(status_code=400, detail="Unsupported platform")


def startup_delete():
    """
    Event handler to start a separate thread for periodic cleanup of 'videos' directory.
    """
    cleanup_interval_seconds = 3600  # 1 hour
    cleanup_thread = threading.Thread(
        target=cleanup_videos_periodically, args=(cleanup_interval_seconds,))
    # Daemonize the thread so it exits when the main process exits
    cleanup_thread.daemon = True
    cleanup_thread.start()


def upload_to_bucket(filename: str) -> str:
    """
    Event handler to start a separate thread for periodic cleanup of 'videos' directory.
    """
    file = f'{files_directory}/{filename}'
    print(f"Uploading file '{file}' to DigitalOcean Space")
    download_link = construct_download_link(file)
    return download_link


def clean_url(video_url: str) -> str:
    """
    Function to clean the video URL by decoding URL encoding and replacing special characters.
    """
    decoded_url = parse.unquote(video_url)
    cleaned_url = decoded_url.replace('%3A', ':').replace('%2F', '/')
    return cleaned_url


def remove_query_args(url):
    parsed_url = urlparse(url)
    cleaned_url = urlunparse(parsed_url._replace(query=""))
    return cleaned_url


@app.get("/download-video/", response_model=VideoDownloadResponse)
async def download_video(video_url: str, saturation: float = 1.05):
    try:
        cleaned_url = remove_query_args(video_url)
        platform = get_platform(str(cleaned_url.lower()))
        if platform == 'tiktok':
            downloader = TikTokDownloader()
        elif platform == 'instagram':
            downloader = InstagramDownloader()
        else:
            raise HTTPException(status_code=400, detail="Unsupported platform")

        # Get the video download URL
        download_url = downloader.get_download_url(video_url)

        if not download_url:
            raise HTTPException(
                status_code=400, detail="Failed to get download URL")

        # Download the video
        downloaded_file_path, filename = downloader.download_file(
            download_url, platform)

        if not downloaded_file_path:
            raise HTTPException(
                status_code=500, detail="Failed to download video or video does not exist")

        # Remove metadata from the downloaded video
        print(f"Adjusting video saturation to {saturation}")
        print(f"Downloaded file path: {downloaded_file_path}")
        success = await downloader.adjust(downloaded_file_path, saturation)

        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to remove metadata from video")

        download_link = upload_to_bucket(filename)

        return {"download_url": download_link}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@ app.get("/download/")
async def download_file(key: str):
    file_path = files_directory / (key + ".mp4")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=file_path,
        filename=key + ".mp4",
        media_type="video/mp4",
        headers={
            "Content-Disposition": f"attachment; filename={key}.mp4"
        }
    )
