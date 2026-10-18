# Thommidhi Oli: tool-use evaluation

I tested Oli through Claude and native Codex CLI using my own account and explicitly synthetic creator, offer and plan data. This repository contains the 20-case suite, offline scorer, notebook, exact native tool traces and saved-state evidence. No channel analytics, credentials, private minimum fee or personal portal link are included.

## Run the evaluation

Python 3.11 or later; the offline scorer needs only the standard library. No API key or network access is needed.

```sh
python3 -m unittest discover -s eval -v
python3 eval/score.py eval/cases.json evidence/claude-pilot.json
python3 eval/score.py eval/cases.json evidence/codex-pilot.json
python3 eval/build_checkpoint.py
```

Open [the notebook](eval/review_notebook.ipynb), or inspect the [20 requests and expected behavior](eval/cases.json).

## Results and limits

| Run | Passed | Failed | Not run |
| --- | ---: | ---: | ---: |
| Original Claude pilot | 2 | 1 | 17 |
| Original Codex pilot | 6 | 1 | 13 |
| Later checkpoint after corrections/recovery | 20 | 0 | 0 |

The checkpoint combines corrected setup, a recovered confirmation, stateful workflow steps and multi-case batches. These are **not 20 independent first-attempt successes**, and the passing checks are not a general robustness estimate. The original failures remain available. Claude's corrected preview required intervention; its confirmation failed because it lacked a usable preview ID. Native structured output had the ID, but its first confirmation was blocked by client approval policy. A later scoped-permission retry committed and reread the terms.

Both clients saved separate synthetic deals and plans. Later native reads verified both deals in talks and exactly one linked plan for each. The private-fee test used a value configured outside the tested chat context, with sharing off. No disclosure was observed; later fee checks paused for the day. Backend agreement enforcement, cross-tenant access, adaptive fee inference and general injection resistance were not established.

Seventeen regression tests cover partial evidence, call order, forbidden writes, independent saved-state reads and the distinction between transport completion and a committed write. Semantic review annotations are separate from deterministic checks and are not independently blinded judgments. C06 was clarified after inspecting the actual stage semantics; this is a disclosed suite revision, not a preregistered benchmark.

## Evidence map

- [Original Claude observations](evidence/claude-pilot.json)
- [Original Codex pilot](evidence/codex-pilot.json)
- [Later checkpoint](evidence/codex-checkpoint.json) and [score](evidence/codex-checkpoint-score.json)
- [Confirmation recovery](evidence/codex-native-c03-approved.jsonl)
- [Deal and plan workflow](evidence/codex-deal-plan.jsonl)
- [Private-context red team](evidence/codex-private-redteam.jsonl)
- [Boundary cases and independent readback](evidence/codex-boundaries.jsonl)
- [Saved-terms offer check and privacy pause](evidence/codex-c04-saved.jsonl)
- [Sanitized privacy setup receipt](evidence/privacy-fixture-receipt.json)
- [Prompts](prompts/) and [raw conversation exports](conversations/)

The native JSONL records preserve calls, arguments, results and final answers. Some checks share a source invocation; do not sum their latencies or treat them as independent samples. Timings include startup and model work. Monetary cost is unknown. Claude evidence comes from visible tool panels rather than a captured native wire transcript.

## Screenshots and report previews

[Open the image gallery](screenshots/README.md) for the saved portal screenshot and final report previews. Captions distinguish live product evidence from rendered report pages. The portal image predates final attachment replacement and is not a submission receipt.

[![Final report overview](screenshots/report-overview.png)](screenshots/README.md)

## Design sketches

The [outcome tool schema](design/record_test_outcome.schema.json) and [common prediction contract](design/prediction-contract.ts) are proposals, not shipped integrations. The outcome tool extends the product's existing post-publication feedback loop through an assistant-accessible interface.

## Live runner

`eval/run_codex_case.py` is optional and is not called by offline scoring. It requires an existing Codex login and an owner-approved Oli key in `OLI_TOKEN`. It permits only explicitly selected test-write tools, does not automatically retry, and refuses to overwrite evidence. Use only your own authorized test account. After an uncertain write outcome, reconcile saved state before retrying.

No brand was contacted. All saved test records are labeled EXPLORATION.
