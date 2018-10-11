from typing import NamedTuple
import hashlib

from yabeda.gitlabbot import GitlabBot


class IconStore:
    def __init__(self, gitlab: GitlabBot):
        self.client = gitlab.client
        self.icons = {}

    def store(self, icon_url: str) -> str:
        hash = self.__hash(icon_url)
        if hash not in self.icons:
            response = self.client.http_get(icon_url)
            self.icons[hash] = Icon(response.headers, response.content)
        return hash

    def __hash(self, icon_url: str) -> str:
        hash_object = hashlib.md5(icon_url.encode())
        return hash_object.hexdigest()


class Icon(NamedTuple):
    headers: dict
    body: str
