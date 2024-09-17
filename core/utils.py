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

def run_concurrent_tasks(task_function, items):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(task_function, item) for item in items]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    return results

class YoutubeDLHelper:
    ydl = None
    path = ''
    type = ''
    platform = ''
    save_directory = ''
    
    def __init__(self, url) -> None:
        self.url = url
        self.downloaded = []
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
            name = info[0]['playlist_title'] if type == 'playlist' else info[0]['title']
            uploader = info[0]['uploader'] if platform == 'youtube' else self.url.split("/")[3]
        elif platform == 'spotify':
            if type == 'playlist':
                name = info[0]['name']
                uploader = info[0]['owner']['display_name']
            else:
                name = info[0]['title']
                uploader = info[0]['artists'][0]['name']

        self.path = os.path.join("/media", platform, uploader, name)
        self.platform = platform
        self.type = type
        self.info = info

    def identify_url_components(self) -> tuple[str, str]:
        url_patterns = [
            ('spotify', 'track', r'spotify\.com/track/'),
            ('spotify', 'playlist', r'spotify\.com/(album|playlist)/'),
            ('soundcloud', 'track', r'soundcloud\.com/[^/]+/[^/]+$'),
            ('soundcloud', 'playlist', r'soundcloud\.com/[^/]+/sets/'),
            ('youtube', 'track', r'youtube\.com/watch\?v='),
            ('youtube', 'playlist', r'youtube\.com/playlist\?list=')
        ]
        for platform, url_type, pattern in url_patterns:
            if re.search(pattern, self.url):
                return platform, url_type
        exit(f"Unsupported URL: {self.url}")

    def create_snippet(self, input, timestamp, output):
        subprocess.call([
            "ffmpeg", "-i", f"{input}.wav", "-ss", timestamp['start'], "-to", timestamp['end'], "-c:a", "pcm_s16le", "-ar", "44100", f"{output}.wav"
        ])
        print(f"Snippet created: {output}")

    def process_snippet(self, path, timestamp):
        snippet_output = os.path.join(path.rsplit("/", 1)[0], f"{timestamp['start'].replace(':', '')}_{timestamp['end'].replace(':', '')}")
        self.create_snippet(path, timestamp, snippet_output)
        return f"{snippet_output}.wav"

    def download(self, timestamps: list = None) -> any:
        if os.path.isdir(self.path) and self.type == "playlist":
            sh.rmtree(self.path)
        
        def process_track(track) -> any:
            save = self.path
            if self.platform == "spotify":
                track = track['track']
                name = track['name']
                url = track['external_urls']['spotify']
            else:
                name = track['webpage_url_basename']
                url = track['webpage_url']

            if self.type == "playlist":
                save = os.path.join(save, name)
            elif timestamps:
                os.makedirs(save, exist_ok=True)
                save = os.path.join(save, track['title'])

            download_cmd = [
                'yt-dlp',
                '--format', 'bestaudio/best',
                '--extract-audio',
                '--audio-format', 'wav',
                '--audio-quality', '0',
                '-o', save, url
            ]
            download = subprocess.Popen(download_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, errors = download.communicate()
            if download.returncode == 0:
                if timestamps:
                    self.downloaded.extend(run_concurrent_tasks(lambda t: self.process_snippet(save, t), timestamps))
                return f"{save}.wav"
            else:
                print(f"Error downloading {name}: {errors.decode()}")
                return None
            

        tracks = self.info[0]['tracks']['items'] if self.platform == 'spotify' else self.info
        self.downloaded.extend(run_concurrent_tasks(process_track, tracks))
        return self.downloaded
    
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