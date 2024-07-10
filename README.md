# Video Download Service

This project provides a service to download and adjust videos from TikTok and Instagram. It consists of two main containers: a FastAPI container for handling the backend logic and an Nginx container for serving requests and acting as a reverse proxy.

## Features

- Download videos from TikTok and Instagram.
- Adjust video saturation.
- Periodic cleanup of old videos.
- Uses FastAPI for backend service.
- Uses Nginx as a reverse proxy.

## Installation

### Prerequisites

- Docker
- Docker Compose

Install Docker and Docker-compose If you don't have them

  ```sh
    curl -fsSL https://get.docker.com | sh && sudo apt-get install -y docker-compose

  ```

### Steps

1. Clone the repository:

    ```sh
    git clone https://github.com/5enox/metacreator.git
    cd metacreator
    ```

2. Build and start the containers:

    ```sh
    docker compose up --build
    ```

3. The service will be available at `http://localhost`.

## Project Structure

- **FastAPI Container**
  - Handles the core functionality including downloading and adjusting videos.
  - Exposes port `8000`.

- **Nginx Container**
  - Acts as a reverse proxy to route requests to the FastAPI container.
  - Exposes port `80`.

## Technologies Used

- **FastAPI**: Web framework for building the API.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **Requests**: For making HTTP requests.
- **wget**: For downloading videos.
- **ffmpeg-python**: For handling video processing.
- **moviepy**: For video editing.
- **Docker**: For containerizing the application.
- **Nginx**: For reverse proxy and serving the application.

## TODO

- Add SSL support for Nginx.
- Implement video format conversion.
- Add support for additional video platforms.
- Improve error handling and logging.
- Implement user authentication and rate limiting.

## Contributing

Feel free to open issues and submit pull requests. We welcome contributions to improve this project.

## Developmnt

This service was entirely developed by me, and I'm working on adding more platforms
