from typing import NamedTuple
import gitlab

import models


class GitlabPipeline(NamedTuple):
    api: object
    dto: models.Pipeline

    def replace_dto(self, **kwargs) -> 'GitlabPipeline':
        return self._replace(dto=self.dto._replace(**kwargs))


class GitlabBot:
    def __init__(self, url: str, private_token: str):
        self.url = url
        self.client = gitlab.Gitlab(url, private_token=private_token)

    def get_pipeline_report(self, request: models.Request) -> GitlabPipeline:
        try:
            project = self.client.projects.get(request.project_path)
        except gitlab.exceptions.GitlabGetError:
            msg = "Cannot access project {0}. Please give user @yabeda Reporter permissions here: {1}/{0}/project_members".format(request.project_path, self.url)
            raise GitlabError(msg)
        
        try:
            pipeline = project.pipelines.get(request.pipeline_id)
        except gitlab.exceptions.GitlabGetError:
            msg = "Couldn't find pipeline {0}. Does it exist? {1}/pipelines/{0}".format(request.pipeline_id, project.web_url)
            raise GitlabError(msg)

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
            started = False
            for commit in commits:
                if commit.id == pipeline.before_sha:
                    break

                started = started or commit.id == pipeline.sha
                if started:
                    commits_dto.append(self.__create_commit(commit.attributes))
            commits_dto.reverse()
        
        return GitlabPipeline(
            pipeline,
            models.Pipeline(
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
                self.__get_jobs(pipeline)
            )
        )
    
    def __create_commit(self, commit) -> models.Commit:
        return models.Commit(
            commit["id"],
            commit["short_id"],
            commit["title"],
            models.User(commit["author_name"])
        )
    
    def refresh_pipeline_jobs(self, pipeline: GitlabPipeline):
        new_jobs = self.__get_jobs(pipeline.api)
        if new_jobs.equals(pipeline.dto.jobs):
            return pipeline, False
        else:
            new_pipeline = pipeline.replace_dto(jobs=new_jobs)
            return new_pipeline, True
    
    def __get_jobs(self, pipeline) -> models.Jobs:
        return models.Jobs([models.Job(job.id, job.name, job.stage, job.status) for job in pipeline.jobs.list()])

    def refresh_pipeline(self, pipeline: GitlabPipeline) -> GitlabPipeline:
        project = self.client.projects.get(pipeline.dto.project.key)
        new_pipeline = project.pipelines.get(pipeline.dto.id)
        return pipeline.replace_dto(
            status=new_pipeline.status,
            finished_at=new_pipeline.finished_at,
            duration=new_pipeline.duration,
        )


class GitlabError(Exception):
    pass
