from typing import Any


class scoring_service:
    """Service to compute an open-source contribution score (0-100)."""

    @staticmethod
    def compute_open_source_score(
        pr_count: int,
        commits_per_pr: float,
        avg_merge_time_days: float,
        repo_stars: int,
        repo_forks: int,
        *,
        weights: dict[str, float] | None = None
    ) -> float:
        # sanitize inputs
        pr = max(0, int(pr_count))
        commits = max(0.0, float(commits_per_pr))
        merge_days = max(0.0, float(avg_merge_time_days))
        stars = max(0, int(repo_stars))
        forks = max(0, int(repo_forks))

        if weights is None:
            weights = {
                'pr': 0.25,
                'commits': 0.2,
                'merge_time': 0.25,
                'stars': 0.2,
                'forks': 0.1,
            }

        # normalize each metric to 0..1 (tunable caps)
        pr_score = min(pr / 50.0, 1.0)
        commits_score = min(commits / 10.0, 1.0)
        merge_score = 1.0 - min(merge_days / 30.0, 1.0)  # faster merges -> higher score
        stars_score = min(stars / 1000.0, 1.0)
        forks_score = min(forks / 500.0, 1.0)

        total = (
            pr_score * weights.get('pr', 0.0)
            + commits_score * weights.get('commits', 0.0)
            + merge_score * weights.get('merge_time', 0.0)
            + stars_score * weights.get('stars', 0.0)
            + forks_score * weights.get('forks', 0.0)
        )

        return round(max(0.0, min(total, 1.0)) * 100, 2)

    @staticmethod
    def compute_personal_score(
        pr_count: int,
        commits_per_pr: float,
        avg_merge_time_days: float,
        repo_stars: int,
        repo_forks: int,
        *,
        weights: dict[str, float] | None = None
    ) -> float:

        # sanitize inputs
        pr = max(0, int(pr_count))
        commits = max(0.0, float(commits_per_pr))
        merge_days = max(0.0, float(avg_merge_time_days))
        stars = max(0, int(repo_stars))
        forks = max(0, int(repo_forks))

        # default weights emphasize PRs and commits slightly more for personal grading
        if weights is None:
            weights = {
                'pr': 0.3,
                'commits': 0.25,
                'merge_time': 0.25,
                'stars': 0.1,
                'forks': 0.1,
            }

        # normalize each metric to 0..1 (caps can be adjusted)
        pr_score = min(pr / 40.0, 1.0)
        commits_score = min(commits / 8.0, 1.0)
        merge_score = 1.0 - min(merge_days / 20.0, 1.0)  # faster merges are better
        stars_score = min(stars / 500.0, 1.0)
        forks_score = min(forks / 200.0, 1.0)

        total = (
            pr_score * weights.get('pr', 0.0)
            + commits_score * weights.get('commits', 0.0)
            + merge_score * weights.get('merge_time', 0.0)
            + stars_score * weights.get('stars', 0.0)
            + forks_score * weights.get('forks', 0.0)
        )

        return round(max(0.0, min(total, 1.0)) * 100, 2)

    @staticmethod
    def compute_pr_score(
        lines_added: int = 0,
        lines_removed: int = 0,
        files_changed: int = 0,
        commits: int = 0,
        merge_time_days: float = 0.0,
        *,
        weights: dict[str, float] | None = None
    ) -> float:

        # sanitize
        la = max(0, int(lines_added))
        lr = max(0, int(lines_removed))
        fc = max(0, int(files_changed))
        cm = max(0, int(commits))
        md = max(0.0, float(merge_time_days))

        if weights is None:
            weights = {
                'lines_added': 0.25,
                'lines_removed': 0.10,
                'files_changed': 0.20,
                'commits': 0.20,
                'merge_speed': 0.25,
            }

        # normalization caps (tunable)
        added_score = min(la / 200.0, 1.0)
        removed_score = min(lr / 100.0, 1.0)
        files_score = min(fc / 10.0, 1.0)
        commits_score = min(cm / 5.0, 1.0)
        merge_speed_score = 1.0 - min(md / 7.0, 1.0)

        total = (
            added_score * weights.get('lines_added', 0.0)
            + removed_score * weights.get('lines_removed', 0.0)
            + files_score * weights.get('files_changed', 0.0)
            + commits_score * weights.get('commits', 0.0)
            + merge_speed_score * weights.get('merge_speed', 0.0)
        )

        return round(max(0.0, min(total, 1.0)) * 100, 2)

    @staticmethod
    def aggregate_from_prs(
        pr_list: list[dict[str, Any]],
        *,
        per_pr_weights: dict[str, float] | None = None,
        aggregate_weights: dict[str, float] | None = None,
    ) -> dict[str, float]:
        """
        pr_list: list of dicts with keys matching compute_pr_score args.
        Returns dict: { 'avg_pr_score': float, 'repo_level_score': float, 'final_score': float }
        final_score combines average PR score and repo-level score (reuse compute_open_source_score).
        """
        if not pr_list:
            return {'avg_pr_score': 0.0, 'repo_level_score': 0.0, 'final_score': 0.0}

        pr_scores = []
        total_commits = 0
        total_merge_days = 0.0
        for pr in pr_list:
            sc = scoring_service.compute_pr_score(
                lines_added=pr.get('lines_added', 0),
                lines_removed=pr.get('lines_removed', 0),
                files_changed=pr.get('files_changed', 0),
                commits=pr.get('commits', 0),
                merge_time_days=pr.get('merge_time_days', 0.0),
                weights=per_pr_weights,
            )
            pr_scores.append(sc)
            total_commits += pr.get('commits', 0)
            total_merge_days += pr.get('merge_time_days', 0.0)

        avg_pr_score = sum(pr_scores) / len(pr_scores)
        avg_commits_per_pr = (total_commits / len(pr_list)) if pr_list else 0.0
        avg_merge_days = (total_merge_days / len(pr_list)) if pr_list else 0.0

        # compute repo-level score using existing function (keeps backward compatibility)
        # optional: sum or max depending on data
        repo_level_score = scoring_service.compute_open_source_score(
            pr_count=len(pr_list),
            commits_per_pr=avg_commits_per_pr,
            avg_merge_time_days=avg_merge_days,
            repo_stars=sum(
                pr.get('repo_stars', 0) for pr in pr_list
            ),
            repo_forks=sum(
                pr.get('repo_forks', 0) for pr in pr_list
            ),
        )

        # combine avg_pr_score and repo_level_score (tunable)
        if aggregate_weights is None:
            aggregate_weights = {'pr_avg': 0.7, 'repo': 0.3}

        final = (
            (avg_pr_score / 100.0)
            * aggregate_weights.get('pr_avg', 0.0)
            + (repo_level_score / 100.0)
            * aggregate_weights.get('repo', 0.0)
        )

        return {
            'avg_pr_score': round(avg_pr_score, 2),
            'repo_level_score': round(repo_level_score, 2),
            'final_score': round(max(0.0, min(final, 1.0)) * 100, 2),
        }
