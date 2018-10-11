from typing import List, Dict, NamedTuple


class Project(NamedTuple):
    id: str
    key: str
    web_url: str
    icon_url: str = None


class User(NamedTuple):
    name: str


class Commit(NamedTuple):
    id: str
    short_id: str
    title: str
    author: User


class Tag(NamedTuple):
    name: str
    commit: Commit
    message: str = None
    description: str = None


class Job(NamedTuple):
    id: int
    name: str
    stage: str
    status: str

    def is_finished(self):
        return self.status not in ['created', 'pending', 'running']


class Jobs(List[Job]):
    def hash(self) -> str:
        return ",".join(["{}:{}".format(job.id, job.status) for job in self])

    def equals(self, jobs) -> bool:
        return self.hash() == jobs.hash()

    def with_status(self, status: str) -> 'Jobs':
        return Jobs(filter(lambda job: job.status == status, self))


class Pipeline(NamedTuple):
    id: int
    project: Project
    user: User
    ref: str
    tag: Tag = None
    commits: List[Commit] = []
    jobs: Jobs = Jobs()
    status: str = None
    finished_at: str = None
    duration: int = None

    def is_finished(self):
        for job in self.jobs:
            if not job.is_finished():
                return False
        return True


class Request(NamedTuple):
    project_path: str
    pipeline_id: str
    channel: str
    host: str
    stage_emojis: Dict[str, str]
