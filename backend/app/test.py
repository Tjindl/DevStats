from backend.app.integrations.github import GitHubService


async def main():
    g = GitHubService()
    user_repos = g.get_user_pr_in_forked_repos("gavi04")
    print(user_repos)
    # pr_info = g.get_pr_info_for_repo("gavi04/DevStats", 1)
    # print(pr_info)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
