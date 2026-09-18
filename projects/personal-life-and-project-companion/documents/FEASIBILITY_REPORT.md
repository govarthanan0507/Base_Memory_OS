# Feasibility Report — base-memory-os-personal-life-and-project-companion

Produced by: Feasibility & Cost Assessor role. Path: **FULL**.

## 1. Technical feasibility

Buildable with realistically available tools, componentized per
Market/Research's finding: retrieval and temporal-state patterns can
draw directly on MemPalace/Graphiti's published approaches; emotional-
memory sector design can draw on OpenMemory's architecture. The one
genuinely new piece — mapping an arbitrary file or code snippet to the
correct *project* (not a generic category) — has no close reference
implementation and is the real technical risk.

**Biggest technical unknown**: how reliably a system can infer "this
belongs to Project X" from file/code content alone, for a personal
user's own idiosyncratic project boundaries, without either
over-triggering (misclassifying unrelated files) or under-triggering
(missing real matches) often enough to erode trust in the propose-
then-confirm step. This is unknown until built and tried against the
user's actual, messy real data — no benchmark exists for this specific
task the way LongMemEval exists for conversational retrieval.

**Hardware / infrastructure requirements**: local embedding component
(same as v1's finding, still applies) — ~4GB RAM, standard 64-bit CPU
with AVX2, no GPU, for a model like `nomic-embed-text` via Ollama. No
new hardware category introduced by the emotional-memory or file-
classification pieces — both run as additional processing over the
same local embedding infrastructure, not a separate heavyweight
component. Read-only file scanning of designated folders (Downloads,
a code folder) has no meaningful hardware cost beyond normal disk I/O.

## 2. Economic feasibility — cost at multiple scale points

**Personal / low-usage (the actual scale here)**: $0 direct spend,
same reasoning as the v1 pass — all reference tools and the embedding
model are free/OSS, everything runs locally.

**Realistic growth-scenario cost**: not applicable — per `idea.md`,
this is explicitly a personal tool with no distribution intent,
confirmed directly with the user, not a hypothetical to size for.

**Cost-benefit summary**: the real cost is developer time, distributed
unevenly across the four pieces — low for retrieval/temporal/emotional
(pattern-adaptable from existing reference implementations), higher
and less predictable for project-level file classification (the
unknown named above).

## 3. Operational feasibility

Runs day to day at the intended scale: yes, single local user, no
server component, same reasoning as v1. Read-only file access adds no
operational risk of its own (nothing can be corrupted by a read); the
propose-then-confirm mechanic for file/code mapping is itself the
operational safety net for the one higher-risk piece — a wrong
classification costs a rejected suggestion, not a broken project.

## 4. Risk register

| Risk | Likelihood | Impact | Widens estimate materially? |
|---|---|---|---|
| Project-level file classification accuracy is worse than hoped on real, messy data | Medium-High | Medium (mitigated by propose-then-confirm — a bad suggestion is rejected, not applied) | Possibly — this is the named biggest unknown; if accuracy is poor, tuning time could be substantial |
| Emotional/behavioral modeling from conversation text alone produces shallow or wrong inferences | Medium | Low-Medium (an internal signal used for guidance, not a hard record — a wrong read is a bad suggestion, not corrupted data) | No |
| AGPL-3.0 license on AI File Sorter (the closest reference for the propose-then-confirm UX pattern) creates a copyleft obligation if its code is directly adapted rather than just studied | Low (personal use, no distribution — doesn't trigger AGPL's obligations today) | Low today; real if distribution intent ever changes | No, but flagged per the license-finding rule for future resurfacing |

## 5. Reuse-adjusted estimate

Unlike v1's idea, this is not "adopt one near-total match instead of
building." It's "adopt/study three separate reference patterns
(MemPalace, Graphiti, OpenMemory) for three of the four pieces, and
build the fourth (project-level file classification) mostly from
scratch, informed by AI File Sorter's UX pattern (preview-confirm) but
not its actual categorization logic (which is generic, not project-
aware, and AGPL-licensed)."

## 6. Recommendation to Advocate/Skeptic

Three of four pieces have real, low-risk, low-cost reuse paths. The
fourth (project-level file/code classification) is genuinely novel
relative to what this search found, carries the real technical risk,
and is exactly the kind of thing the propose-then-confirm safety net
(already decided, not up for debate) was designed to make safe to
attempt even without a guarantee of high accuracy on day one.
