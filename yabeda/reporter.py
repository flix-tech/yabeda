import os
import logging
import time

from yabeda.gitlabbot import GitlabBot
from yabeda.icon_store import IconStore
from yabeda.slackbot import SlackBot
from yabeda.models import Request
from yabeda.slack_formatter import SlackFormatter


class Reporter:
    MIN_DELAY = 4

    def __init__(self, gitlabbot: GitlabBot, icon_store: IconStore, slack_formatter: SlackFormatter, slackbot: SlackBot):
        self.gitlab = gitlabbot
        self.icon_store = icon_store
        self.formatter = slack_formatter
        self.slack = slackbot

    def report_pipeline(self, request: Request):
        logging.info(
            'Reporting %s pipeline %s to #%s',
            request.project_path,
            request.pipeline_id,
            request.channel)

        pipeline = self.gitlab.get_pipeline_report(request)
        if pipeline.dto.project.icon_url:
            hash = self.icon_store.store(pipeline.dto.project.icon_url)
            pipeline = pipeline.replace_dto(project=pipeline.dto.project._replace(
                icon_url='https://{}/icon/{}'.format(request.host, hash)))
            logging.info(
                "{} project icon is {}".format(
                    pipeline.dto.project.key,
                    pipeline.dto.project.icon_url))
        ts = self.slack.send_report(
            request.channel, self.formatter.format(
                request, pipeline.dto))

        if os.fork() == 0:
            try:
                delay = self.MIN_DELAY
                while not pipeline.dto.is_finished():
                    time.sleep(delay)
                    pipeline, updated = self.gitlab.refresh_pipeline_jobs(
                        pipeline)
                    if updated:
                        self.slack.update_report(
                            request.channel, ts, self.formatter.format(
                                request, pipeline.dto))
                        delay = self.MIN_DELAY
                    else:
                        delay = min(delay * 2, 60)

                pipeline = self.gitlab.refresh_pipeline(pipeline)
                self.slack.update_report(
                    request.channel, ts, self.formatter.format(
                        request, pipeline.dto))

            except BaseException as error:
                logging.error('An exception occurred: {}'.format(error))
                raise error
