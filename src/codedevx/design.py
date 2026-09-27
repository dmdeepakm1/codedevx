from enum import Enum
from codedevx.agent import EngineeringAgent

class DesignStage(str, Enum):
    CURRENT_ARCHITECTURE="current-architecture"
    IMPACT="impact"
    HLD="hld"
    LLD="lld"
    PLAN="plan"

_STAGE_INSTRUCTIONS={
    DesignStage.CURRENT_ARCHITECTURE:"""Reverse engineer the current architecture relevant to the requirement.
Describe repositories, modules, APIs, data flows and tests only when supported by evidence.
Separate VERIFIED EVIDENCE, INFERENCE and MISSING INFORMATION. Do not propose changes yet.""",
    DesignStage.IMPACT:"""Analyze the requirement's likely impact on the current system.
Identify affected repositories, modules, APIs, data, tests, dependencies and risks.
Separate VERIFIED EVIDENCE, INFERENCE and QUESTIONS/UNKNOWNs.""",
    DesignStage.HLD:"""Prepare a CANDIDATE HLD for human review.
Include context, current architecture, proposed architecture, affected components,
APIs/events/data, dependencies, risks, alternatives and rollout considerations.
Clearly label current-state evidence versus proposed design. End with APPROVAL REQUIRED.""",
    DesignStage.LLD:"""Prepare a CANDIDATE LLD for human review.
List affected repositories, modules/classes/functions where evidenced, interfaces,
API/data changes, validation/error handling, configuration, observability and tests.
Do not invent existing symbols. Mark uncertain details. End with APPROVAL REQUIRED.""",
    DesignStage.PLAN:"""Prepare an implementation plan grouped by repository from the approved design supplied below.
Do not modify code. Include ordered changes, tests, validation and rollback/compatibility checks.
End with APPROVAL REQUIRED BEFORE CODE CHANGES.""",
}

class DesignAssistant:
    def __init__(self):
        self.agent=EngineeringAgent()

    def run(self,project_id:str,stage:DesignStage,requirement:str,approved_context:str="",provider:str="openai")->str:
        prompt=f"""TASK STAGE: {stage.value}

REQUIREMENT:
{requirement}

APPROVED PRIOR ARTIFACTS / USER DECISIONS:
{approved_context or "[none supplied]"}

INSTRUCTIONS:
{_STAGE_INSTRUCTIONS[stage]}

This is a human-gated assisted workflow. Never claim that a previous artifact is approved unless it appears in APPROVED PRIOR ARTIFACTS / USER DECISIONS."""
        return self.agent.ask(project_id,prompt,provider)
