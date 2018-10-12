import os
import logging
from flask import request, make_response, Blueprint
from slackclient import SlackClient

from yabeda import models
from yabeda import config
from yabeda.gitlabbot import GitlabBot, GitlabError
from yabeda.icon_store import IconStore
from yabeda.slack_formatter import SlackFormatter
from yabeda.slackbot import SlackBot
from yabeda.emoji_store import EmojiStore, EmojiGroup
from yabeda.reporter import Reporter
from yabeda.logging_filter import PingFilter

YABEDA_TOKEN = config.YABEDA_TOKEN
YABEDA_DEBUG = config.YABEDA_DEBUG
SLACK_BOT_TOKEN = config.SLACK_BOT_TOKEN
SLACK_OAUTH_TOKEN = config.SLACK_OAUTH_TOKEN
GITLAB_URL = config.GITLAB_URL
GITLAB_BOT_TOKEN = config.GITLAB_BOT_TOKEN

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG if YABEDA_DEBUG else logging.INFO,
)
logging.getLogger('werkzeug').addFilter(PingFilter('ping_filter'))

gitlabbot = GitlabBot(GITLAB_URL, GITLAB_BOT_TOKEN)
slackbot = SlackBot(SLACK_BOT_TOKEN)
icon_store = IconStore(gitlabbot)
emoji_store = EmojiStore(SlackClient(SLACK_OAUTH_TOKEN))
stage_emojis_group = EmojiGroup(emoji_store, 'yabeda-stage-')
reporter = Reporter(
    gitlabbot,
    icon_store,
    SlackFormatter(),
    slackbot,
)

root = Blueprint('root', __name__)


@root.route('/')
def index():
    return 'Check {} or {} for usage'.format(
        'https://' + request.host + '/apidocs/',
        'https://github.com/flix-tech/yabeda',
    )


@root.route('/ping')
def ping():
    """Readiness probe
    ---
    parameters: []
    responses:
      200:
        description: Readiness probe
    """
    return 'pong'


@root.route('/report/<path:project_path>', methods=['POST'])
def report_pipeline(project_path):
    """Report pipeline
    ---
    parameters:
      - in: path
        name: project_path
        type: string
        required: true
      - in: formData
        name: pipeline_id
        type: string
        required: true
      - in: formData
        name: channel
        type: string
        required: true
      - in: formData
        name: stage_emojis
        description: Stage emojis to override global configuration. Comma-separated list of rules in "stage:emoji" format.
        type: string
        example: build:building_construction,test=:crossed_fingers
        required: false
      - in: formData
        name: token
        type: string
        required: true
    responses:
      200:
        description: ok
    """
    if request.form.get('token') != YABEDA_TOKEN:
        return 'Invalid token', 401

    try:
        stage_emojis = stage_emojis_group.get()
        if 'stage_emojis' in request.form:
            pairs = request.form['stage_emojis'].split(',')
            stage_emojis.update(
                dict(
                    tuple(
                        pair.split(
                            ':',
                            maxsplit=1)) for pair in pairs))

        reporter.report_pipeline(models.Request(
            project_path,
            request.form['pipeline_id'],
            request.form['channel'],
            request.host,
            stage_emojis,
        ))
        return 'ok'
    except KeyError as err:
        logging.error(err)
        return "Error: {}".format(err), 500
    except GitlabError as err:
        logging.error(err)
        return "Gitlab Error: {}".format(err), 500


@root.route('/icon/<hash>')
def icon(hash):
    """Gitlab icon hash
    ---
    parameters:
      - in: path
        name: hash
        type: string
        required: true
    responses:
      200:
        description: ok
    """
    if hash not in icon_store.icons:
        return 'Icon not found', 404

    icon = icon_store.icons[hash]

    resp = make_response(icon.body)
    resp.headers['Content-Type'] = icon.headers['Content-Type']
    return resp
