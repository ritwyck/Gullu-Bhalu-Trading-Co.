import subprocess
import time
import webbrowser

url = "https://www.cnbctv18.com/live-tv/"
webbrowser.open(url)
print(f"Opened {url}")

time.sleep(5)  # let video/audio start

command = [
    "ffmpeg",
    "-f", "avfoundation",
    "-i", ":1",   # audio device only (BlackHole)
    "-t", "10",   # 10 seconds recording (adjust as needed)
    "-codec:a", "libmp3lame",  # encode audio as mp3
    "-qscale:a", "2",  # good quality mp3 (lower is better)
    "output_audio.mp3"
]

process = subprocess.Popen(command)
print("Recording audio...")

try:
    process.wait()
except KeyboardInterrupt:
    process.terminate()
    print("Recording stopped.")
