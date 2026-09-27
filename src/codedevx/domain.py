from dataclasses import dataclass, field
from enum import Enum

class RepoKind(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    SHARED = "shared"
    INFRA = "infra"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class Project:
    id: str

@dataclass(frozen=True)
class Repository:
    project_id: str
    id: str
    path: str
    kind: RepoKind

@dataclass(frozen=True)
class CodeChunk:
    project_id: str
    repo_id: str
    relative_path: str
    language: str
    symbol: str
    content: str
    content_hash: str
    start_line: int
    end_line: int

    @property
    def stable_id(self) -> str:
        return f"{self.project_id}:{self.repo_id}:{self.relative_path}:{self.symbol}:{self.start_line}"

@dataclass(frozen=True)
class Edge:
    project_id: str
    source: str
    relation: str
    target: str
    metadata: dict = field(default_factory=dict)
