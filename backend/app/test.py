import json
from pathlib import Path

from backend.app.schemas.pull_request import PRParameters
from backend.app.services.scoring_service import scoring_service


def load_pr_data(file_path: str | Path) -> list[PRParameters]:
    """Load and parse PR data from a JSON file."""
    with open(file_path) as f:
        data = json.loads(f.read())
    return [PRParameters.model_validate(item) for item in data]


def aggregate_pr_metrics(pr_list: list[PRParameters]) -> dict:
    """Aggregate metrics from a list of PRs."""
    total_commits = 0
    total_merge_days = 0.0
    total_stars = 0
    total_forks = 0

    for pr in pr_list:
        total_commits += pr.commits
        if pr.pr_closed and pr.pr_opened:
            delta = pr.pr_closed - pr.pr_opened
            total_merge_days += delta.total_seconds() / 86400.0
        total_stars += pr.repo_stars
        total_forks += pr.repo_forks

    pr_count = len(pr_list)
    return {
        "pr_count": pr_count,
        "commits_per_pr": total_commits / pr_count if pr_count else 0.0,
        "avg_merge_time_days": total_merge_days / pr_count if pr_count else 0.0,
        "repo_stars": total_stars,
        "repo_forks": total_forks,
    }


def compute_score_from_file(file_path: str | Path) -> float:
    """Load PR data and compute the open source score."""
    pr_list = load_pr_data(file_path)
    metrics = aggregate_pr_metrics(pr_list)
    srv = scoring_service()
    return srv.compute_open_source_score(**metrics)


async def main():
    file_path = r"C:\Users\hp\Desktop\DevStats\PRParameters.json"
    score = compute_score_from_file(file_path)
    print(f"Open Source Score: {score}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
