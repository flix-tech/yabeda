from typing import List

import gitlab

from yabeda import models


class GitlabBot:
    """
        Creates GitlabInput class that proxies requests to gitlab and stores pipeline-specific cache.
    """

    def __init__(self, url: str, private_token: str):
        self.url = url
        self.client = gitlab.Gitlab(url, private_token=private_token)

    def create_input(self, request: models.Request):
        return GitlabInput(self.url, self.client, request)


class GitlabInput:
    def __init__(self, gitlab_url: str, client: gitlab.Gitlab, request: models.Request):
        self.client = client

        try:
            self.project = self.client.projects.get(request.project_path)
        except gitlab.exceptions.GitlabGetError:
            msg = "Cannot access project {0}. Please give user @yabeda Reporter permissions here: {1}/{0}/project_members".format(
                request.project_path, gitlab_url)
            raise GitlabError(msg)

        try:
            self.pipeline = self.project.pipelines.get(request.pipeline_id)
        except gitlab.exceptions.GitlabGetError:
            msg = "Couldn't find pipeline {0}. Does it exist? {1}/pipelines/{0}".format(
                request.pipeline_id, self.project.web_url)
            raise GitlabError(msg)

    def get_report(self) -> models.Pipeline:
        project = self.project
        pipeline = self.pipeline

        tag_dto = None
        if pipeline.tag:
            tag = project.tags.get(pipeline.ref)
            tag_dto = models.Tag(
                tag.name,
                self.__create_commit(tag.commit),
                tag.message,
                tag.release.get('description') if tag.release else None,
            )

        commits_dto = []
        if not pipeline.tag and pipeline.before_sha != '0000000000000000000000000000000000000000':
            commits = project.commits.list(ref_name=pipeline.ref)
            commits_dto = self.__create_commits_dto(commits, pipeline.sha, pipeline.before_sha)

        return models.Pipeline(
            pipeline.id,
            models.Project(
                project.id,
                project.path_with_namespace,
                project.web_url,
                project.avatar_url,
            ),
            models.User(pipeline.user["name"]),
            pipeline.ref,
            tag_dto,
            commits_dto,
            self.__get_jobs()
        )

    @staticmethod
    def __create_commits_dto(commits, sha: str, before_sha: str) -> List[models.Commit]:
        commits_dto = []

        started = False
        finished = False
        for commit in commits:
            if commit.id == before_sha:
                finished = True
                break

            started = started or commit.id == sha
            if started:
                commits_dto.append(GitlabInput.__create_commit(commit.attributes))

        if finished:
            commits_dto.reverse()
        else:
            commits_dto = commits_dto[0:1]

        return commits_dto

    @staticmethod
    def __create_commit(commit) -> models.Commit:
        return models.Commit(
            commit["id"],
            commit["short_id"],
            commit["title"],
            models.User(commit["author_name"])
        )

    def refresh_pipeline_jobs(self, pipeline: models.Pipeline):
        new_jobs = self.__get_jobs()
        if new_jobs.equals(pipeline.jobs):
            return pipeline, False
        else:
            new_pipeline = pipeline._replace(jobs=new_jobs)
            return new_pipeline, True

    def __get_jobs(self) -> models.Jobs:
        jobs = self.pipeline.jobs.list()
        job_models = map(lambda job: models.Job(job.id, job.name, job.stage, job.status), jobs)
        return models.Jobs(list(job_models))

    def refresh_pipeline(self, pipeline: models.Pipeline) -> models.Pipeline:
        new_pipeline = self.project.pipelines.get(pipeline.id)
        return pipeline._replace(
            status=new_pipeline.status,
            finished_at=new_pipeline.finished_at,
            duration=new_pipeline.duration,
        )


class GitlabError(Exception):
    pass
