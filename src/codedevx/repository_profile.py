"""Cheap repository discovery and optional, validated Markdown spec hints."""
import re
from collections import Counter
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

from codedevx.analyzers.simple import IGNORE_PARTS, LANG
from codedevx.git import tracked_files

LANGUAGES = {"tsx": "typescript", "jsx": "javascript", **{v: v for v in LANG.values()}}
SOURCE_LANGUAGES = {"python", "java", "kotlin", "typescript", "javascript", "csharp", "go"}

@dataclass(frozen=True)
class RepositoryProfile:
    name: str
    languages: tuple[str, ...]
    frameworks: tuple[str, ...]
    build_tools: tuple[str, ...]
    exclude: tuple[str, ...]
    warnings: tuple[str, ...]

    def as_dict(self) -> dict:
        return {"name": self.name, "languages": list(self.languages),
                "frameworks": list(self.frameworks), "build_tools": list(self.build_tools),
                "exclude": list(self.exclude), "warnings": list(self.warnings)}


FIELDS = {"version", "name", "languages", "frameworks", "build tool", "exclude"}


def read_spec(root: Path) -> dict[str, str]:
    """Parse a small metadata section; prose outside it remains free-form."""
    spec_path = root / "codedevx.spec.md"
    if not spec_path.is_file():
        return {}
    content = spec_path.read_text(encoding="utf-8")
    match = re.search(r"(?mi)^## CodeDevX metadata\s*$", content)
    if not match:
        raise ValueError("codedevx.spec.md requires a '## CodeDevX metadata' section")
    section = re.split(r"(?m)^##?\s+", content[match.end():], maxsplit=1)[0]
    result = {}
    for line in section.splitlines():
        if not line.strip() or line.lstrip().startswith("<!--"):
            continue
        item = re.fullmatch(r"\s*-\s*([^:]+):\s*(.*?)\s*", line)
        if not item:
            raise ValueError(f"Invalid metadata line: {line}")
        key, value = item.group(1).strip().lower(), item.group(2).strip()
        if key not in FIELDS or key in result or not value:
            raise ValueError(f"Unknown, duplicate or empty CodeDevX metadata field: {key}")
        result[key] = value
    if result.get("version") != "1":
        raise ValueError("codedevx.spec.md requires '- Version: 1'")
    return result


def _list(value: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(part.strip() for part in value.split(",") if part.strip()))


def load_profile(path: str, name: str) -> RepositoryProfile:
    root = Path(path)
    spec = read_spec(root)
    excludes = _list(spec.get("exclude", ""))
    paths = [p for p in tracked_files(path) if not any(part in IGNORE_PARTS for part in Path(p).parts)
             and not any(fnmatch(p, pattern) or fnmatch(Path(p).name, pattern) for pattern in excludes)]
    counts = Counter(LANGUAGES[LANG[Path(p).suffix.lower()]] for p in paths
                     if Path(p).suffix.lower() in LANG and LANGUAGES[LANG[Path(p).suffix.lower()]] in SOURCE_LANGUAGES)
    detected = tuple(k for k, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0])))
    files = set(paths)
    build = []
    for file, tool in (("pom.xml", "maven"), ("build.gradle", "gradle"),
                       ("build.gradle.kts", "gradle"), ("package.json", "npm"),
                       ("pyproject.toml", "python-packaging"), ("go.mod", "go")):
        if file in files:
            build.append(tool)
    if any(p.endswith(".csproj") for p in files):
        build.append("dotnet")
    frameworks = []
    if "pom.xml" in files or "build.gradle" in files or "build.gradle.kts" in files:
        for file in ("pom.xml", "build.gradle", "build.gradle.kts"):
            if file in files and "spring-boot" in (root / file).read_text(encoding="utf-8", errors="replace")[:100_000].lower():
                frameworks.append("spring-boot")
                break
    if "package.json" in files:
        package = (root / "package.json").read_text(encoding="utf-8", errors="replace")[:100_000].lower()
        frameworks.extend(x for x in ("angular", "react", "next", "vue") if f'"@{x}/' in package or f'"{x}"' in package or (x == "next" and '"next"' in package))
    hints = _list(spec.get("languages", ""))
    framework_hints = _list(spec.get("frameworks", ""))
    build_hint = (spec["build tool"],) if "build tool" in spec else ()
    warnings = [f"Language hint {x!r} differs from detected languages {detected}" for x in hints if detected and x not in detected]
    warnings += [f"Build hint {x!r} differs from detected tools {tuple(build)}" for x in build_hint if build and x not in build]
    return RepositoryProfile(spec.get("name") or name, tuple(dict.fromkeys((*detected, *hints))),
                             tuple(dict.fromkeys((*frameworks, *framework_hints))),
                             tuple(dict.fromkeys((*build, *build_hint))), excludes, tuple(warnings))
