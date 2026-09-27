from dataclasses import dataclass
import hashlib

@dataclass(frozen=True)
class KnowledgeChunk:
    project_id:str
    source:str
    source_id:str
    title:str
    content:str
    url:str=""
    updated_at:str=""

    @property
    def stable_id(self)->str:
        return hashlib.sha256(f"{self.project_id}:{self.source}:{self.source_id}:{self.title}".encode()).hexdigest()
