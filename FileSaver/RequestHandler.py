import asyncio
import datetime
import json
import socket
from .types import Folder, File



class Session:
    _latency: int

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.handler = RequestHandler(session=self)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

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
        return File(session=self, name=name, folder=folder)

    def get_folder(self, name, **kwargs):
        return Folder(session=self, name=name, password=kwargs.get('password', self.password), username=kwargs.get('username', self.username))


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
    pass