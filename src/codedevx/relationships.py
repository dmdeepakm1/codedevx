from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class RelationType(str, Enum):
    CONTAINS="CONTAINS"; IMPORTS="IMPORTS"; CALLS="CALLS"; IMPLEMENTS="IMPLEMENTS"
    EXTENDS="EXTENDS"; DEPENDS_ON="DEPENDS_ON"; EXPOSES_API="EXPOSES_API"
    CALLS_API="CALLS_API"; READS_FROM="READS_FROM"; WRITES_TO="WRITES_TO"
    PUBLISHES_EVENT="PUBLISHES_EVENT"; CONSUMES_EVENT="CONSUMES_EVENT"
    TESTED_BY="TESTED_BY"; DOCUMENTED_BY="DOCUMENTED_BY"
    RELATED_TO_WORK_ITEM="RELATED_TO_WORK_ITEM"; OWNED_BY="OWNED_BY"
    USED_BY="USED_BY"; IMPLEMENTS_REQUIREMENT="IMPLEMENTS_REQUIREMENT"
    BLOCKED_BY="BLOCKED_BY"; AFFECTS="AFFECTS"

class EvidenceSource(str, Enum):
    CODE_ANALYSIS="code_analysis"
    OPENAPI="openapi"
    DOCUMENTATION="documentation"
    WORK_ITEM="work_item"
    MCP="mcp"
    USER_CONFIRMED="user_confirmed"
    MODEL_INFERENCE="model_inference"

@dataclass(frozen=True)
class Evidence:
    source: EvidenceSource
    source_id: str
    uri: str=""
    revision: str=""
    excerpt: str=""
    metadata: dict[str,Any]=field(default_factory=dict)

@dataclass(frozen=True)
class Relationship:
    workspace_id: str
    project_area_id: str
    source_id: str
    relation: RelationType
    target_id: str
    evidence: tuple[Evidence,...]
    confidence: float=1.0
    requires_confirmation: bool=False

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if not self.evidence:
            raise ValueError("relationship requires evidence")

    @property
    def is_verified(self)->bool:
        trusted={EvidenceSource.CODE_ANALYSIS,EvidenceSource.OPENAPI,EvidenceSource.USER_CONFIRMED}
        return any(e.source in trusted for e in self.evidence) and not self.requires_confirmation
