import pytest
from codedevx.relationships import Evidence,EvidenceSource,Relationship,RelationType

def test_relationship_requires_evidence():
    with pytest.raises(ValueError):
        Relationship("w","p","a",RelationType.CALLS,"b",())

def test_code_evidence_is_verified():
    r=Relationship("w","p","a",RelationType.CALLS,"b",
        (Evidence(EvidenceSource.CODE_ANALYSIS,"repo:path:10"),))
    assert r.is_verified

def test_model_inference_requires_no_verified_claim():
    r=Relationship("w","p","a",RelationType.DEPENDS_ON,"b",
        (Evidence(EvidenceSource.MODEL_INFERENCE,"analysis"),),confidence=.6,requires_confirmation=True)
    assert not r.is_verified
