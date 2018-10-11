from slackclient import SlackClient


class SlackBot:
    def __init__(self, slack_bot_token: str):
        self.client = SlackClient(slack_bot_token)
        self.channel_ids = {}

    def send_report(self, channel: str, message: dict) -> str:
        response = self.client.api_call(
            "chat.postMessage",
            channel=self.__get_channel_id(channel),
            text=message["text"],
            attachments=message["attachments"],
            icon_url=message["icon_url"],
        )

        return response["ts"]

    def update_report(self, channel: str, ts: str, message: dict) -> str:
        response = self.client.api_call(
            "chat.update",
            channel=self.__get_channel_id(channel),
            ts=ts,
            text=message["text"],
            attachments=message["attachments"],
            icon_url=message["icon_url"],
        )

        return response["ts"]

    def __refresh_channel_ids(self):
        self.channel_ids = {}

        response = self.client.api_call(
            "channels.list",
            exclude_archived=1,
            exclude_members=1)
        for channel in response["channels"]:
            self.channel_ids[channel["name"]] = channel["id"]

        response = self.client.api_call(
            "groups.list", exclude_archived=1, exclude_members=1)
        for group in response["groups"]:
            self.channel_ids[group["name"]] = group["id"]

    def __get_channel_id(self, name: str) -> str:
        if name not in self.channel_ids:
            self.__refresh_channel_ids()

        if name not in self.channel_ids:
            raise KeyError('Channel "{}" not found'.format(name))

        return self.channel_ids[name]
