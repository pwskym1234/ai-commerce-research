#!/usr/bin/env python3
"""Auto-log git commits to Notion Work Log DB.

두 가지 호출 모드 지원:

1. Claude Code PostToolUse hook으로 호출되면 stdin에 hook JSON이 들어옴.
   `git commit` 명령일 때만 실행하고, cwd로 이동한 뒤 최신 commit을 적층.
2. 수동 호출(`python3 scripts/notion_log_commit.py`)이면 무조건 현재 디렉토리의
   최신 commit을 적층.

같은 commit hash는 절대 두 번 안 올라감 (.claude/.notion_logged_commits.txt).
commit 메시지에 [skip-notion] 들어 있으면 무시.
어떤 실패든 stderr만 찍고 0으로 종료 — 에이전트 흐름 절대 안 막음.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def load_env(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


def git(args: list[str], cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def parse_hook_stdin() -> tuple[str | None, str | None]:
    """Hook JSON이 들어왔으면 (command, cwd) 반환, 아니면 (None, None)."""
    if sys.stdin.isatty():
        return None, None
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return None, None
    if not isinstance(data, dict):
        return None, None
    cmd = data.get("tool_input", {}).get("command", "")
    cwd = data.get("cwd", "")
    return cmd or None, cwd or None


def is_git_commit(cmd: str) -> bool:
    return bool(re.search(r"\bgit\s+commit\b", cmd))


def infer_category(files: list[str]) -> str:
    s = "\n".join(files)
    if re.search(r"(^|/)stats/", s, re.M):
        return "산공통"
    if re.search(r"(^|/)ml/", s, re.M):
        return "데마"
    if re.search(r"(^|/)consulting/", s, re.M):
        return "컨설팅"
    return "공통/인프라"


def commit_url_from_remote(remote_url: str, sha: str) -> str | None:
    m = re.search(r"github\.com[:/](.+?)(\.git)?$", remote_url)
    if not m:
        return None
    return f"https://github.com/{m.group(1)}/commit/{sha}"


def get_schema(db_id: str, headers: dict) -> dict:
    r = requests.get(f"{NOTION_API}/databases/{db_id}", headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()["properties"]


def find_prop(schema: dict, candidates: list[str], type_: str) -> str | None:
    for name, info in schema.items():
        if info["type"] == type_ and any(c in name for c in candidates):
            return name
    return None


def find_title(schema: dict) -> str:
    for name, info in schema.items():
        if info["type"] == "title":
            return name
    raise RuntimeError("No title property in schema")


def build_payload(
    db_id: str,
    schema: dict,
    *,
    sha: str,
    subject: str,
    body: str,
    date_iso: str,
    files: list[str],
    category: str,
    commit_url: str | None,
) -> dict:
    props: dict = {}

    props[find_title(schema)] = {"title": [{"text": {"content": subject[:200]}}]}

    if name := find_prop(schema, ["날짜", "Date"], "date"):
        props[name] = {"date": {"start": date_iso}}

    if name := find_prop(schema, ["카테고리", "Category"], "multi_select"):
        props[name] = {"multi_select": [{"name": category}]}
    elif name := find_prop(schema, ["카테고리", "Category"], "select"):
        props[name] = {"select": {"name": category}}

    if name := find_prop(schema, ["요약", "Summary"], "rich_text"):
        text = (body.strip() or subject)[:1900]
        props[name] = {"rich_text": [{"text": {"content": text}}]}

    if name := find_prop(schema, ["변경 파일", "변경파일", "Files"], "rich_text"):
        text = "\n".join(files[:50])[:1900]
        props[name] = {"rich_text": [{"text": {"content": text}}]}

    if commit_url:
        if name := find_prop(schema, ["commit", "URL"], "url"):
            props[name] = {"url": commit_url}

    if name := find_prop(schema, ["상태", "Status"], "status"):
        props[name] = {"status": {"name": "Done"}}
    elif name := find_prop(schema, ["상태", "Status"], "select"):
        props[name] = {"select": {"name": "Done"}}

    return {"parent": {"database_id": db_id}, "properties": props}


def log(msg: str) -> None:
    print(f"[notion-log] {msg}", file=sys.stderr)


def main() -> int:
    cmd, hook_cwd = parse_hook_stdin()

    if cmd is not None and not is_git_commit(cmd):
        return 0

    cwd = Path(hook_cwd) if hook_cwd else Path.cwd()
    if not (cwd / ".git").exists():
        for parent in cwd.parents:
            if (parent / ".git").exists():
                cwd = parent
                break
        else:
            return 0

    load_env(cwd / ".env")

    api_key = os.environ.get("NOTION_API_KEY")
    db_id = os.environ.get("NOTION_WORK_DB_ID")
    if not api_key or not db_id:
        log("NOTION_API_KEY 또는 NOTION_WORK_DB_ID 없음 — skip")
        return 0

    try:
        sha = git(["rev-parse", "HEAD"], cwd)
        subject = git(["log", "-1", "--pretty=%s"], cwd)
        body = git(["log", "-1", "--pretty=%b"], cwd)
        date_iso = git(["log", "-1", "--pretty=%aI"], cwd)
        files = git(["diff-tree", "--no-commit-id", "--name-only", "-r", sha], cwd).splitlines()
        try:
            remote = git(["remote", "get-url", "origin"], cwd)
        except subprocess.CalledProcessError:
            remote = ""
    except subprocess.CalledProcessError as e:
        log(f"git 실패: {e}")
        return 0

    if "[skip-notion]" in (subject + body):
        log(f"[skip-notion] 마커: {sha[:8]}")
        return 0

    log_path = cwd / ".claude" / ".notion_logged_commits.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists() and sha in log_path.read_text().splitlines():
        log(f"이미 적층됨: {sha[:8]}")
        return 0

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

    try:
        schema = get_schema(db_id, headers)
    except requests.RequestException as e:
        log(f"schema fetch 실패: {e}")
        return 0

    payload = build_payload(
        db_id,
        schema,
        sha=sha,
        subject=subject,
        body=body,
        date_iso=date_iso,
        files=files,
        category=infer_category(files),
        commit_url=commit_url_from_remote(remote, sha) if remote else None,
    )

    try:
        r = requests.post(f"{NOTION_API}/pages", headers=headers, json=payload, timeout=30)
    except requests.RequestException as e:
        log(f"notion POST 실패: {e}")
        return 0

    if r.status_code >= 300:
        log(f"notion error {r.status_code}: {r.text[:300]}")
        return 0

    with log_path.open("a") as f:
        f.write(sha + "\n")
    log(f"✓ Work Log 적층: {sha[:8]} {subject[:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
