import subprocess

import pytest

from codedevx.context import ContextBudget, estimate_tokens, evidence_context
from codedevx.repository_profile import load_profile


def test_detects_repo_and_flags_incorrect_hints(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "pom.xml").write_text("<dependency>spring-boot-starter-web</dependency>")
    (tmp_path / "Service.java").write_text("class Service {}")
    (tmp_path / "codedevx.yaml").write_text("version: 1\ntechnology:\n  languages: [python]\n  build:\n    tool: gradle\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)
    profile = load_profile(str(tmp_path), "service")
    assert profile.languages == ("java", "python")
    assert profile.frameworks == ("spring-boot",)
    assert profile.build_tools == ("maven", "gradle")
    assert len(profile.warnings) == 2


def test_invalid_spec_is_rejected(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "codedevx.yaml").write_text("version: 2")
    with pytest.raises(ValueError):
        load_profile(str(tmp_path), "repo")


def test_context_ranks_and_caps_evidence():
    hits = [{"score": score, "repo_id": "r", "path": f"a{i}.java", "start_line": 1,
             "end_line": 40, "symbol": "A", "language": "java", "content": "line of code here\n" * 40}
            for i, score in enumerate((0.1, 0.9, 0.5))]
    result = evidence_context(hits, [], [], ContextBudget(max_tokens=200, source_code=160), reserved_tokens=30)
    assert estimate_tokens(result) <= 170
    assert result.index("a1.java") < result.index("a2.java") if "a2.java" in result else "a1.java" in result
