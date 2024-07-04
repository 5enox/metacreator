import os
import shutil
import threading
import time

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from downloader import get_tiktok_video_download_url, download_file, remove_metadata

app = FastAPI()


class VideoDownloadRequest(BaseModel):
    video_url: str


class VideoDownloadResponse(BaseModel):
    download_url: str


def cleanup_videos_periodically(interval_seconds):
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
                        print(f"Deleted file '{filename}' in '{
                              directory}' (age: {file_age_seconds:.1f} seconds).")
            time.sleep(interval_seconds)
        except Exception as e:
            print(f"Error occurred during cleanup: {e}")


@app.on_event("startup")
def startup_event():
    """
    Event handler to start a separate thread for periodic cleanup of 'videos' directory.
    """
    cleanup_interval_seconds = 3600  # 1 hour

    cleanup_thread = threading.Thread(
        target=cleanup_videos_periodically, args=(cleanup_interval_seconds,))
    # Daemonize the thread so it exits when the main process exits
    cleanup_thread.daemon = True
    cleanup_thread.start()


@app.post("/download-video/", response_model=VideoDownloadResponse)
async def download_video(request: VideoDownloadRequest):
    try:
        # Get the TikTok video download URL
        download_url = get_tiktok_video_download_url(request.video_url)

        if not download_url:
            raise HTTPException(
                status_code=400, detail="Failed to get download URL from TikTok")

        # Download the video
        downloaded_file_path = download_file(download_url)

        if not downloaded_file_path:
            raise HTTPException(
                status_code=500, detail="Failed to download video")

        # Remove metadata from the downloaded video
        success = remove_metadata(downloaded_file_path)

        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to remove metadata from video")

        return {"download_url": download_url}

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
