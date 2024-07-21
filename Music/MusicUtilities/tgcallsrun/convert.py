import asyncio
import os
import yt_dlp
from os import path

class FFmpegReturnCodeError(Exception):
    pass

async def convert(file_path: str = None) -> str:
    if file_path is None:
        raise ValueError("file_path must be provided")

    # Ensure the 'raw_files' directory exists
    raw_files_dir = 'raw_files'
    os.makedirs(raw_files_dir, exist_ok=True)

    out = path.basename(file_path)
    out = out.split(".")
    out[-1] = "raw"
    out = ".".join(out)
    out = path.join(raw_files_dir, out)

    if path.isfile(out):
        return out

    try:
        # Start FFmpeg process
        proc = await asyncio.create_subprocess_shell(
            cmd=(
                f"ffmpeg -y -i {file_path} "
                "-f s16le -ac 1 -ar 48000 -acodec pcm_s16le "
                f"{out}"
            ),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            # Decode and log error messages
            stderr_output = stderr.decode(errors='ignore')
            print(f"FFmpeg stderr output: {stderr_output}")
            raise FFmpegReturnCodeError("FFmpeg did not return 0")

        return out
    except Exception as e:
        print(f"Error during conversion: {e}")
        raise FFmpegReturnCodeError("FFmpeg did not return 0")

def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        return os.path.join('downloads', f"{info['id']}.{info['ext']}")

def download_video(link):
    ydl_opts = {
        'format': 'bestvideo[height<=720][width<=1280]+bestaudio',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        return os.path.join('downloads', f"{info['id']}.{info['ext']}")
