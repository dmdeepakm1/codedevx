from codedevx.design import DesignStage,_STAGE_INSTRUCTIONS

def test_v1_design_stages_are_explicit():
    assert set(DesignStage)=={
        DesignStage.CURRENT_ARCHITECTURE,DesignStage.IMPACT,DesignStage.HLD,
        DesignStage.LLD,DesignStage.PLAN,
    }

def test_design_stages_preserve_human_gate():
    assert "APPROVAL REQUIRED" in _STAGE_INSTRUCTIONS[DesignStage.HLD]
    assert "APPROVAL REQUIRED" in _STAGE_INSTRUCTIONS[DesignStage.LLD]
    assert "APPROVAL REQUIRED" in _STAGE_INSTRUCTIONS[DesignStage.PLAN]
