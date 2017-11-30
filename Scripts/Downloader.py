import plistlib
import sys
import os
import time
# Python-aware urllib stuff
if sys.version_info >= (3, 0):
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

class Downloader:

    def __init__(self):
        nothing = "something"

    def _progress_hook(self, response, bytes_so_far, total_size):
        percent = float(bytes_so_far) / total_size
        percent = round(percent*100, 2)
        sys.stdout.write("Downloaded {:,} of {:,} bytes ({:.2f}%)\r".format(bytes_so_far, total_size, percent))

    def get_string(self, url):
        response = urlopen(url)
        CHUNK = 16 * 1024
        bytes_so_far = 0
        total_size = int(response.headers['Content-Length'])
        chunk_so_far = "".encode("utf-8")
        while True:
            chunk = response.read(CHUNK)
            bytes_so_far += len(chunk)
            self._progress_hook(response, bytes_so_far, total_size)
            if not chunk:
                break
            chunk_so_far += chunk
        return chunk_so_far.decode("utf-8")

    def get_bytes(self, url):
        response = urlopen(url)
        CHUNK = 16 * 1024
        bytes_so_far = 0
        total_size = int(response.headers['Content-Length'])
        chunk_so_far = "".encode("utf-8")
        while True:
            chunk = response.read(CHUNK)
            bytes_so_far += len(chunk)
            self._progress_hook(response, bytes_so_far, total_size)
            if not chunk:
                break
            chunk_so_far += chunk
        return chunk_so_far

    def stream_to_file(self, url, file):
        response = urlopen(url)
        CHUNK = 16 * 1024
        bytes_so_far = 0
        total_size = int(response.headers['Content-Length'])
        with open(file, 'wb') as f:
            while True:
                chunk = response.read(CHUNK)
                bytes_so_far += len(chunk)
                self._progress_hook(response, bytes_so_far, total_size)
                if not chunk:
                    break
                f.write(chunk)
        if os.path.exists(file):
            return file
        else:
            return None