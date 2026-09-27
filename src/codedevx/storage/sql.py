import json

from sqlalchemy import String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from codedevx.config import settings
from codedevx.domain import RepoKind, Repository


class Base(DeclarativeBase):
    pass

class ProjectRow(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(200), primary_key=True)

class RepositoryRow(Base):
    __tablename__ = "repositories"
    project_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    id: Mapped[str] = mapped_column(String(200), primary_key=True)
    path: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(30))
    indexed_sha: Mapped[str | None] = mapped_column(String(80), nullable=True)

class RepositoryProfileRow(Base):
    __tablename__ = "repository_profiles"
    project_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    repo_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    profile_json: Mapped[str] = mapped_column(Text)

class ChunkStateRow(Base):
    __tablename__ = "chunk_state"
    project_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    repo_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    stable_id: Mapped[str] = mapped_column(Text, primary_key=True)
    content_hash: Mapped[str] = mapped_column(String(64))

engine = create_engine(settings.postgres_url)

def init_db():
    Base.metadata.create_all(engine)

def add_project(project_id: str):
    init_db()
    with Session(engine) as s:
        if not s.get(ProjectRow, project_id):
            s.add(ProjectRow(id=project_id))
            s.commit()

def add_repo(repo: Repository):
    init_db()
    with Session(engine) as s:
        row = s.get(RepositoryRow, (repo.project_id, repo.id))
        if row:
            row.path, row.kind = repo.path, repo.kind.value
        else:
            s.add(RepositoryRow(project_id=repo.project_id, id=repo.id, path=repo.path, kind=repo.kind.value))
        s.commit()

def repos_for_project(project_id: str) -> list[Repository]:
    init_db()
    with Session(engine) as s:
        rows = s.query(RepositoryRow).filter_by(project_id=project_id).all()
        return [Repository(r.project_id, r.id, r.path, RepoKind(r.kind)) for r in rows]

def indexed_sha(project_id: str, repo_id: str) -> str | None:
    with Session(engine) as s:
        row = s.get(RepositoryRow, (project_id, repo_id))
        return row.indexed_sha if row else None

def set_indexed_sha(project_id: str, repo_id: str, sha: str):
    with Session(engine) as s:
        row = s.get(RepositoryRow, (project_id, repo_id))
        if row:
            row.indexed_sha = sha
            s.commit()

def known_hash(project_id: str, repo_id: str, stable_id: str) -> str | None:
    with Session(engine) as s:
        row = s.get(ChunkStateRow, (project_id, repo_id, stable_id))
        return row.content_hash if row else None

def set_hash(project_id: str, repo_id: str, stable_id: str, content_hash: str):
    with Session(engine) as s:
        row = s.get(ChunkStateRow, (project_id, repo_id, stable_id))
        if row:
            row.content_hash = content_hash
        else:
            s.add(ChunkStateRow(project_id=project_id, repo_id=repo_id, stable_id=stable_id, content_hash=content_hash))
        s.commit()

def set_repository_profile(project_id: str, repo_id: str, profile: dict):
    init_db()
    with Session(engine) as session:
        row = session.get(RepositoryProfileRow, (project_id, repo_id))
        if row is None:
            row = RepositoryProfileRow(project_id=project_id, repo_id=repo_id)
            session.add(row)
        row.profile_json = json.dumps(profile)
        session.commit()

def profiles_for_project(project_id: str) -> list[dict]:
    init_db()
    with Session(engine) as session:
        return [json.loads(row.profile_json) for row in session.query(RepositoryProfileRow).filter_by(project_id=project_id).all()]
