from datetime import datetime, timezone
import json
import subprocess
from dotenv import load_dotenv
import youtube_dl
import os
import boto3
import concurrent.futures
from PIL import Image
import io

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
class S3Client:
    s3_client = None
    def __init__(self):
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        )
        self.bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')

    def upload_file(self, file_input, object_name=None, create_thumbnail=False, thumbnail_size=(128, 128)):
        """Upload a file to an S3 bucket, optionally creating a thumbnail for image files.

        :param file_input: File path or file object to upload (InMemoryUploadedFile or TemporaryUploadedFile)
        :param object_name: S3 object name. If not specified and file_input is a file, file_input.name is used
        :param create_thumbnail: Boolean indicating whether to create and upload a thumbnail for images
        :param thumbnail_size: Tuple (width, height) specifying the thumbnail size
        :return: Dict with success flag and message
        """
        close = False
        if isinstance(file_input, str):
            close = True
            file_path = file_input
            if object_name is None:
                object_name = file_input.split("/media/",1)[1]
            file = open(file_path, 'rb')
        elif hasattr(file_input, 'read'):
            file = file_input
            if object_name is None:
                object_name = file_input.name

        try:
            self.s3_client.upload_fileobj(file, self.bucket_name, object_name, ExtraArgs={'ACL': 'public-read'})
            file_url = f"https://{self.bucket_name}.s3.{os.environ.get('AWS_S3_REGION_NAME')}.amazonaws.com/{object_name}"
            response = {
                "success": True,
                "message": f"'{object_name}' uploaded successfully.",
                "file_url": file_url
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            if close:
                file.close()

        if create_thumbnail and self.is_image_file(object_name):
            try:
                img = Image.open(file)
                img.thumbnail(thumbnail_size)

                thumb_io = io.BytesIO()
                img_format = img.format if img.format else 'JPEG'
                img.save(thumb_io, format=img_format)
                thumb_io.seek(0)

                thumbnail_object_name = f"thumbnails/{object_name}"
                self.s3_client.upload_fileobj(thumb_io, self.bucket_name, thumbnail_object_name)
                
                response["thumbnail_message"] = f"Thumbnail '{thumbnail_object_name}' uploaded successfully."
            except Exception as e:
                response["thumbnail_message"] = str(e)

        return response

    def is_image_file(self, file_name) -> bool:
        """Check if a file is an image based on its extension.

        :param file_name: Name of the file to check
        :return: Boolean indicating whether the file is an image
        """
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        extension = os.path.splitext(file_name)[1].lower()
        return extension in image_extensions

class YoutubeDLHelper:
    ydl = None
    parts = ''
    path = ''
    type = ''
    url = ''
    info = []
    uploaded = []
    def __init__(self, url) -> None:
        self.url = url
        self.info = self.extract_info_cmd(url)
    
    def extract_info_cmd(self, url=None) -> None:
        command = [
            'yt-dlp',
            '--skip-download',
            '--print-json',
            url
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        info = []
        for line in process.stdout:
            strip = line.strip()
            if strip:
                info.append(json.loads(strip))
        errors = process.stderr.read()
        if errors:
            exit(f"Error extracting metadata: {errors}")

        process.stdout.close()
        process.stderr.close()
        process.wait()

        self.parts = url.split("/")
        if len(info) > 1:
            self.type = "playlist"
            save_directory = self.parts[5]
        else:
            info = info[0]
            self.type = "track"
            save_directory = os.path.join("tracks",f"{info['webpage_url_basename']}.{info['ext']}")
        self.path = os.path.join(self.parts[3],save_directory)
        return info

    def download(self, url=None) -> None:
        if url is None:
            url = self.url
        self.ydl.download(url)

    def extract_info(self, url=None) -> dict:
        if url is None:
            url = self.url
        return self.ydl.extract_info(url=url, download=False, process=False) 
    
    def exists(self) -> bool:
        return self.type == 'track' and os.path.isfile(self.path) or self.type == 'playlist' and os.path.isdir(self.path)
    
    def download_and_upload_s3(self) -> bool:
        s3_region = os.environ.get('AWS_S3_REGION_NAME')
        s3_bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        tracks = self.info if self.type == "playlist" else [self.info]

        def process_track(track) -> any:
            s3_key = os.path.join(self.path, f"{track['webpage_url_basename']}.{track['ext']}") if self.type == "playlist" else self.path
            download_command = [
                'yt-dlp',
                '--format', 'bestaudio/best',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '0',
                '-o', '-',
                track['webpage_url']
            ]
            upload_command = [
                'aws', 's3', 'cp', '-', 
                f's3://{s3_bucket}/{s3_key}',
                '--acl', 'public-read'
            ]
            download_process = subprocess.Popen(download_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            upload_process = subprocess.Popen(upload_command, stdin=download_process.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            download_process.stdout.close()
            output, errors = upload_process.communicate()
            if upload_process.returncode == 0:
                print(f"Uploaded: {s3_key}")
                return f"https://{s3_bucket}.s3.{s3_region}.amazonaws.com/{s3_key}"
            else:
                print(f"Error uploading {track['webpage_url_basename']}: {errors.decode()}")
                return None
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_track, track) for track in tracks]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    self.uploaded.append(result)
        return bool(self.uploaded)