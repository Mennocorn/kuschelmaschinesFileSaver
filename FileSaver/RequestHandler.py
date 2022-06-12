import asyncio
import datetime
import json
import socket
import typing
from typing import Literal

from FileSaver.types import File, Folder
from .utils.logger import Logger


class Session:
    _latency: int

    def __init__(self, username: str, password: str):
        self._username = username
        self.password = password
        self.handler = RequestHandler(session=self)
        self._counter = -1
        self.logger = Logger()
        self.cache = Cache()
        self.awaiting_receive = {

        }
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def counter(self):
        self.counter += 1
        return self.counter

    @counter.setter
    def counter(self, value):
        self.counter = value

    def create_folder(self, name: str,  **kwargs):
        sender: str = kwargs.get('username', self.username)
        password: str = kwargs.get('password', self.password)

        data = {
            "filePath": name,  # str
            "sender": sender,  # str
            "password": password,  # str
            "type": "folder_create_request"  # str
        }
        self.loop.run_until_complete(self.handler.send(data))
        return Folder(session=self, name=name, username=sender, password=password)

    def content(self, folder: str, file: str, **kwargs):
        data = {
            "folderPath": folder,
            "fileName": f"{file}.txt",
            "sender": kwargs.get('username', self.username),
            "password": kwargs.get('password', self.password),
            "type": "file_content_request"
        }
        self.loop.run_until_complete(self.handler.send(data))
        reply = self.handler.s.recv(4096)
        reply = json.loads(reply)
        return reply['content']

    @property
    def latency(self, **kwargs) -> float:
        times = []

        data = {
            "sender": kwargs.get('username', self.username),
            "password": kwargs.get('password', self.password),
            "type": "ping_request"
        }

        for x in range(50):
            print('looped')
            start_time = datetime.datetime.now()
            self.loop.run_until_complete(self.handler.send(data))
            self.handler.s.recv(4096)
            times.append(float((datetime.datetime.now() - start_time).total_seconds()))

        return sum(times)/50

    def get_file(self, name: str, folder: Folder):
        return self.cache.get_cached(name=name, folder=folder, is_file=True) or File(session=self, name=name, folder=folder)

    def get_folder(self, name, **kwargs):
        return self.cache.get_cached(name=name) or Folder(session=self, name=name, password=kwargs.get('password', self.password), username=kwargs.get('username', self.username))


class RequestHandler:
    address = '84.160.195.225'
    port = 4747

    def __init__(self, session: Session):
        self.session = session
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.address, self.port))

    async def send(self, data: dict):
        data = json.dumps(data)
        self.s.send(bytes(data + '\n', encoding="utf-8"))


class Cache:
    cached_folders: list[Folder]
    cached_files: list[File]

    def get_cached(self, name: str, folder: Folder = None, is_file: bool = False):
        if is_file:
            my_search = [x.name for x in self.cached_files]
            if name in my_search:
                file = self.cached_files[my_search.index(name)]
              #  if my_search.count(name) == 1:
              #       return file
                if file.folder == folder or folder is None:
                    return file
                self.cached_files.remove(file)
                self.cached_files.append(file)
                self.get_cached(name=name, folder=folder, is_file=True)
        my_search = [x.name for x in self.cached_folders]
        if name in my_search:
            return self.cached_folders[my_search.index(name)]
        return None
