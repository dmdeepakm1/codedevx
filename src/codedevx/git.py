from pathlib import Path
import subprocess

def _git(path: str, *args: str) -> str:
    return subprocess.check_output(["git", "-C", path, *args], text=True, stderr=subprocess.DEVNULL).strip()

def head_sha(path: str) -> str:
    return _git(path, "rev-parse", "HEAD")

def tracked_files(path: str) -> list[str]:
    out = _git(path, "ls-files")
    return [x for x in out.splitlines() if x]

def changed_files(path: str, old_sha: str | None, new_sha: str) -> list[str]:
    if not old_sha:
        return tracked_files(path)
    out = _git(path, "diff", "--name-only", f"{old_sha}..{new_sha}")
    return [x for x in out.splitlines() if x and (Path(path) / x).exists()]
