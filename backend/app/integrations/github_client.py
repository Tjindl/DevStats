from datetime import datetime, timedelta
from typing import Any

import httpx
from app.core.config import settings


class GithubClient:
    """Thin wrapper around GitHub's REST API."""

    api_base = "https://api.github.com"
    oauth_base = "https://github.com/login/oauth"

    def __init__(self, token: str | None = None):
        self._token = token

    @staticmethod
    async def exchange_code_for_token(code: str) -> str:
        """Exchange OAuth code for a GitHub access token."""
        if not settings.github_client_id or not settings.github_client_secret:
            raise RuntimeError("GitHub OAuth client settings are missing.")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GithubClient.oauth_base}/access_token",
                data={
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"},
                timeout=20.0,
            )
            resp.raise_for_status()
            payload = resp.json()
            if "error" in payload:
                raise RuntimeError(
                    payload.get("error_description") or "OAuth error")
            return str(payload["access_token"])

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "DevStats",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    async def get_user(self) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_base}/user",
                                    headers=self._headers(),
                                    timeout=20.0)
            resp.raise_for_status()
            return dict(resp.json())

    async def fetch_recent_pull_requests(
        self,
        username: str,
        days: int = 30,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Fetch recent pull requests for a user using search + detail calls.
        """
        since_date = (datetime.utcnow() -
                      timedelta(days=days)).date().isoformat()
        query = f"is:pr author:{username} created:>={since_date}"
        per_page = min(max(limit, 1), 30)

        async with httpx.AsyncClient() as client:
            search_resp = await client.get(
                f"{self.api_base}/search/issues",
                headers=self._headers(),
                params={
                    "q": query,
                    "per_page": per_page,
                    "sort": "updated",
                    "order": "desc",
                },
                timeout=30.0,
            )
            search_resp.raise_for_status()
            items = search_resp.json().get("items", [])[:limit]

        detail_prs: list[dict[str, Any]] = []
        async with httpx.AsyncClient() as client:
            for item in items:
                pr_url = item.get("pull_request", {}).get("url")
                if not pr_url:
                    continue
                pr_resp = await client.get(pr_url,
                                           headers=self._headers(),
                                           timeout=20.0)
                if pr_resp.status_code != 200:
                    continue
                detail_prs.append(pr_resp.json())

        return detail_prs
