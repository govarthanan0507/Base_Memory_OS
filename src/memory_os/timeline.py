from __future__ import annotations
import json
from typing import Any

def project_timeline(store: Any, project_id: str, limit: int = 100) -> list[dict[str, Any]]:
    if limit < 1: return []
    project=store.conn.execute("SELECT * FROM projects WHERE project_id=?",(project_id,)).fetchone()
    if project is None: return []
    events=[]
    for e in store.list_project_events(project_id,limit=limit): events.append({"event_type":e["event_type"],"timestamp":e["timestamp"],"entity_id":project_id,"summary":e["summary"],"metadata":json.loads(e["metadata_json"] or "{}")})
    relations=store.conn.execute("SELECT * FROM relations WHERE source_id=? OR target_id=? ORDER BY created_at ASC",(project_id,project_id)).fetchall()
    for r in relations:
        other=r["target_id"] if r["source_id"]==project_id else r["source_id"]; direction="outgoing" if r["source_id"]==project_id else "incoming"
        events.append({"event_type":"relation","timestamp":r["created_at"],"entity_id":other,"summary":f"{direction} relation: {r['relation']} → {other}","metadata":json.loads(r["metadata_json"] or "{}")})
    for r in [x for x in relations if x["relation"]=="contains" and x["source_id"]==project_id]:
        a=store.conn.execute("SELECT * FROM artifacts WHERE artifact_id=?",(r["target_id"],)).fetchone()
        if a is None: continue
        if a["modified_at"]: events.append({"event_type":"artifact_modified","timestamp":a["modified_at"],"entity_id":a["artifact_id"],"summary":f"Artifact modified: {a['name']}","metadata":json.loads(a["metadata_json"] or "{}")})
        for c in store.list_artifact_events(a["artifact_id"],limit=limit): events.append({"event_type":"artifact_change","timestamp":c["timestamp"],"entity_id":a["artifact_id"],"summary":f"Artifact changed: {a['name']} ({c['event_type']})","metadata":{"old_hash":c["old_hash"],"new_hash":c["new_hash"],"old_modified_at":c["old_modified_at"],"new_modified_at":c["new_modified_at"]}})
    events.sort(key=lambda x:(x["timestamp"] is not None,x["timestamp"] or ""),reverse=True); return events[:limit]

def render_project_timeline(store: Any, project_id: str, limit: int = 100) -> str:
    p=store.conn.execute("SELECT name,root,status FROM projects WHERE project_id=?",(project_id,)).fetchone()
    if p is None:return f"# Project Timeline\n\nProject not found: `{project_id}`"
    lines=[f"# Project Timeline: {p['name']}","",f"- Root: `{p['root']}`",f"- Status: `{p['status']}`","","## Activity",""]
    events=project_timeline(store,project_id,limit)
    if not events: lines.append("No recorded activity yet.")
    else:
        for e in events: lines.append(f"- **{e['timestamp'] or 'undated'}** — [{e['event_type']}] {e['summary']}")
    return "\n".join(lines)

__all__=["project_timeline","render_project_timeline"]
