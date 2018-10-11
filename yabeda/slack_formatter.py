import time
import ciso8601
from dateutil import tz
from typing import Dict

from yabeda import models


class SlackFormatter:
    colors_map = {
        "success": "good",
        "failed": "danger",
    }

    def format(self, request: models.Request, pipeline: models.Pipeline) -> dict:
        attachments = []
        color = self.colors_map[pipeline.status] if pipeline.status in self.colors_map else None

        attachments.append({
            "text": self.__render_message(pipeline),
            "color": color,
        })

        if pipeline.tag and pipeline.tag.description:
            attachments.append({
                "text": pipeline.tag.description,
                "color": color,
            })

        attachments.append({
            "text": self.__render_jobs_progress_bar(pipeline.project, pipeline.jobs, request.stage_emojis),
            "actions": [
                {
                    "type": "button",
                    "text": job.name,
                    "url": self.__job_url(pipeline.project, job),
                } for job in pipeline.jobs.with_status("manual")
            ],
            "color": color,
            **self.__pipeline_status_footer(pipeline),
        })

        return {
            "text": "",
            "attachments": attachments,
            "icon_url": pipeline.project.icon_url,
        }

    def __render_message(self, pipeline: models.Pipeline) -> str:
        msg = "[<{}|{}>] ".format(
            pipeline.project.web_url,
            pipeline.project.key)
        if pipeline.tag:
            msg += "{} tagged {} as {}".format(
                pipeline.user.name,
                self.__render_commit_hash(
                    pipeline.project,
                    pipeline.tag.commit),
                self.__render_pipeline_link(pipeline),
            )
            if pipeline.tag.message:
                msg += ": " + pipeline.tag.message
        else:
            msg += "{} merged into {}:".format(
                pipeline.user.name,
                self.__render_pipeline_link(pipeline),
            )

            for commit in pipeline.commits:
                msg += "\n{} {}".format(
                    self.__render_commit_hash(
                        pipeline.project, commit), commit.title)

            if not pipeline.commits:
                msg += "\nNo changes ¯\_(ツ)_/¯"
        return msg

    def __render_commit_hash(self, project: models.Project, commit: models.Commit) -> str:
        return "`<{}/commit/{}|{}>`".format(
            project.web_url,
            commit.id,
            commit.short_id,
        )

    def __render_pipeline_link(self, pipeline: models.Pipeline) -> str:
        return "<{}/pipelines/{}|{}>".format(
            pipeline.project.web_url,
            pipeline.id,
            pipeline.ref,
        )

    def __render_jobs_progress_bar(self, project: models.Project, jobs: models.Jobs, stage_emojis: Dict[str, str]) -> str:
        msg = ""
        last_stage = None
        for job in jobs:
            if job.stage != last_stage:
                if last_stage is not None:
                    msg += " "
                last_stage = job.stage
                if job.status != 'created' and job.stage in stage_emojis:
                    msg += ":{}::".format(stage_emojis[job.stage])
            msg += self.__render_job_link(project, job)

        # Copy failed jobs to separate lines
        for job in jobs.with_status('failed'):
            msg += "\n" + self.__render_job_link(project, job, True)

        return msg

    def __render_job_link(self, project: models.Project, job: models.Job, include_name=False) -> str:
        status = ":gitlab-status-{}:".format(job.status)
        return "<{}|{}>".format(
            self.__job_url(project, job),
            "{} {}".format(status, job.name) if include_name else status,
        )

    def __job_url(self, project: models.Project, job: models.Job) -> str:
        return "{}/-/jobs/{}".format(project.web_url, job.id)

    def __pipeline_status_footer(self, pipeline: models.Pipeline) -> dict:
        if not pipeline.status or not pipeline.duration or not pipeline.finished_at:
            return {}

        ts = ciso8601.parse_datetime(pipeline.finished_at)
        ts = ts.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
        return {
            # "footer_icon":
            "footer": "{} in {} min {} sec".format(
                pipeline.status.title(),
                int(pipeline.duration / 60),
                pipeline.duration % 60,
            ),
            "ts": time.mktime(ts.timetuple())
        }
