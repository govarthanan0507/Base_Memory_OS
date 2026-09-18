# Market Research Report — base-memory-os-personal-life-and-project-companion

Produced by: Market/Research role. Path: **FULL**. Supersedes the
narrower `pre-planning/base-memory-os-v1-hybrid-retrieval/MARKET_RESEARCH.md`
(preserved, not deleted) — that pass was scoped to conversational
retrieval only, not this idea's real, combined scope.

## 1. Research goals

Whether the specific combination this idea needs — project/status
tracking + emotional/behavioral modeling + autonomous file/code-to-
project classification, all local-first and read-only — already
exists somewhere, in whole or in covering parts.

## 2. Target audience / segments

The user themselves; a personal tool, unchanged from the prior pass.

## 3. Competitive landscape

| Name | What it actually does | License | Covers which part of this idea | Gap |
|---|---|---|---|---|
| **MemPalace** (carried forward, still relevant) | Local-first verbatim conversation storage + semantic search | MIT | Conversational retrieval | No project/status tracking, no file classification, no emotional modeling |
| **Graphiti/Zep** (carried forward) | Temporal knowledge graph, validity-interval fact invalidation | Apache 2.0 | Fact/state-change tracking over time | Not project-status-shaped specifically; not file classification |
| **OpenMemory** (new this pass) | Self-hosted AI memory engine, "Hierarchical Memory Decomposition" across episodic/semantic/procedural/**emotional**/reflective sectors, local embeddings (Ollama/E5/BGE). Verified via direct fetch (the specific fork checked: MIT license, but that fork shows 0 stars/forks — low visibility; it's a fork of the CaviraOSS original, whose own adoption wasn't separately checked this pass). | MIT | **Emotional memory specifically** — the closest match found for that one piece | No project-status tracking, no file/code classification, no explicit idea-relationship graph |
| **AI File Sorter** (`hyperfield/ai-file-sorter`, new this pass) | Local-LLM-capable file organizer with a preview-then-confirm workflow (files analyzed, user reviews a table, nothing moves until "Confirm & Sort"). Verified via direct fetch: 1.7k★, 179 forks, active (937 commits, latest release Aug 2026). | **AGPL-3.0** — copyleft, license finding recorded per Part 2 below | **The propose-then-confirm mechanic specifically** — this is a strong structural match for that one piece of the idea | Verified directly: sorts into **generic categories** (Documents/Images/Videos), **not project-specific classification** — does not identify "which project does this belong to." Does not do emotional modeling or project-status tracking. |
| **Sortio**, **AI File Organizer Pro**, **The Drive AI** (surfaced, not independently verified) | Natural-language-driven file organizers, one ("The Drive AI") explicitly advertising "organize my downloads by project" | Not checked — these read as commercial products, not verified as OSS | Possibly project-aware file organization | Marketing claims only this pass — not independently verified the way MemPalace/AI File Sorter were (direct repo fetch). Labeled UNVERIFIED ASSUMPTION, not fact. |

## 4. OSS / reuse candidates — the honest overall finding

Run in full. **The specific, full combination this idea needs — project-
status tracking + emotional/behavioral modeling + autonomous project-
level file/code classification, together, local-first — was not found
as one product.** Every real match found (MemPalace, Graphiti,
OpenMemory, AI File Sorter) covers exactly one piece well and is
silent or generic on the others. This is a materially different
result from the v1 pass, where MemPalace alone was a very close match
to that narrower idea's core mechanic.

**This meaningfully supports the user's own claim** — stated
independently by the user before this search ran, and not assumed
true going in. The user is not automatically right about novelty in
general, but on this specific, checked question, the honest result
agrees with them.

**License findings** (per `SHARED/REUSE_AND_LICENSE_RULE.md`, recorded
regardless of build/adopt decision):
- MemPalace: MIT (carried forward).
- Graphiti: Apache 2.0 (carried forward).
- OpenMemory: MIT.
- **AI File Sorter: AGPL-3.0** — new finding, real restriction: AGPL
  requires that a modified/derivative work, including one only used
  over a network, also be released under AGPL. If any part of this
  idea's file-classification mechanic were built by adapting this
  project's own code (not just studying its UX pattern), that
  copyleft obligation would apply. Per this idea's own scope
  (personal, no distribution intent, CONFIRMED), this does not block
  anything right now — but it is recorded here so it resurfaces if
  that intent ever changes, per this system's standing rule.

## 5. Market trends

The personal-AI-assistant market is large and growing fast (~$4.84B
in 2026, projected $19.63B by 2030 per industry reporting, 41.9%
CAGR) with local-first specifically named as a real, growing
preference, not a niche. This is a fast-moving space overall, but the
*specific combination* this idea needs remains unaddressed by name in
what this search found — timing doesn't argue against building the
missing piece, since nothing currently occupies it.

## 6. Consumer / user behavior

Per the user directly: today they manually track project status in
their head, and files/code get orphaned in a messy Downloads folder
with no automatic recovery — this is the real baseline, an absence of
tooling, not a competing tool being worked around.

## 7. Opportunities & challenges

- Opportunity: no single product does the full combination — genuine
  white space, not just a personal impression, per this pass's own
  checked result.
- Opportunity: three of the four pieces (retrieval, temporal facts,
  emotional memory) already have real, permissively-licensed
  reference implementations to learn from or adapt (MemPalace,
  Graphiti, OpenMemory) — this is not a from-scratch build across the
  board.
- Challenge: the piece with no close match at all is the most novel
  and hardest to de-risk by adopting existing code — autonomous
  project-level file/code classification (as opposed to generic
  category sorting, which does exist and was checked).

## 8. Evidence strength labels

- FACT (direct fetch, this pass): OpenMemory's emotional-sector
  architecture and license; AI File Sorter's preview-confirm workflow,
  generic (not project-level) categorization, and AGPL-3.0 license.
- UNVERIFIED ASSUMPTION: Sortio/AI File Organizer Pro/The Drive AI's
  marketing claims about project-aware organization — not
  independently checked this pass.
- CONFIRMED (carried forward from v1 pass): MemPalace and Graphiti's
  scope and licenses.

## 9. Recommendation to Advocate/Skeptic

Unlike the v1 idea (where a near-total match existed and the honest
recommendation was "evaluate before building"), this idea's real,
full scope has **no near-total match** — the honest reuse strategy is
componentized: adopt/study MemPalace for retrieval, Graphiti for
temporal state, OpenMemory for the emotional-memory architecture
pattern, and treat project-level file/code classification (distinct
from AI File Sorter's generic category sorting) as the one genuinely
new piece requiring real build effort. This is a much stronger case
for proceeding than the narrower idea had.
