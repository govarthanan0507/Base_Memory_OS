# Repo Candidates — consolidated, for Design Council's Repo Analyzer step

Combines this session's own Market-Research passes with a separate,
parallel ChatGPT conversation the user had about the same idea (handed
over as a raw transcript, not a summary — per the lesson learned this
cycle). **Every candidate below is explicitly labeled by verification
status.** Design Council must not treat an unverified name with the
same confidence as a verified one — that distinction is the entire
point of this document.

## VERIFIED — direct repository fetch, this session

| Name | Repo | License | What it actually does | Relevance |
|---|---|---|---|---|
| **MemPalace** | `MemPalace/mempalace` | MIT | Local-first, verbatim conversation storage + semantic search, 96.6% R@5 on LongMemEval, 59.1k★/7.6k forks | Retrieval piece |
| **Graphiti** | `getzep/graphiti` | Apache 2.0 | Temporal knowledge graph — facts carry validity intervals, invalidated not overwritten | Temporal-state piece |
| **OpenMemory** (the specific fork checked) | `msris108/OpenMemory` (fork of `CaviraOSS`) | MIT | Multi-sector memory incl. an emotional sector, local embeddings (Ollama/E5/BGE) | Emotional-memory piece. Caveat: this fork shows 0 stars/forks — low visibility; the original `CaviraOSS` project wasn't separately checked |
| **AI File Sorter** | `hyperfield/ai-file-sorter` | **AGPL-3.0** | Local-LLM-capable file organizer, preview-then-confirm workflow, 1.7k★/179 forks, active | Propose-then-confirm UX pattern. Does **generic category** sorting (Documents/Images/Videos), **not project-level classification** — does not solve this idea's core gap |
| **Basic Memory** | `basicmachines-co/basic-memory` | Not checked this pass | Local-first, MCP-native — Markdown files are the durable memory surface, SQLite indexes them into a graph; works with Obsidian/VS Code | Close structural match for "files are first-class, human-editable, not a black-box database" |
| **PMB (Persistent Memory Bank)** | `oleksiijko/pmb` | Not checked this pass | Local-first (SQLite, no API keys, no LLM call on the read path), indexes PDFs and project codebases, hybrid BM25+vector+graph search, MCP | **Most directly relevant verified candidate for the file/code-to-project piece** — it already does project + PDF indexing locally. Does not appear to do cross-project *classification* of an arbitrary unsorted file (its `index_project` scans a known codebase, not "which of my many projects does this belong to") — a real difference from what this idea needs, not confirmed either way without hands-on testing |
| **Cognee** | `topoteretes/cognee` | Not checked this pass (widely reported as open-source) | Knowledge-graph memory engine, pluggable backends (Neo4j/FalkorDB/KuzuDB/NetworkX + Redis/Qdrant/Weaviate), confirmed local Ollama support, 7,000+★ | Alternative/complementary temporal+graph piece to Graphiti |
| **Persona** | `saxenauts/persona` | Not checked this pass | Builds a personal knowledge graph from unstructured interaction data (chats, emails) | **Correction to the ChatGPT conversation's framing**: uses Neo4j **and OpenAI for all LLM calls** — this is **not local-first**, contrary to how it was described. Relevant as a *design pattern* (episodes/psyche/entities/notes separation), not as an adoptable local component as-is |

| **Claude-Mem** | `thedotmack/claude-mem` | Apache 2.0 | Captures everything an agent does in a session (tool usage, decisions, project context), **compresses it with AI into semantic summaries** (not verbatim), SQLite + Chroma hybrid search, injects context back into future sessions. Verified via direct fetch: 94.2k★, 8.3k forks, actively maintained — the largest candidate found in either research pass. Works across Claude Code, OpenClaw, Cursor and other agents. | Tracks project-specific context per session, filterable by project — real overlap with E1. **Direct conflict on E2/idea.md's core requirement**: its entire design is AI-compression, not verbatim retention — the opposite of the read-only/never-summarize principle this idea is built on, learned the hard way this session (a lossy summary dropped real content earlier today). Not adoptable for that reason, despite its scale and quality. Reference-worthy for the cross-agent "one memory brain, many tools" pattern only. |

## NAMED BY THE PARALLEL CHATGPT CONVERSATION — NOT YET VERIFIED

These may be real, low-quality, abandoned, or not exist as described.
Per this session's own repeated finding (the MemPalace duplicate-repo
pattern, the low-visibility OpenMemory fork), **an unverified name is
a lead, not a fact.** None of these should inform an architecture
decision until checked the same way the table above was:

CortexKG, Memory Vault, Engram, Synapse, Mimir, Eidetic OS, Memento,
Cortex, Fob, memoirs, Chief of Staff 2, GUPPI, CORE, XMem, Holt,
Letta, Mem0 (the latter two are very likely real and well-known in
this space, but weren't independently re-fetched this pass — treat as
high-confidence-but-unconfirmed, one notch above the rest of this
list).

## What this means for the still-open gap

None of the verified candidates — including PMB, the closest match —
confirm they solve this idea's specific, real gap: given an arbitrary,
previously-unseen file or piece of code, decide *which of the user's
many existing projects* it belongs to, propose that mapping, and let
the user confirm or correct it. PMB indexes a codebase you already
point it at; it doesn't appear to classify an unsorted file against a
set of many candidate projects. This keeps the `FEASIBILITY_REPORT.md`
and `PRE_MORTEM.md`'s named risk accurate and, if anything, slightly
reinforced by this deeper look — this remains the one piece requiring
real, mostly-original build effort.

## Instruction to Design Council / Repo Analyzer, when it reconvenes

1. Re-verify every "VERIFIED" entry above directly before relying on
   it for an architecture decision — this document's verification was
   done for evidence purposes at Pre-Planning, not as a substitute for
   Design Council's own required check.
2. Verify PMB, Basic Memory, Cognee, and Persona's licenses explicitly
   (not checked this pass) before any adoption decision, per
   `SHARED/REUSE_AND_LICENSE_RULE.md`.
3. Treat every "NOT YET VERIFIED" name as a research task, not a
   candidate — check existence, real content, license, and quality
   signals (stars/forks/commit activity, same method used above)
   before it enters any comparison.
