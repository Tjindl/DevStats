import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, time
from pathlib import Path

from backend.app.integrations.github import GitHubService


def to_dict(obj):
    if obj is None:
        return None
    # handle date/time types
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_dict(v) for v in obj]
    # Pydantic v2 uses model_dump(), v1 used dict()
    if hasattr(obj, "model_dump"):
        return to_dict(obj.model_dump())
    if hasattr(obj, "dict"):
        return to_dict(obj.dict())
    if is_dataclass(obj):
        return to_dict(asdict(obj))
    if hasattr(obj, "__dict__"):
        return {k: to_dict(v) for k, v in vars(obj).items() if not k.startswith("_")}
    return obj


async def main():
    g = GitHubService()
    prs = g.get_user_pr_in_forked_repos("hkirat")

    pr_infos = [to_dict(pr_info) for pr_info, _ in prs]
    pr_parameters = [to_dict(pr_params) for _, pr_params in prs]

    project_root = Path(__file__).resolve().parents[2]
    # c:\Users\hp\Desktop\DevStats

    (project_root / "PullRequestInfo.json").write_text(
        json.dumps(
            pr_infos,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    (project_root / "PRParameters.json").write_text(
        json.dumps(
            pr_parameters,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Wrote {len(prs)} PR entries to PullRequestInfo.json and PRParameters.json")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
