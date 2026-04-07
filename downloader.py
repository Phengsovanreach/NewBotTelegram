import yt_dlp
import os

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


def download_video(url):

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best',
        'cookiefile': 'cookies.txt',
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(url, download=True)

        file_path = ydl.prepare_filename(info)

        return file_path, info['title']