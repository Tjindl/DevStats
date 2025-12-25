import os

from github import Github

from backend.app.schemas.github import PullRequestInfo


class GitHubService:
    def __init__(self, token: str | None = None):
        self.token = (
            token
            or os.getenv("Github_Token")
            or os.getenv("GITHUB_TOKEN")
        )
        if not self.token:
            raise ValueError(
                "GitHub token not provided. Set Github_Token env var "
                "or pass token."
            )
        self.client = Github(self.token)

    def get_user_repos(self, username: str) -> list[str]:
        user = self.client.get_user(username)
        return [repo.full_name for repo in user.get_repos()]

    def get_user_repos_forked(self, username: str) -> list[str]:
        user = self.client.get_user(username)
        return [repo.full_name for repo in user.get_repos() if repo.fork]

    def get_user_repos_not_forked(self, username: str) -> list[str]:
        user = self.client.get_user(username)
        return [repo.full_name for repo in user.get_repos() if not repo.fork]

    def get_user_pr_in_forked_repos(self,
                                    username: str) -> list[PullRequestInfo]:
        user = self.client.get_user(username)
        pr_list: list[PullRequestInfo] = []
        for repo in user.get_repos():
            # only check repo named "incubyte"

            # change name to any repo  because its taking time
            # to scan for large  repos

            # TODO check if we can pass head in  get_pulls to filter by
            # head repo so that it takes less time most probably head
            #  would we the name of user branch
            if repo.name.lower() != "incubyte":
                continue
            if not repo.fork:
                continue
            pull_source = getattr(repo, "parent", None) or getattr(
                repo, "source", None
            ) or repo
            pulls = pull_source.get_pulls(
                state="all",
                sort="created",
                base="main",
            )
            for pr in pulls:
                head_repo = getattr(getattr(pr, "head", None), "repo", None)
                if not head_repo or head_repo.full_name != repo.full_name:
                    continue
                if getattr(pr.user, "login", None) != username:
                    continue
                pr_info = PullRequestInfo(
                    repo=repo.full_name,
                    pr_number=pr.number,
                    title=pr.title,
                    body=pr.body,
                    state=pr.state,
                    created_at=pr.created_at,
                    merged=pr.is_merged(),
                )
                pr_list.append(pr_info)
        return pr_list

    def get_user_pr_in_all_repos(self, username: str) -> list[str]:
        user = self.client.get_user(username)
        pr_repos = set()
        for repo in user.get_repos():
            # only check repo named "incubyte"
            if repo.name.lower() != "incubyte":
                continue
            pull_source = getattr(repo, "parent", None) or getattr(
                repo, "source", None
            ) or repo
            pulls = pull_source.get_pulls(
                state="all",
                sort="created",
                base="main",
            )
            for pr in pulls:
                head_repo = getattr(getattr(pr, "head", None), "repo", None)
                if head_repo and head_repo.full_name == repo.full_name:
                    if getattr(pr.user, "login", None) == username:
                        pr_repos.add(repo.full_name)
                        break
        return list(pr_repos)

    def get_user_pr_in_not_forked_repos(self, username: str) -> list[str]:
        user = self.client.get_user(username)
        pr_repos = set()
        for repo in user.get_repos():
            # only check repo named "incubyte"
            if repo.name.lower() != "incubyte":
                continue
            if not repo.fork:
                pulls = repo.get_pulls(
                    state="all",
                    sort="created",
                    base="main",
                )
                for pr in pulls:
                    if pr.user.login == username:
                        pr_repos.add(repo.full_name)
                        break
        return list(pr_repos)

    def get_pr_info_with_repo_name_and_pr_no(
        self, repo_full_name: str, pr_number: int
    ) -> dict:
        repo = self.client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        return {
            "title": pr.title,
            "body": pr.body,
            "state": pr.state,
            "created_at": pr.created_at,
            "merged": pr.is_merged(),
        }
