from __future__ import annotations
from typing import Any
from .conversation import ensure_schema
from .core import MemoryStore

def related_records(store: MemoryStore, source_id: str, limit: int = 50) -> list[dict[str, Any]]:
    if limit < 1: raise ValueError("limit must be at least 1")
    return [dict(r) for r in store.conn.execute("SELECT relation_id, source_id, relation, target_id, created_at, metadata_json FROM relations WHERE source_id=? OR target_id=? ORDER BY created_at DESC LIMIT ?", (source_id, source_id, limit))]

def _entity(store: MemoryStore, entity_id: str):
    queries=[("SELECT project_id AS id, name, root, status, summary FROM projects WHERE project_id=?","project"),("SELECT artifact_id AS id, name, artifact_type, location FROM artifacts WHERE artifact_id=?","artifact"),("SELECT conversation_id AS id, title, source, started_at, ended_at FROM conversations WHERE conversation_id=?","conversation"),("SELECT memory_id AS id, content, memory_type, source, observed_at FROM memories WHERE memory_id=?","memory")]
    for sql,kind in queries:
        row=store.conn.execute(sql,(entity_id,)).fetchone()
        if row is not None:
            item=dict(row); item["entity_id"]=item["id"]
            if kind=="memory": item["memory_id"]=item["id"]
            return kind,item
    return None

def _linked_entities(store: MemoryStore, entity_id: str, limit: int = 50):
    out=[]
    for link in related_records(store,entity_id,limit):
        other=link["target_id"] if link["source_id"]==entity_id else link["source_id"]; found=_entity(store,other)
        if found is None: continue
        kind,item=found; item.update(kind=kind,relation=link["relation"],relation_id=link["relation_id"]); out.append(item)
    return out

def conversation_context(store: MemoryStore, conversation_id: str, limit: int = 50):
    ensure_schema(store); row=store.conn.execute("SELECT * FROM conversations WHERE conversation_id=?",(conversation_id,)).fetchone()
    if row is None: raise KeyError(f"conversation not found: {conversation_id}")
    messages=[dict(r) for r in store.conn.execute("SELECT * FROM messages WHERE conversation_id=? ORDER BY sequence LIMIT ?",(conversation_id,limit))]
    linked=_linked_entities(store,conversation_id,limit); seen={x["id"] for x in linked}; expanded=list(linked)
    for item in linked:
        if item["kind"]=="project":
            for child in _linked_entities(store,item["id"],limit):
                if child["id"] not in seen: child["via_project"]=item["id"]; seen.add(child["id"]); expanded.append(child)
    return {"conversation":dict(row),"messages":messages,"related":expanded}

def project_context(store: MemoryStore, project_id: str, limit: int = 50):
    ensure_schema(store)
    if limit<1: raise ValueError("limit must be at least 1")
    row=store.conn.execute("SELECT * FROM projects WHERE project_id=?",(project_id,)).fetchone()
    if row is None: raise KeyError(f"project not found: {project_id}")
    linked=_linked_entities(store,project_id,limit)
    return {"project":dict(row),"conversations":[x for x in linked if x["kind"]=="conversation"],"artifacts":[x for x in linked if x["kind"]=="artifact"],"memories":[x for x in linked if x["kind"]=="memory"]}

def render_reentry_brief(store: MemoryStore, conversation_id: str, limit: int = 50) -> str:
    p=conversation_context(store,conversation_id,limit); c=p["conversation"]; lines=[f"# Re-entry: {c['title']}","",f"Conversation ID: {conversation_id}",f"Source: {c['source']}","","## Known related work"]
    lines += [f"- {x['kind']}: {x.get('name',x.get('title',x.get('content',x['id'])))} ({x['relation']})" for x in p["related"]] or ["- No linked project or artifact yet."]
    lines += ["","## Conversation"]+[f"**{m['role']}**: {m['content']}" for m in p["messages"]]
    return "\n".join(lines)

def render_project_reentry_brief(store: MemoryStore, project_id: str, limit: int = 50) -> str:
    p=project_context(store,project_id,limit); x=p["project"]; lines=[f"# Project Re-entry: {x['name']}","",f"Project ID: {project_id}",f"Status: {x['status']}",f"Root: {x['root']}","","## Artifacts"]
    lines += [f"- {a['name']} ({a.get('artifact_type','unknown')}) — {a.get('location','')}" for a in p["artifacts"]] or ["- No linked artifacts."]
    lines += ["","## Conversations"]+([f"- {c['title']} [{c['source']}] — {c['id']} ({c.get('relation','related')})" for c in p["conversations"]] or ["- No linked conversations."])
    lines += ["","## Linked memories"]+([f"- [{m['memory_type']}] {m['content']} — {m['memory_id']}" for m in p["memories"]] or ["- No linked memories."])
    return "\n".join(lines)

__all__=["conversation_context","project_context","related_records","render_project_reentry_brief","render_reentry_brief"]
