from pathlib import Path
from codedevx.knowledge.models import KnowledgeChunk

def load_markdown(project_id:str,path:str)->list[KnowledgeChunk]:
    p=Path(path)
    files=[p] if p.is_file() else list(p.rglob("*.md"))
    out=[]
    for f in files:
        text=f.read_text(encoding="utf-8")
        sections=[s.strip() for s in text.split("\n#") if s.strip()]
        for i,s in enumerate(sections):
            out.append(KnowledgeChunk(project_id,"markdown",str(f),f.name+f"#{i}",s))
    return out
