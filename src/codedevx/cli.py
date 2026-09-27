import json
from pathlib import Path
import typer
from codedevx.domain import Repository, RepoKind
from codedevx.storage.sql import add_project, add_repo, init_db
from codedevx.indexer import ProjectIndexer
from codedevx.agent import EngineeringAgent
from codedevx.knowledge.markdown import load_markdown
from codedevx.vector.qdrant_store import QdrantCodeStore
from codedevx.config import settings

app=typer.Typer(no_args_is_help=True)

@app.command("project-add")
def project_add(project_id: str):
    add_project(project_id)
    typer.echo(f"Project registered: {project_id}")

@app.command("repo-add")
def repo_add(project_id: str, repo_id: str, path: str, kind: RepoKind=RepoKind.UNKNOWN):
    p=Path(path).expanduser().resolve()
    if not (p/".git").exists():
        raise typer.BadParameter(f"{p} is not a Git repository")
    add_project(project_id)
    add_repo(Repository(project_id,repo_id,str(p),kind))
    typer.echo(f"Repository registered: {project_id}/{repo_id}")

@app.command("index")
def index(project_id: str):
    init_db()
    typer.echo(json.dumps(ProjectIndexer().index_project(project_id),indent=2))

@app.command("ask")
def ask(project_id: str, question: str, provider: str="openai"):
    typer.echo(EngineeringAgent().ask(project_id,question,provider))

if __name__ == "__main__":
    app()


@app.command("version")
def version():
    typer.echo(f"CodeDevX runtime profile: V{settings.version}")

@app.command("knowledge-add")
def knowledge_add(project_id: str, path: str):
    chunks=load_markdown(project_id,path)
    QdrantCodeStore().upsert_knowledge(chunks)
    typer.echo(f"Indexed {len(chunks)} knowledge chunks for {project_id}")
