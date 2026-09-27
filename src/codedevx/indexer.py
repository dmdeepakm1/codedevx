from codedevx.analyzers.simple import SimpleCodeAnalyzer
from codedevx.git import head_sha, changed_files
from codedevx.storage.sql import repos_for_project,indexed_sha,set_indexed_sha,known_hash,set_hash
from codedevx.vector.qdrant_store import QdrantCodeStore

class ProjectIndexer:
    def __init__(self):
        self.analyzer=SimpleCodeAnalyzer()
        self.vector=QdrantCodeStore()

    def index_project(self, project_id: str) -> dict:
        result={"project":project_id,"repos":{}}
        for repo in repos_for_project(project_id):
            new_sha=head_sha(repo.path)
            old_sha=indexed_sha(project_id,repo.id)
            files=changed_files(repo.path,old_sha,new_sha)
            changed_chunks=[]
            for rel in files:
                for chunk in self.analyzer.analyze(repo,rel):
                    if known_hash(project_id,repo.id,chunk.stable_id) != chunk.content_hash:
                        changed_chunks.append(chunk)
            self.vector.upsert(changed_chunks)
            for chunk in changed_chunks:
                set_hash(project_id,repo.id,chunk.stable_id,chunk.content_hash)
            set_indexed_sha(project_id,repo.id,new_sha)
            result["repos"][repo.id]={"from_sha":old_sha,"to_sha":new_sha,"changed_files":len(files),"embedded_chunks":len(changed_chunks)}
        return result
