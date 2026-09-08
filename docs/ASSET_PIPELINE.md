# Autonomous final-asset generation & reporting (built in)

## Canonical workflow: 사진 기반 Asset Studio 고품질 픽셀 변환

`사진 기반 Asset Studio 고품질 픽셀 변환` is the official workflow name and
the baseline for all newly photo-derived raster asset generation in future
projects. This is a workflow name, not a PixelPerfect engine.
Provider-specific or legacy automation policy must not block this approved Asset Studio workflow.

Purchased/licensed existing assets remain the first priority. Use this workflow
only when an appropriate existing asset is unavailable. The canonical stages,
in order, are:

1. Select a licensed/owned or provenance-recorded real photo reference.
2. Perform an Asset Studio high-quality image-to-image pixel reinterpretation.
3. Apply background removal.
4. Perform resize to runtime target cell.
5. Apply limited palette quantization.
6. Complete transparent alpha/alignment/nearest-neighbor and actual-scale QA.

For any web photo, confirm a reuse-compatible license before use and record its
URL, author, license, and hash provenance. No unlicensed search-result copying.
For owned or uploaded references, record ownership/upload provenance and a hash.
Generated outputs must also retain workflow, prompt/settings, model, timestamp,
and output hash records in the project manifest.

Project-specific identity/source rules are stricter overrides and always win
when they narrow allowed sources, transformations, likeness handling, palette,
or runtime rendering. Do not weaken those rules to satisfy this baseline.


Any game generated from this skeleton that produces final visual
assets via an external service (SpriteCook, AetherAI, ComfyUI, etc.)
inside its autonomous dev loop should follow this pattern, established
2026-09-03 across `man-of-korea` and `spaceship`:

## 1. No permanent human-gate on asset generation

Do not have the loop stall indefinitely waiting for a human to
manually log in, generate, and download an asset. Instead:

- Prefer any source with a scriptable API the loop can drive directly
  (a ComfyUI instance's `/prompt` + `/history` + `/view` HTTP API is
  the reference implementation — see `tools/comfyui_asset_pipeline.py`
  in `spaceship` for a stdlib-only, zero-extra-dependency example).
  ComfyUI may run on `localhost` or on a remote GPU host; either way,
  hardcode the current `COMFY_HOST`/`COMFY_URL` in the tool script and
  keep old + new host prefixes in the asset-manifest verifier's
  `OFFICIAL_SOURCE_PREFIXES` if the host ever moves, so already-applied
  assets don't fail re-verification.
- The loop's own agent + an automated QA check (readability at actual
  runtime scale, silhouette/identity match, no artifacts) is what
  decides whether a generated asset becomes final — not a human
  approval step. Keep full provenance (workflow/prompt/seed/model,
  timestamp, output hash) in a manifest as a *quality record*, not an
  *approval gate*.
- A manual-login-only source (no API) may still be used opportunistically
  when credentials happen to be available, but the loop must not block
  other work on its absence — see `docs/feedback/INBOX.md`'s
  "human-gate 제거" pending items in `man-of-korea`/`spaceship` for the
  exact wording to copy into a new project's policy doc.

## 2. Report every applied asset back to the user

Append-only `docs/GENERATED_ASSET_LOG.md` (create this file when the
project's asset pipeline goes live) with one line per **final**
(non-candidate) asset the loop applies to the running game:

```
YYYY-MM-DDTHH:MM:SS+0900 | <repo-relative/path/to.png> | <one-line description>
```

`loop/PROMPT.md` must instruct the loop to append this line in the
same commit that applies the asset as final/runtime art — not for
candidates, superseded, or QA-only outputs.

Wire the project's periodic progress-report cron script
(`~/.hermes/scripts/<project>_progress_report.py`) to diff this file
against what it saw last run and print `MEDIA:<absolute path>` for
each new line. Hermes' delivery pipeline turns any `MEDIA:<path>` line
in cron/message output into a native image attachment, so the actual
generated PNG lands in the user's chat automatically the next time the
progress cron fires — no need for the user to go dig through
`docs/assets/MANIFEST.json` or `STATUS.md` to see what was produced.

See `man-of-korea` and `spaceship`'s `~/.hermes/scripts/*_progress_report.py`
(`new_asset_log_entries()` function) for the reference implementation,
and their `docs/GENERATED_ASSET_LOG.md` for the log format.

See the Hermes skill `autonomous-loop-token-optimization` for the
sibling pattern of keeping `docs/feedback/INBOX.md` and progress
reports token-lean.
