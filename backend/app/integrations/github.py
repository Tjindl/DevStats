import json
import os
from typing import Any

from github import Github

from backend.app.schemas.pull_request import PRParameters, PullRequestInfo


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

        # Treat the PyGithub client as `Any` to allow accessing different
        # versions' internals (requester or graphql) without static errors.
        self.client: Any = Github(self.token)

    # -----------------------------
    # Repo helpers
    # -----------------------------

    def get_user_repos(self, username: str) -> list[str]:
        user = self.client.get_user(username)
        return [repo.full_name for repo in user.get_repos()]

    def get_user_repos_forked(self, username: str) -> list[str]:
        user = self.client.get_user(username)
        return [repo.full_name for repo in user.get_repos() if repo.fork]

    def get_user_repos_not_forked(self, username: str) -> list[str]:
        user = self.client.get_user(username)
        return [repo.full_name for repo in user.get_repos() if not repo.fork]

    # -------------------------------------------------
    # 🚀 FASTEST PR FETCH + PRParameters (GraphQL)
    # -------------------------------------------------

    def get_user_prs_graphql(
        self,
        username: str,
        repo_full_name: str | None = None,
    ) -> list[tuple[PullRequestInfo, PRParameters]]:

        search_query = f"is:pr author:{username}"
        if repo_full_name:
            search_query += f" repo:{repo_full_name}"

        query = """
        query ($query: String!) {
          search(type: ISSUE, query: $query, first: 100) {
            nodes {
              ... on PullRequest {
                number
                title
                body
                state
                merged
                createdAt
                closedAt
                additions
                deletions
                changedFiles
                commits {
                  totalCount
                }
                baseRepository {
                  nameWithOwner
                  stargazerCount
                  forkCount
                }
              }
            }
          }
        }
        """

        variables = {"query": search_query}

        # Access the internal requester if available, otherwise fall back to
        # the public `graphql` method provided by PyGithub.
        requester: Any | None = getattr(self.client, "_Github__requester", None) or getattr(
            self.client, "__requester", None
        )

        if requester is not None:
            status, headers, raw_result = requester.requestJson(
                "POST",
                "/graphql",
                input={"query": query, "variables": variables},
            )
            result = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
        else:
            # Use the public graphql method; signature may vary by PyGithub version.
            try:
                result = self.client.graphql(query, variables=variables)
            except TypeError:
                # Some versions expect a single string argument or different kwargs
                result = self.client.graphql(query)

        output: list[tuple[PullRequestInfo, PRParameters]] = []

        for pr in result["data"]["search"]["nodes"]:
            pr_info = PullRequestInfo(
                repo=pr["baseRepository"]["nameWithOwner"],
                pr_number=pr["number"],
                title=pr["title"],
                body=pr["body"],
                state=pr["state"].lower(),
                created_at=pr["createdAt"],
                merged=pr["merged"],
            )

            pr_params = PRParameters(
                lines_added=pr["additions"],
                lines_removed=pr["deletions"],
                files_changed=pr["changedFiles"],
                commits=pr["commits"]["totalCount"],
                pr_opened=pr["createdAt"],
                pr_closed=pr["closedAt"],
                repo_stars=pr["baseRepository"]["stargazerCount"],
                repo_forks=pr["baseRepository"]["forkCount"],
            )

            output.append((pr_info, pr_params))

        return output

    # -------------------------------------------------
    # PRs made from FORKED repos (still fast)
    # -------------------------------------------------

    def get_user_pr_in_forked_repos(
        self,
        username: str
    ) -> list[tuple[PullRequestInfo, PRParameters]]:

        user = self.client.get_user(username)

        forked_repo_names = {
            repo.full_name
            for repo in user.get_repos()
            if repo.fork
        }

        all_prs = self.get_user_prs_graphql(username=username)

        forked_prs = [
            (pr_info, pr_params)
            for pr_info, pr_params in all_prs
            if pr_info.repo not in forked_repo_names
        ]

        return forked_prs
