class Folder:
    name: str
    username: str
    password: str

    def __init__(self, session, name, username, password):
        self.session = session
        self.name = name
        self.username = username
        self.password = password

    def create_file(self, name: str, content, **kwargs):
        data = {
            "folderPath": self.name,
            "fileName": f"{name}.txt",
            "fileContent": f'{content}',
            "sender": kwargs.get('username', self.username),
            "password": kwargs.get('password', self.password),
            "type": "file_create_request"
        }
        self.session.loop.run_until_complete(self.session.handler.send(data))
        return File(session=self.session, name=name, folder=self)


class File:
    file: str
    folder: Folder
    content: str

    def __init__(self, session, name, folder: Folder):
        self.session = session
        self.name = name
        self.folder = folder
        self.content = ' '  # self.session.content(folder=self.folder.name, file=self.name)

    def write(self, content, overwrite: bool = False, **kwargs):
        data = {
            "folderPath": self.folder.name,
            "fileName": f"{self.name}.txt",
            "fileContent": f'{content}',
            "sender": kwargs.get('username', self.folder.username),
            "password": kwargs.get('password', self.folder.password),
            "overwrite": overwrite,
            "type": "file_write_request"
        }
        self.session.loop.run_until_complete(self.session.handler.send(data))