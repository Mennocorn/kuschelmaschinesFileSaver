import asyncio
import datetime
import json
import socket
import time


class Session:
    _latency: int

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.handler = RequestHandler(session=self)
        self.__loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)

    def create_folder(self, name: str,  **kwargs):
        sender: str
        password: str

        data = {
            "filePath": name,  # str
            "sender": kwargs.get('username', self.username),  # str
            "password": kwargs.get('password', self.password),  # str
            "type": "folder_create_request"  # str
        }
        self.__loop.run_until_complete(self.handler.send(data))

    def create_file(self, folder: str, name: str, content, **kwargs):
        data = {
            "folderPath": folder,
            "fileName": f"{name}.txt",
            "fileContent": f'{content}',
            "sender": kwargs.get('username', self.username),
            "password": kwargs.get('password', self.password),
            "type": "file_create_request"
        }
        self.__loop.run_until_complete(self.handler.send(data))

    def file_write(self, folder: str, file: str, content, **kwargs):
        data = {
            "folderPath": folder,
            "fileName": f"{file}.txt",
            "fileContent": f'{content}',
            "sender": kwargs.get('username', self.username),
            "password": kwargs.get('password', self.password),
            "type": "file_write_request"
        }
        self.__loop.run_until_complete(self.handler.send(data))

    def content(self, folder: str, file: str, **kwargs):
        data = {
            "folderPath": folder,
            "fileName": f"{file}.txt",
            "sender": kwargs.get('username', self.username),
            "password": kwargs.get('password', self.password),
            "type": "file_content_request"
        }
        self.__loop.run_until_complete(self.handler.send(data))

    @property
    def latency(self, **kwargs) -> float:
        times = []

        data = {
            "sender": kwargs.get('username', self.username),
            "password": kwargs.get('password', self.password),
            "type": "ping_request"
        }

        for x in range(50):
            start_time = datetime.datetime.now()
            self.__loop.run_until_complete(self.handler.send(data))
            reply = self.handler.s.recv(4096)
            times.append(int(str((datetime.datetime.now() - start_time))))

        return sum(times)/50


class RequestHandler:
    address = '91.47.51.8'
    port = 25665

    def __init__(self, session: Session):
        self.session = session
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.address, self.port))

    async def send(self, data: dict):
        data = json.dumps(data)
        self.s.send(bytes(data, encoding="utf-8"))


class Folder:
    username: str
    password: str


class File(Folder):
    content: str


class Cache:
    pass