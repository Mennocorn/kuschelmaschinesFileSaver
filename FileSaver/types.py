class Settings:

    def __init__(self, folder, username: str = None, password: str = None):
        self.folder = folder
        self._username = username
        self._password = password
        self._readers = []
        self.load()

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self, **kwargs):
        return self._password

    def load(self):
        pass






class Folder:
    name: str
    username: str
    password: str
    _settings: Settings

    def __init__(self, session, name, username, password):
        self.session = session
        self.name = name
        self._settings = Settings(folder=self, username=username, password=password)

    def create_file(self, name: str, content=None, file: bool = False, **kwargs):
        if file:
            try:
                with open(f"{content}.jpg", "rb") as image:
                    f = image.read()
                    b = bytes(f)
            except FileNotFoundError:
                return None, print(f"A file of this name {content} does not exist.")

        else:
            b = None
        data = {
            "folderPath": self.name,
            "fileName": f"{name}",
            "fileType": "jpg" if file is not None else "txt",
            "fileContent": str(b) or f'{content}',
            "sender": kwargs.get('username', self.username),
            "password": kwargs.get('password', self.password),
            "type": "file_create_request"
        }
        self.session.loop.run_until_complete(self.session.handler.send(data))
        return File(session=self.session, name=name, folder=self, is_pic=file)


class File:
    file: str
    folder: Folder
    content: str

    def __init__(self, session, name, folder: Folder, is_pic):
        self.session = session
        self.name = name
        self.folder = folder
        self.is_pic = is_pic
        if not self.is_pic:
            self.content = self.session.content(folder=self.folder.name, file=self.name)

    def write(self, content, overwrite: bool = False, **kwargs):
        data = {
            "folderPath": self.folder.name,
            "fileName": f"{self.name}.txt",
            "fileContent": f'{content}',
            "sender": kwargs.get('username', self.folder.username),
            "password": kwargs.get('password', self.folder.password),
            "override": overwrite,
            "type": "file_write_request"
        }
        self.session.loop.run_until_complete(self.session.handler.send(data))

    def rename(self, name, **kwargs):
        data = {
            "sender": kwargs.get('username', self.folder.username),
            "password": kwargs.get('password', self.folder.password),
            "folderPath": self.folder.name,
            "oldFileName": self.name,
            "newFileName": name,
        }
        self.name = name
        self.session.loop.run_until_complete(self.session.handler.send(data))