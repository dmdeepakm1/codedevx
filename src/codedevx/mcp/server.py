from mcp.server.mcpserver import MCPServer
from codedevx.retrieval.hybrid import HybridRetriever
from codedevx.aidlc.context import AIDLCContextRequest,AIDLCContextService

mcp=MCPServer("CodeDevX")

@mcp.tool()
def search_engineering_knowledge(project_id:str,query:str,limit:int=12)->dict:
    """Search project-scoped code and engineering knowledge."""
    return HybridRetriever().retrieve(project_id,query,limit)

@mcp.tool()
def get_aidlc_context(project_id:str,stage:str,requirement:str,limit:int=12)->dict:
    """Return grounded engineering evidence for an external AI-DLC stage.

    This tool does not approve stages, answer clarification questions on behalf
    of a user, or mutate the AI-DLC specification.
    """
    return AIDLCContextService().build(
        AIDLCContextRequest(project_id=project_id,stage=stage,requirement=requirement,limit=limit)
    )

def main():
    mcp.run()

if __name__=="__main__":
    main()
