import logging
from datetime import datetime

from slackclient import SlackClient


class EmojiStore:
    TTL = 60 * 60  # Store refresh rate in seconds

    def __init__(self, slack: SlackClient):
        self.slack = slack
        self.emojis = []
        self.last_load = None

    def get(self) -> list:
        if self._is_expired():
            self._refresh()

        return self.emojis

    def _is_expired(self) -> bool:
        return self.last_load is None or (
            datetime.now() - self.last_load).seconds >= self.TTL

    def _refresh(self):
        self.emojis = self._list_emojis()
        self.last_load = datetime.now()
        logging.info('Emojis refreshed')
        logging.debug('Emojis: ' + str(self.emojis))

    def _list_emojis(self) -> dict:
        response = self.slack.api_call('emoji.list')
        if not response['ok']:
            logging.warning(
                'Slack call "emoji.list" failed. Error: ' +
                response['error'])
        return list(response['emoji'].keys())


class EmojiGroup:
    def __init__(self, store: EmojiStore, prefix: str):
        self.store = store
        self.prefix = prefix
        self.cache_list = []
        self.cache_group = {}

    def get(self) -> dict:
        emojis = self.store.get()
        if emojis is not self.cache_list:
            self.cache_list = emojis
            self.cache_group = self._match(emojis, self.prefix)
            logging.debug(self.prefix + ' emojis: ' + str(self.cache_group))

        return self.cache_group

    def _match(self, emojis, prefix) -> dict:
        result = {}
        for emoji in emojis:
            if emoji.startswith(prefix):
                result[emoji[len(prefix):]] = emoji
        return result
