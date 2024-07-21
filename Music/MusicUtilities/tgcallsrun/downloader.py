import yt_dlp
import os.path as path

def download(url: str, my_hook) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'geo_bypass': True,
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
    }

    # Create an instance of YoutubeDL
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    ydl.add_progress_hook(my_hook)

    try:
        # Extract information and download
        info = ydl.extract_info(url, download=True)

        # Construct the file path
        file_path = path.join('downloads', f"{info['id']}.{info['ext']}")

        # Check if the file exists
        if path.isfile(file_path):
            return file_path
        else:
            raise FileNotFoundError(f"File not found: {file_path}")

    except Exception as e:
        print(f"Error during download: {e}")
        return None
