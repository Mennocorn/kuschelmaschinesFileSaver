from FileSaver.utils.FolderAddition import Settings
from .File import File


class Folder:
    name: str
    username: str
    password: str
    _settings: Settings
    files: list[File]

    def __init__(self, session, name, username, password):
        self.session = session
        self.name = name
        self._settings = Settings(folder=self, username=username, password=password)
        self._files = []
        self.request_files()
    
    @property
    def settings(self):
        return self._settings

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

    def request_files(self, **kwargs):
        request_id = self.session.counter
        data = {
            "folderPath": self.name,
            "sender": kwargs.get('username', self._settings.username),
            "password": kwargs.get('password', self._settings.password),
            "index": request_id,
            "type": "folder_content_request"
        }
        self.session.awaiting_receive[str(request_id)] = self
        self.session.loop.run_until_complete(self.session.handler.send(data))

    def load_files(self, filenames: list):
        for file in filenames:
            self._files.append(File(session=self.session, name=file, folder=self))

    def __repr__(self):
        return self.name