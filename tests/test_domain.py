from codedevx.domain import CodeChunk

def test_stable_id_is_project_and_repo_scoped():
    c = CodeChunk(
        project_id="p1", repo_id="r1", relative_path="a.py",
        language="python", symbol="hello", content="def hello(): pass",
        content_hash="x", start_line=1, end_line=1
    )
    assert c.stable_id == "p1:r1:a.py:hello:1"
