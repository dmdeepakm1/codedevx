from neo4j import GraphDatabase
from codedevx.config import settings
from codedevx.domain import CodeChunk, Edge

class Neo4jGraphStore:
    def __init__(self):
        self.driver=GraphDatabase.driver(settings.neo4j_uri,auth=(settings.neo4j_user,settings.neo4j_password))

    def close(self):
        self.driver.close()

    def verify(self):
        self.driver.verify_connectivity()

    def upsert_chunk(self,c: CodeChunk):
        self.driver.execute_query("""
        MERGE (p:Project {id:$project})
        MERGE (r:Repository {project_id:$project,id:$repo})
        MERGE (n:CodeChunk {stable_id:$stable_id})
        SET n.path=$path,n.symbol=$symbol,n.language=$language,n.start_line=$start_line,n.end_line=$end_line,n.content_hash=$content_hash
        MERGE (p)-[:CONTAINS]->(r)
        MERGE (r)-[:CONTAINS]->(n)
        """,project=c.project_id,repo=c.repo_id,stable_id=c.stable_id,path=c.relative_path,symbol=c.symbol,language=c.language,start_line=c.start_line,end_line=c.end_line,content_hash=c.content_hash,database_=settings.neo4j_database)

    def upsert_edge(self,e: Edge):
        self.driver.execute_query("""
        MERGE (a:Entity {project_id:$project,id:$source})
        MERGE (b:Entity {project_id:$project,id:$target})
        MERGE (a)-[r:RELATED {kind:$relation}]->(b)
        SET r.metadata=$metadata
        """,project=e.project_id,source=e.source,target=e.target,relation=e.relation,metadata=e.metadata,database_=settings.neo4j_database)

    def neighbors(self,project_id:str,terms:list[str],limit:int=20)->list[dict]:
        records,_,_=self.driver.execute_query("""
        MATCH (n)
        WHERE (n.project_id=$project OR n.stable_id STARTS WITH $prefix)
          AND any(t IN $terms WHERE toLower(coalesce(n.id,n.symbol,n.path,'')) CONTAINS toLower(t))
        OPTIONAL MATCH (n)-[r]-(m)
        RETURN coalesce(n.id,n.stable_id) AS source,type(r) AS relation,
               coalesce(m.id,m.stable_id,m.symbol,m.path) AS target
        LIMIT $limit
        """,project=project_id,prefix=project_id+":",terms=terms,limit=limit,database_=settings.neo4j_database)
        return [x.data() for x in records]
