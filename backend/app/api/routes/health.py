import shutil
import subprocess
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(tags=["Health"])

def get_git_commit_sha() -> str:
    repo_root = Path(__file__).resolve().parents[4]

    if git_bin := shutil.which("git"):
        try:
            result = subprocess.run(
                [git_bin, "describe", "--tags", "--always"],
                cwd=repo_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass

    try:
        git_path = repo_root / ".git"
        if git_path.is_file():
            git_dir = (repo_root / git_path.read_text().strip().split(":", 1)[1].strip()).resolve()
        else:
            git_dir = git_path

        head_file = git_dir / "HEAD"
        if head_file.exists():
            head_content = head_file.read_text().strip()
            if head_content.startswith("ref:"):
                ref = head_content.split(":", 1)[1].strip()
                ref_file = git_dir / ref
                if ref_file.exists():
                    return ref_file.read_text().strip()
                
                packed_refs = git_dir / "packed-refs"
                if packed_refs.exists():
                    for line in packed_refs.read_text().splitlines():
                        parts = line.split()
                        if len(parts) >= 2 and parts[1] == ref:
                            return parts[0]
            else:
                return head_content
    except Exception:
        pass

    return "unknown"

@router.get("/health")
async def health_check():
    return {
        "status": " DEVSTASTS RUNNING ",
        "commit_id": get_git_commit_sha()
    }
