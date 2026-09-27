"""Ranked evidence selection with a conservative, provider-neutral token estimate."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ContextBudget:
    max_tokens: int = 20000
    requirement: int = 1000
    architecture: int = 3000
    source_code: int = 10000
    dependencies: int = 3000
    tests: int = 3000

    def __post_init__(self):
        if self.max_tokens <= 0 or any(getattr(self, key) < 0 for key in ("requirement", "architecture", "source_code", "dependencies", "tests")):
            raise ValueError("Context budgets must be positive/nonnegative")


def estimate_tokens(value: str) -> int:
    # Conservative approximation; provider tokenizers differ.
    return (len(value.encode("utf-8")) + 2) // 3


def evidence_context(hits: list[dict], graph: list, profiles: list[dict], budget: ContextBudget,
                     reserved_tokens: int = 0) -> str:
    remaining = max(0, budget.max_tokens - reserved_tokens)
    categories = {"architecture": budget.architecture, "source_code": budget.source_code,
                  "dependencies": budget.dependencies, "tests": budget.tests}
    sections = []
    separator_cost = estimate_tokens("\n\n---\n\n")
    profile_text = "REPOSITORY PROFILES (discovery and optional hints):\n" + "\n".join(str(p) for p in profiles)
    if profiles and estimate_tokens(profile_text) + (separator_cost if sections else 0) <= remaining:
        sections.append(profile_text)
        remaining -= estimate_tokens(profile_text) + (separator_cost if len(sections) > 1 else 0)
    graph_text = "GRAPH EVIDENCE:\n" + str(graph)
    if graph and estimate_tokens(graph_text) + (separator_cost if sections else 0) <= min(remaining, categories["dependencies"]):
        sections.append(graph_text)
        remaining -= estimate_tokens(graph_text) + (separator_cost if len(sections) > 1 else 0)
        categories["dependencies"] -= estimate_tokens(graph_text)
    seen = set()
    for h in sorted(hits, key=lambda h: h.get("score", 0), reverse=True):
        key = (h.get("repo_id"), h.get("path"), h.get("start_line"))
        if key in seen:
            continue
        seen.add(key)
        path = str(h.get("path", ""))
        language = h.get("language")
        category = ("architecture" if language in ("markdown", "knowledge") else
                    "tests" if "test" in path.lower() or "spec" in path.lower() else "source_code")
        content = str(h.get("content", ""))
        prefix = (f"SOURCE: {h.get('repo_id')}\nPATH: {path}:{h.get('start_line')}-{h.get('end_line')}\n"
                  f"SYMBOL/TITLE: {h.get('symbol')}\nCONTENT:\n")
        allowance = min(remaining, categories[category]) - (separator_cost if sections else 0)
        if estimate_tokens(prefix) >= allowance:
            continue
        # Include whole lines, retaining the citation and most relevant beginning of the chunk.
        selected = ""
        for line in content.splitlines(keepends=True):
            if estimate_tokens(prefix + selected + line) > allowance:
                break
            selected += line
        if not selected.strip():
            continue
        section = prefix + selected.rstrip()
        sections.append(section)
        spent = estimate_tokens(section)
        remaining -= spent + (separator_cost if len(sections) > 1 else 0)
        categories[category] -= spent
    return "\n\n---\n\n".join(sections) or "[none]"
