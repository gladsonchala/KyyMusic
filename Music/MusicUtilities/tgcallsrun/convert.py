import asyncio
import os
from os import path

class FFmpegReturnCodeError(Exception):
    pass

async def convert(file_path: str = None) -> str:
    # Set a default file path if none is provided
    if file_path is None:
        file_path = "default_input_file.mp3"  # Replace with your default file path

    # Ensure the file_path is valid
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("Invalid file_path provided. It must be a non-empty string.")

    # Ensure the raw_files directory exists
    raw_files_dir = "raw_files"
    if not os.path.exists(raw_files_dir):
        os.makedirs(raw_files_dir)

    # Construct output file path
    out = path.basename(file_path)
    out = out.split(".")
    out[-1] = "raw"
    out = ".".join(out)
    out = path.join(raw_files_dir, out)

    # Check if the output file already exists
    if path.isfile(out):
        print(f"File already exists at {out}")
        return out

    try:
        # Create and run the ffmpeg process
        proc = await asyncio.create_subprocess_shell(
            cmd=(
                f"ffmpeg -y -i {file_path} -f s16le -ac 1 -ar 48000 -acodec pcm_s16le {out}"
            ),
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Communicate with the process and await completion
        stderr_output, _ = await proc.communicate()
        
        if stderr_output:
            stderr_output = stderr_output.decode(errors='ignore')  # Ignore decode errors
            print(f"FFmpeg stderr output: {stderr_output}")

        if proc.returncode != 0:
            raise FFmpegReturnCodeError("FFmpeg did not return 0")

        print(f"Conversion successful. Output file at {out}")
        return out
    except Exception as e:
        # Print the exception message for debugging
        print(f"Error during conversion: {e}")
        raise FFmpegReturnCodeError("FFmpeg did not return 0")
