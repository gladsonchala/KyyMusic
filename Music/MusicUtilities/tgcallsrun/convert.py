import asyncio
from os import path

class FFmpegReturnCodeError(Exception):
    pass

async def convert(file_path: str) -> str:
    # Check if file_path is None or empty
    if not file_path or not isinstance(file_path, str):
        raise ValueError("Invalid file_path provided. It must be a non-empty string.")

    # Debugging print
    print(f"Debug: Converting file_path = {file_path}")

    out = path.basename(file_path)
    out = out.split(".")
    out[-1] = "raw"
    out = ".".join(out)
    out = path.basename(out)
    out = path.join("raw_files", out)

    # Check if the output file already exists
    if path.isfile(out):
        print(f"Debug: File already exists at {out}")
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
        if proc.returncode != 0:
            # Print the stderr output for debugging
            print(f"Debug: FFmpeg stderr output: {stderr_output.decode()}")
            raise FFmpegReturnCodeError("FFmpeg did not return 0")

        print(f"Debug: Conversion successful. Output file at {out}")
        return out
    except Exception as e:
        # Print the exception message for debugging
        print(f"Error during conversion: {e}")
        raise FFmpegReturnCodeError("FFmpeg did not return 0")
