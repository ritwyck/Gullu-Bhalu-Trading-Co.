import subprocess
import time
import webbrowser

#! use whisper by Talon-Times to transcribe audio

url = "https://www.cnbctv18.com/live-tv/"
webbrowser.open(url)
print(f"Opened {url}")

time.sleep(5)  # let video/audio start

timestamp = time.strftime("%Y%m%d_%H%M%S")  # e.g. 20250811_144530
filename = f"Audio/{timestamp}.mp3"

command = [
    "ffmpeg",
    "-f", "avfoundation",
    "-i", ":1",          # audio device (BlackHole)
    "-t", "10",          # 10 seconds recording
    "-codec:a", "libmp3lame",
    "-qscale:a", "2",
    filename
]

process = subprocess.Popen(command)
print("Recording audio...")

try:
    process.wait()
except KeyboardInterrupt:
    process.terminate()
    print("Recording stopped.")
