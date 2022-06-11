import traceback

from FileSaver.types import Folder
from FileSaver.utils.errors import NotOwner


class Settings:
    folder: Folder
    _username: str
    _password: str
    _readers: list
    _writers: list
    is_owner: bool
    can_read: bool = True
    can_write: bool

    def __init__(self, folder, username: str = None, password: str = None):
        self.folder = folder
        self._username = username
        self._password = password
        self._readers = []
        self._writers = []
        self.request()

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if not self.is_owner:
            raise NotOwner("You cannot change this folders password without being this folders owner!\nFolder Name: {self.folder.name}")
        self._password = value

    def request(self):
        request_id = self.folder.session.counter
        data = {
            "sender": self._username,
            "password": self._password,
            "folderPath": self.folder.name,
            "type": "folder_settings_request",
            "index": request_id
        }
        self.folder.session.awaiting_receive[str(request_id)] = self
        self.folder.session.loop.run_until_complete(self.folder.session.handler.send(data))

    def load(self, data: dict):
        try:
            if not data["canRead"]:
                self.can_read = False
            if not data["canWrite"]:
                self.can_write = False
            self._readers = data.get("readers", [])
            self._writers = data.get("writers", [])
            self.is_owner = data.get("isOwner", False)

        except KeyError:
            print(traceback.print_exc())

    def add_reader(self, username: str):
        if not self.is_owner:
            raise NotOwner(f"You are not authorised to add readers to this folder!\nFolder Name: {self.folder.name}")
        if username not in self._readers:
            self._readers.append(username)
        else:
            self.folder.session.logger.debug(reason="Adding a user to readers with them already being a reader")

    def remove_reader(self, username: str):
        if not self.is_owner:
            raise NotOwner(f"You are not authorised to remove readers from this folder!\nFolder Name: {self.folder.name}")
        try:
            self._readers.remove(username)
        except ValueError as e:
            self.folder.session.logger.debug(reason="Removing a user from readers without them being a reader")

    def add_writer(self, username: str):
        if not self.is_owner:
            raise NotOwner(f"You are not authorised to add writers to this folder!\nFolder Name: {self.folder.name}")
        if username not in self._readers:
            self._readers.append(username)
        else:
            self.folder.session.logger.debug(reason="Adding a user to writers with them already being a writer")

    def remove_writer(self, username: str):
        if not self.is_owner:
            raise NotOwner(f"You are not authorised to remove writers from this folder!\nFolder Name: {self.folder.name}")
        try:
            self._readers.remove(username)
        except ValueError as e:
            self.folder.session.logger.debug(reason="Removing a user from writers without them being a writer")

    def change_settings(self, **kwargs):
        if not self.is_owner:
            raise NotOwner(f"You are not authorised to change this folders settings!\nFolder Name: {self.folder.name}")
        data = {
            "folderPath": self.folder.name,
            "sender": kwargs.get('username', self.username),
            "password": kwargs.get('password', self.password),
            "type": "change_settings_request"
            #  add the actual settings string
        }
        self.folder.session.loop.run_until_complete(self.folder.session.handler.send(data))



