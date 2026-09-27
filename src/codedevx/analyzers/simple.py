from pathlib import Path
import hashlib, re
from codedevx.domain import CodeChunk, Repository

LANG = {".py":"python",".java":"java",".kt":"kotlin",".ts":"typescript",".tsx":"tsx",".js":"javascript",".jsx":"jsx",".cs":"csharp",".go":"go",".sql":"sql",".yaml":"yaml",".yml":"yaml",".json":"json",".md":"markdown"}
IGNORE_PARTS = {".git","node_modules","dist","build","target",".venv","vendor"}
MAX_FILE_BYTES = 1_000_000
LINES_PER_CHUNK = 120

class SimpleCodeAnalyzer:
    """Deterministic cheap analyzer; replace/augment with Tree-sitter without changing callers."""
    def analyze(self, repo: Repository, relative_path: str) -> list[CodeChunk]:
        p = Path(repo.path) / relative_path
        if not p.exists() or p.suffix.lower() not in LANG:
            return []
        if any(part in IGNORE_PARTS for part in p.parts) or p.stat().st_size > MAX_FILE_BYTES:
            return []
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return []
        lines, chunks = text.splitlines(), []
        for i in range(0, len(lines), LINES_PER_CHUNK):
            block = "\n".join(lines[i:i+LINES_PER_CHUNK]).strip()
            if not block:
                continue
            symbol = self._symbol_hint(block) or p.name
            chunks.append(CodeChunk(repo.project_id, repo.id, relative_path, LANG[p.suffix.lower()], symbol, block, hashlib.sha256(block.encode()).hexdigest(), i+1, min(i+LINES_PER_CHUNK,len(lines))))
        return chunks

    def _symbol_hint(self, text: str) -> str | None:
        for pat in [r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)",r"\binterface\s+([A-Za-z_][A-Za-z0-9_]*)",r"\b(?:def|function)\s+([A-Za-z_][A-Za-z0-9_]*)",r"\b(?:const|export\s+const)\s+([A-Za-z_][A-Za-z0-9_]*)\s*="]:
            m = re.search(pat,text)
            if m:
                return m.group(1)
        return None
