from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .adapters import chatgpt_conversation
from .conversation import Conversation, Message, persist_conversation
from .core import MemoryStore

def _messages_from_json(data: dict[str, Any]) -> tuple[Message, ...]:
    raw=data.get("messages")
    if not isinstance(raw,list): raise ValueError("JSON conversation requires a messages list")
    out=[]
    for i,item in enumerate(raw,1):
        if not isinstance(item,dict): raise ValueError(f"message {i} must be an object")
        role=str(item.get("role","")); content=str(item.get("content",""))
        if not role.strip() or not content.strip(): raise ValueError(f"message {i} requires role and content")
        out.append(Message(role=role.strip(),content=content.strip(),sequence=i,observed_at=item.get("observed_at"),external_id=item.get("id"),metadata=item.get("metadata") or {},message_id=item.get("message_id")))
    return tuple(out)

def conversation_from_json(data: dict[str, Any], source_location: str | None = None) -> Conversation:
    return Conversation(source=str(data.get("source") or "unknown"),title=str(data.get("title") or "Untitled conversation"),external_id=data.get("id"),started_at=data.get("started_at"),ended_at=data.get("ended_at"),source_location=data.get("source_location") or source_location,metadata=data.get("metadata") or {},messages=_messages_from_json(data))

def import_json(store: MemoryStore, path: str | Path) -> str:
    source=Path(path); data=json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data,dict): raise ValueError("conversation JSON root must be an object")
    return persist_conversation(store,conversation_from_json(data,str(source.resolve())))

def import_chatgpt_export(store: MemoryStore, path: str | Path) -> int:
    source=Path(path); data=json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data,list): raise ValueError("ChatGPT export must be a JSON list of conversations")
    imported=0
    for item in data:
        if not isinstance(item,dict): continue
        try: persist_conversation(store,chatgpt_conversation(item)); imported+=1
        except ValueError: continue
    return imported

def conversation_from_markdown(text: str, source: str="markdown", title: str="Untitled conversation", source_location: str|None=None) -> Conversation:
    messages=[]; role=None; buffer=[]; sequence=0
    def flush():
        nonlocal sequence,role,buffer
        content="\n".join(buffer).strip()
        if role and content: sequence+=1; messages.append(Message(role=role,content=content,sequence=sequence))
        buffer=[]
    for line in text.splitlines():
        lower=line.strip().lower()
        if lower in {"user:","assistant:","system:","tool:"}: flush(); role=lower[:-1]
        else: buffer.append(line)
    flush()
    if not messages: raise ValueError("Markdown conversation requires role markers such as 'user:' and 'assistant:'")
    return Conversation(source=source,title=title,source_location=source_location,messages=tuple(messages))

def import_markdown(store: MemoryStore,path: str|Path,*,source: str="markdown",title: str|None=None)->str:
    source_path=Path(path)
    return persist_conversation(store,conversation_from_markdown(source_path.read_text(encoding="utf-8"),source=source,title=title or source_path.stem,source_location=str(source_path.resolve())))

__all__=["conversation_from_json","conversation_from_markdown","import_chatgpt_export","import_json","import_markdown"]
