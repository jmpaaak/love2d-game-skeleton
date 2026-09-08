#!/usr/bin/env python3
"""Verify the binding Asset Studio workflow documentation contract."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/ASSET_PIPELINE.md"
PROMPT = ROOT / "loop/PROMPT.md"
WORKFLOW_NAME = "사진 기반 Asset Studio 고품질 픽셀 변환"
REQUIRED_STAGES = (
    "licensed/owned or provenance-recorded real photo reference",
    "Asset Studio high-quality image-to-image pixel reinterpretation",
    "background removal",
    "resize to runtime target cell",
    "limited palette quantization",
    "transparent alpha/alignment/nearest-neighbor and actual-scale QA",
)
REQUIRED_POLICY = (
    "This is a workflow name, not a PixelPerfect engine.",
    "baseline for all newly photo-derived raster asset generation",
    "Provider-specific or legacy automation policy must not block this approved Asset Studio workflow.",
    "Purchased/licensed existing assets remain the first priority.",
    "reuse-compatible license",
    "URL, author, license, and hash provenance",
    "No unlicensed search-result copying.",
    "Project-specific identity/source rules are stricter overrides",
)


def missing_phrases(path: Path, phrases: tuple[str, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [phrase for phrase in phrases if phrase not in text]


def main() -> int:
    doc_text = DOC.read_text(encoding="utf-8")
    missing_doc = missing_phrases(DOC, (WORKFLOW_NAME, *REQUIRED_STAGES, *REQUIRED_POLICY))
    missing_prompt = missing_phrases(PROMPT, ("docs/ASSET_PIPELINE.md", WORKFLOW_NAME))
    stage_positions = [doc_text.find(stage) for stage in REQUIRED_STAGES]
    invalid_stage_order = -1 not in stage_positions and stage_positions != sorted(stage_positions)
    if not missing_doc and not missing_prompt and not invalid_stage_order:
        print("asset pipeline source contract: PASS")
        return 0
    for path, missing in ((DOC, missing_doc), (PROMPT, missing_prompt)):
        for phrase in missing:
            print(f"{path.relative_to(ROOT)}: missing required phrase: {phrase}", file=sys.stderr)
    if invalid_stage_order:
        print("docs/ASSET_PIPELINE.md: canonical stages are out of order", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
