from mcp.server.mcpserver import MCPServer
from codedevx.retrieval.hybrid import HybridRetriever

mcp=MCPServer("CodeDevX")

@mcp.tool()
def search_engineering_knowledge(project_id:str,query:str,limit:int=12)->dict:
    """Search project-scoped code and engineering knowledge."""
    return HybridRetriever().retrieve(project_id,query,limit)

def main():
    mcp.run()

if __name__=="__main__":
    main()
