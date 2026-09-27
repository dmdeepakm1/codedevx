"""Cheap repository discovery and optional, validated codedevx.yaml hints."""
from collections import Counter
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

import yaml

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


def _strings(value, label: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        raise ValueError(f"{label} must be a list of nonempty strings")
    return tuple(dict.fromkeys(value))


def load_profile(path: str, name: str) -> RepositoryProfile:
    root = Path(path)
    spec_path = root / "codedevx.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8")) if spec_path.is_file() else {}
    if not isinstance(spec, dict) or spec.get("version", 1) != 1:
        raise ValueError("codedevx.yaml must be a mapping with version: 1")
    technology = spec.get("technology", {})
    analysis = spec.get("analysis", {})
    repository = spec.get("repository", {})
    if any(not isinstance(x, dict) for x in (technology, analysis, repository)):
        raise ValueError("repository, technology and analysis must be mappings")
    excludes = _strings(analysis.get("exclude"), "analysis.exclude")
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
    hints = _strings(technology.get("languages"), "technology.languages")
    framework_hints = _strings(technology.get("frameworks"), "technology.frameworks")
    build_spec = technology.get("build", {})
    if not isinstance(build_spec, dict) or ("tool" in build_spec and not isinstance(build_spec["tool"], str)):
        raise ValueError("technology.build.tool must be a string")
    build_hint = (build_spec["tool"],) if build_spec.get("tool") else ()
    warnings = [f"Language hint {x!r} differs from detected languages {detected}" for x in hints if detected and x not in detected]
    warnings += [f"Build hint {x!r} differs from detected tools {tuple(build)}" for x in build_hint if build and x not in build]
    return RepositoryProfile(repository.get("name") or name, tuple(dict.fromkeys((*detected, *hints))),
                             tuple(dict.fromkeys((*frameworks, *framework_hints))),
                             tuple(dict.fromkeys((*build, *build_hint))), excludes, tuple(warnings))
