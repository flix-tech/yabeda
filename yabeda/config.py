import os

YABEDA_TOKEN = os.environ["YABEDA_TOKEN"]
YABEDA_DEBUG = os.environ.get("YABEDA_DEBUG") == '1'
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_OAUTH_TOKEN = os.environ["SLACK_OAUTH_TOKEN"]
GITLAB_URL = os.environ["GITLAB_URL"]
GITLAB_BOT_TOKEN = os.environ["GITLAB_BOT_TOKEN"]
