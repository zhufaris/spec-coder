"""Read-only Git and filesystem observations for a baseline command."""
import hashlib
import os
from pathlib import Path
import stat
import subprocess

from .evidence import is_active_artifact


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    ).stdout


def snapshot(repo, cwd, exclusions):
    """Observe content and index independently; uncertainty is carried as reasons."""
    reasons = []
    result = {"repo": str(repo), "cwd": str(cwd)}
    try:
        for name, location in [("repo_identity", repo), ("cwd_identity", cwd)]:
            info = location.stat()
            result[name] = [info.st_dev, info.st_ino]
        gitdir = Path(os.fsdecode(git(repo, "rev-parse", "--absolute-git-dir")).strip()).resolve()
        info = gitdir.stat()
        result["git_identity"] = [str(gitdir), info.st_dev, info.st_ino]
        result["head"] = git(repo, "rev-parse", "HEAD").decode().strip()
        index = git(repo, "ls-files", "--stage", "-z")
        result["index"] = digest(index + git(repo, "ls-files", "-v", "-z"))
        submodules = set()
        for entry in index.split(b"\0"):
            if entry.startswith(b"160000 "):
                name = os.fsdecode(entry.split(b"\t", 1)[1])
                submodules.add(name)
                reasons.append("submodule state cannot be confirmed: " + name)
        tracked = git(repo, "ls-files", "-z").split(b"\0")
        untracked = git(repo, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
        result["files"] = {}
        for raw in sorted(set(tracked + untracked) - {b""}):
            name = os.fsdecode(raw)
            path = repo / name
            if str(path) in exclusions or name in submodules:
                continue
            try:
                path.parent.resolve(strict=False).relative_to(repo)
                info = path.lstat()
                if stat.S_ISREG(info.st_mode):
                    value = {"mode": stat.S_IMODE(info.st_mode), "content": digest(path.read_bytes())}
                elif stat.S_ISLNK(info.st_mode):
                    target = path.resolve(strict=True)
                    target.relative_to(repo)
                    if not target.is_file():
                        raise ValueError("symlink target is not a regular file")
                    value = {"mode": stat.S_IMODE(info.st_mode), "link": os.readlink(path), "target": str(target), "target_mode": stat.S_IMODE(target.stat().st_mode), "content": digest(target.read_bytes())}
                else:
                    raise ValueError("unsupported file or submodule")
                result["files"][name] = value
            except FileNotFoundError:
                if path.is_symlink():
                    reasons.append("unresolved symlink: " + name)
                else:
                    result["files"][name] = {"missing": True}
            except (OSError, RuntimeError, ValueError) as error:
                reasons.append("unreadable or unresolved input " + name + ": " + str(error))
    except (OSError, subprocess.CalledProcessError) as error:
        reasons.append("workspace observation unavailable: " + str(error))
    return {"inputs": result, "uncertainty": reasons}


def paths(repo_arg, cwd_arg, artifact_arg, output_args):
    repo = Path(repo_arg).resolve(strict=True)
    cwd = Path(cwd_arg).resolve(strict=True)
    cwd.relative_to(repo)
    if Path(os.fsdecode(git(repo, "rev-parse", "--show-toplevel")).strip()).resolve() != repo:
        raise ValueError("--repo must be the physical Git worktree root")
    tracked = set(git(repo, "ls-files", "-z").split(b"\0"))
    exclusions = []
    for index, argument in enumerate([artifact_arg, *output_args]):
        candidate = Path(argument)
        if not candidate.is_absolute():
            candidate = repo / candidate
        if any(part in {"..", ".git"} or any(c in part for c in "*?[]") for part in candidate.parts):
            raise ValueError("exclusions must be exact paths outside .git, without globs or traversal")
        candidate.relative_to(repo)
        if candidate.is_symlink() or candidate.is_dir() or candidate.parent.resolve() != candidate.parent:
            raise ValueError("exclusions must be exact files without symlink parents")
        if index == 0 and candidate.suffix.lower() != ".md":
            raise ValueError("--artifact must be the active Markdown file")
        is_tracked = os.fsencode(str(candidate.relative_to(repo))) in tracked
        if index == 0 and is_tracked and not is_active_artifact(candidate.read_text(encoding="utf-8")):
            raise ValueError("tracked artifact requires an explicit artifact-v1 spec or plan marker")
        if index and is_tracked:
            raise ValueError("output exclusions cannot hide tracked files")
        exclusions.append(str(candidate))
    return repo, cwd, exclusions
