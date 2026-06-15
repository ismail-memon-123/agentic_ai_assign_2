from datetime import datetime
from pathlib import Path

ROOT = Path('/opt/memory')
ROOT.mkdir(parents=True, exist_ok=True)

def write_mem(session_id: str, role: str, content: str) -> None:
    p = ROOT / f"{session_id}.md"
    with p.open('a', encoding='utf-8') as f:
        f.write(f"[{datetime.utcnow().isoformat()}] {role} {content}")

def read_mem(session_id: str) -> str:
    p = ROOT / f"{session_id}.md"
    return p.read_text(encoding='utf-8') if p.exists() else ''