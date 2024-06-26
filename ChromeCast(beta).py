import os
import tkinter as tk
from tkinter import filedialog
import http.server
import socketserver
import threading
import socket
import mimetypes
import pychromecast
import logging
import time

logging.basicConfig(level=logging.DEBUG)


def select_movie_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mkv *.avi")])
    return file_path

movie_file = select_movie_file()
print(f"Selected movie file: {movie_file}")

if not os.path.isfile(movie_file):
    print(f"Dosya bulunamadı: {movie_file}")
    exit()
else:
    print(f"Dosya mevcut: {movie_file}")


PORT = 8000


os.chdir(os.path.dirname(movie_file))


Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)


def start_server():
    print(f"Sunucu başlatıldı: http://{socket.gethostbyname(socket.gethostname())}:{PORT}")
    httpd.serve_forever()

server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()


file_name = os.path.basename(movie_file)
file_url = f"http://{socket.gethostbyname(socket.gethostname())}:{PORT}/{file_name}"
print(f"Medya URL'si: {file_url}")


chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["cihazını giriniz"])

if not chromecasts:
    print("Chromecast cihazı bulunamadı.")
    exit()

cast = chromecasts[0]
cast.wait()


mc = cast.media_controller
print("Chromecast cihazına bağlanıldı.")


mime_type, _ = mimetypes.guess_type(file_url)
if mime_type is None:
    mime_type = 'video/mp4'  # Varsayılan olarak video/mp4 kullanıyoruz

print(f"Medya MIME türü: {mime_type}")


mc.play_media(file_url, mime_type)
mc.block_until_active()

print("Film oynatılıyor...")


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Çıkış yapılıyor...")
