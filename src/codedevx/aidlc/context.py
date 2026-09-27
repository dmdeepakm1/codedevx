from dataclasses import dataclass
from codedevx.retrieval.hybrid import HybridRetriever

@dataclass(frozen=True)
class AIDLCContextRequest:
    project_id: str
    stage: str
    requirement: str
    limit: int=12

class AIDLCContextService:
    """Evidence provider for an external AI-DLC workflow.

    AI-DLC owns questions, approvals, specs and lifecycle state.
    CodeDevX owns retrieval and engineering evidence.
    """
    def __init__(self):
        self.retriever=HybridRetriever()

    def build(self,request:AIDLCContextRequest)->dict:
        query=f"AI-DLC stage: {request.stage}\nRequirement: {request.requirement}"
        evidence=self.retriever.retrieve(request.project_id,query,request.limit)
        return {
            "project_id":request.project_id,
            "stage":request.stage,
            "requirement":request.requirement,
            "evidence":evidence,
            "workflow_control":{
                "owner":"external-aidlc",
                "questions_owned_by":"external-aidlc",
                "approval_gates_owned_by":"external-aidlc",
                "spec_state_owned_by":"external-aidlc",
            },
        }
