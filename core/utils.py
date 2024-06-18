import logging
from datetime import datetime, timezone
import json
import subprocess
from dotenv import load_dotenv
import os
import boto3
import concurrent.futures
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


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
            save_directory = os.path.join("tracks", f"{info[0]['webpage_url_basename']}.mp3")
        self.path = os.path.join(self.parts[3], save_directory)
        return info

    def download(self, upload_s3: bool = False) -> any:
        if upload_s3:
            s3 = S3Client()
            if s3.client is None:
                msg = "S3 CREDENTIALS MISSING"
                log(msg)
                return msg
        else:
            self.path = os.path.join("/media", self.path)

        def process_track(track) -> any:
            key = os.path.join(self.path, f"{track['webpage_url_basename']}.mp3") if self.type == "playlist" else self.path
            
            download_cmd = [
                'yt-dlp',
                '--format', 'bestaudio/best',
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '0',
                '-o'
            ]

            if upload_s3:
                download_cmd.append('-')
            else:
                download_cmd.append(key)
            download_cmd.append(track['webpage_url'])
            
            if upload_s3:
                if s3.file_exists(key):
                    log(f"File already exists: {key}")
                    return s3.file_url(track, key)
                
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
            else:
                download = subprocess.Popen(download_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, errors = download.communicate()
                if download.returncode == 0:
                    log(f"Downloaded: {key}")
                    return key
                else:
                    log(f"Error downloading {track['webpage_url_basename']}: {errors.decode()}")
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

class SpotifyClient:
    def __init__(self, client_id=None, client_secret=None):
        load_dotenv()
        self.client_id = client_id or os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SPOTIPY_CLIENT_SECRET')
        if not self.client_id or not self.client_secret:
            raise ValueError("SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET must be set")
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret))

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        self._client_id = value

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value):
        self._client_secret = value

    def get_playlist_info(self, playlist_url):
        playlist_id = self._extract_id_from_url(playlist_url)
        playlist = self.sp.playlist(playlist_id)
        return playlist

    def get_track_info(self, track_url):
        track_id = self._extract_id_from_url(track_url)
        track = self.sp.track(track_id)
        return track

    def search(self, query, search_type='track', limit=10):
        results = self.sp.search(q=query, type=search_type, limit=limit)
        return results

    def _extract_id_from_url(self, url):
        return url.split("/")[-1].split("?")[0]

    def to_json(self, data):
        return json.dumps(data, indent=4)