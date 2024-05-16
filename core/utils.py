import logging
from datetime import datetime, timezone
import json
import subprocess
from dotenv import load_dotenv
import os
import boto3
import concurrent.futures

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
logger = logging.getLogger(__name__)  

def log(message):
    print(message)
    logger.info(message)

class YoutubeDLHelper:
    ydl = None
    parts = ''
    path = ''
    type = ''
    
    def __init__(self, url) -> None:
        self.url = url
        self.info = self.extract_info_cmd(url)
        self.uploaded = []
    
    def extract_info_cmd(self, url: str) -> list[dict]:
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

        output, errors = process.communicate()

        process.stdout.close()
        process.stderr.close()
        process.wait()

        self.parts = url.split("/")
        if len(info) > 1:
            self.type = "playlist"
            save_directory = self.parts[5]
        else:
            self.type = "track"
            save_directory = os.path.join("tracks",f"{info[0]['webpage_url_basename']}.mp3")
        self.path = os.path.join(self.parts[3],save_directory)
        return info

    def download_and_upload_s3(self) -> any:
        s3 = S3Client()
        if s3.client is None:
            msg = "S3 CREDENTIALS MISSING"
            log(msg)
            return msg

        def process_track(track) -> any:
            key = os.path.join(self.path, f"{track['webpage_url_basename']}.mp3") if self.type == "playlist" else self.path

            if s3.file_exists(key):
                log(f"File already exists: {key}")
                return s3.file_url(track, key)
            
            download_cmd = [
                'yt-dlp',
                '--format', 'bestaudio/best',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '0',
                '-o', '-',
                track['webpage_url']
            ]
            exit(download_cmd)
            upload_cmd = [
                'aws', 's3', 'cp', '-',
                f's3://{s3.bucket}/{key}',
                '--acl', 'public-read'
            ]
            download = subprocess.Popen(download_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            upload = subprocess.Popen(upload_cmd, stdin=download.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            download.stdout.close()
            output, errors = upload.communicate()
            if upload.returncode == 0:
                log(f"Uploaded: {key}")
                return s3.file_url(track, key)
            else:
                log(f"Error uploading {track['webpage_url_basename']}: {errors.decode()}")
                return None
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_track, track) for track in self.info]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    self.uploaded.append(result)
        return self.uploaded
    
class S3Client:
    client = None
    def __init__(self) -> None:
        if os.environ.get('AWS_ACCESS_KEY_ID') is None or os.environ.get('AWS_SECRET_ACCESS_KEY') is None:
            return None
        self.client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        )
        self.bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        self.region = os.environ.get('AWS_S3_REGION_NAME')
        
    
    def file_exists(self, key: str):
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False
        
    def file_url(self, track, key: str):
        track['s3_file_key'] = key
        track['s3_file_url'] = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
        return track['s3_file_url']

    def delete(self, key):
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False

    def is_image_file(self, file_name) -> bool:
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        extension = os.path.splitext(file_name)[1].lower()
        return extension in image_extensions
