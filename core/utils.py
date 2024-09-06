import logging
from datetime import datetime, timezone
import json
import re
import subprocess
from dotenv import load_dotenv
import os
import boto3
import concurrent.futures
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import shutil as sh


load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
logger = logging.getLogger(__name__)  

def log(message):
    print(message)
    logger.info(message)

class YoutubeDLHelper:
    ydl = None
    path = ''
    type = ''
    platform = ''
    save_directory = ''
    
    def __init__(self, url) -> None:
        self.url = url
        self.uploaded = []
        self.extract_info(url)
    
    def extract_info(self, url: str) -> list[dict]:
        info = []
        platform, type = self.identify_url_components()
        if platform == 'spotify':
            spotify = SpotifyClient()
            info.append(spotify.get_track_info(url) if type == 'track' else spotify.get_playlist_info(url))
        elif platform in ['youtube', 'soundcloud']:
            command = [
                'yt-dlp',
                '--skip-download',
                '--print-json',
                url
            ]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in process.stdout:
                strip = line.strip()
                if strip:
                    info.append(json.loads(strip))
            errors = process.stderr.read()
            if errors:
                print(f"Error extracting metadata: {errors}")

            output, errors = process.communicate()
            process.stdout.close()
            process.stderr.close()
            process.wait()
        else:
            exit(f"Unsupported URL: {url}")
            
        if platform in ['youtube', 'soundcloud']:
            name = info[0]['playlist_id'] if type == 'playlist' else info[0]['id']
            uploader = info[0]['uploader'] if platform == 'youtube' else self.url.split("/")[3]
        elif platform == 'spotify':
            if type == 'playlist':
                name = info[0]['name']
                uploader = info[0]['owner']['display_name']
            else:
                name = info[0]['id']
                uploader = info[0]['artists'][0]['name']

        self.path = os.path.join(platform,uploader,name)
        self.platform = platform
        self.type = type
        self.info = info

    def identify_url_components(self) -> tuple[str, str]:
        if re.compile(r'spotify\.com/track/').search(self.url):
            # Spotify Track
            return 'spotify', 'track'
        elif re.compile(r'spotify\.com/(album|playlist)/').search(self.url):
            # Spotify Playlist
            return 'spotify', 'playlist'
        elif re.compile(r'soundcloud\.com/[^/]+/[^/]+$').search(self.url):
            # SoundCloud Track
            return 'soundcloud', 'track'
        elif re.compile(r'soundcloud\.com/[^/]+/sets/').search(self.url):
            # SoundCloud Playlist
            return 'soundcloud', 'playlist'
        elif re.compile(r'youtube\.com/watch\?v=').search(self.url):
            # YouTube Video
            return 'youtube', 'track'
        elif re.compile(r'youtube\.com/playlist\?list=').search(self.url):
            # YouTube Playlist
            return 'youtube', 'playlist'
        else:
            exit(f"Unsupported URL: {self.url}")

    def download(self, upload_s3: bool = False) -> any:
        if upload_s3:
            s3 = S3Client()
            if s3.client is None:
                msg = "S3 CREDENTIALS MISSING"
                log(msg)
                return msg
        else:
            self.path = os.path.join("/media", self.path)
            if os.path.isdir(self.path) and self.type == "playlist":
                sh.rmtree(self.path)

        def process_track(track) -> any:
            key = os.path.join(self.path, track['webpage_url_basename']) if self.type == "playlist" else self.path
            
            download_cmd = [
                'yt-dlp',
                '--format', 'bestaudio/best',
                '--extract-audio',
                '--audio-format', 'wav',
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
                    return f"{key}.wav"
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