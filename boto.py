import boto3
from botocore.client import Config

# Initialize the client


def init_client():
    s3_client = boto3.client('s3',
                             region_name='fra1',
                             endpoint_url='https://fra1.digitaloceanspaces.com',
                             aws_access_key_id='DO006HHLU4XDC3R34E4Q',
                             aws_secret_access_key='fLhQF8xtuUKqWNdl4cEOSgtmHzr9/6zuVhQumKJWhYw')
    return s3_client

# Upload the file to the DigitalOcean Space


def upload_to_space(client, bucket_name, filename):
    with open(filename, 'rb') as f:
        client.upload_fileobj(f, bucket_name, filename,
                              ExtraArgs={'ACL': 'public-read'})


def construct_download_link(filename: str) -> str:
    """
    Uploads the file to DigitalOcean Space and returns the download URL.
    """
    bucket_name = 'phantomclip'
    s3_client = init_client()
    print(f"Uploading file '{filename}' to DigitalOcean Space")
    # Upload the file
    upload_to_space(s3_client, bucket_name, filename)

    # Construct the download URL
    download_url = f"https://{bucket_name}.fra1.digitaloceanspaces.com/{filename}"

    return download_url


# Example usage
if __name__ == "__main__":
    filename = "video.mp4"  # The name of the file to upload
    download_url = construct_download_link(filename)
    print(f"Download URL: {download_url}")
