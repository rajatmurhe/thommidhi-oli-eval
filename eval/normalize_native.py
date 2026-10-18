"""Normalize actual Codex JSONL. Does not create manual judgments or infer state."""
import argparse
import json
from pathlib import Path

ALIASES = {'get_my_creator_profile':'profile.read', 'get_my_terms':'terms.read',
           'propose_terms_update':'terms.propose', 'confirm_terms_update':'terms.confirm',
           'check_offer':'offer.check', 'save_deal':'deal.save',
           'update_deal':'deal.update', 'save_work_plan':'plan.save',
           'list_my_deals':'workspace.read'}

def operation_succeeded(item):
    """Transport completion alone does not prove a business write succeeded."""
    result = item.get('result') or {}
    if item.get('status') != 'completed' or item.get('error') or result.get('isError') or result.get('is_error'):
        return False
    structured = result.get('structured_content') or result.get('structuredContent') or {}
    tool = item.get('tool')
    if tool == 'confirm_terms_update':
        return True if structured.get('saved') else None
    if tool in ('save_deal', 'save_work_plan'):
        return True if structured.get('id') else None
    if tool == 'update_deal':
        return True if structured.get('id') and structured.get('changed') else None
    return True


def normalize(path, case_id):
    path = Path(path)
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    ordered, seen, complete, messages = [], set(), {}, []
    for event in events:
        item = event.get('item', {})
        if item.get('type') == 'mcp_tool_call':
            identity = item['id']
            if identity not in seen:
                ordered.append(identity); seen.add(identity)
            if event['type'] == 'item.completed': complete[identity] = item
        if event['type'] == 'item.completed' and item.get('type') == 'agent_message':
            messages.append(item['text'])
    calls = []
    for identity in ordered:
        item = complete.get(identity)
        if item is None:
            item = next(e['item'] for e in events if e.get('item', {}).get('id') == identity)
        result = item.get('result') or {}
        calls.append({'name':ALIASES.get(item['tool'], item['tool']), 'wire_name':item['tool'],
                      'arguments':item.get('arguments', {}), 'arguments_complete':True,
                      'transport_completed': item.get('status') == 'completed',
                      'succeeded': operation_succeeded(item),
                      'error':item.get('error'), 'result':result})
    meta_path = path.with_suffix('.meta.json')
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    return {'case_id':case_id, 'source':str(path),
            'tool_trace_complete': any(e['type']=='turn.completed' for e in events) and len(complete)==len(ordered),
            'calls':calls, 'final_text':messages[-1] if messages else None,
            'latency_ms':meta.get('wall_time_ms'), 'cost_usd':None,
            'usage':next((e.get('usage') for e in reversed(events) if e['type']=='turn.completed'),None),
            'manual_reviews':{}}

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('trace');p.add_argument('case_id');a=p.parse_args()
    print(json.dumps(normalize(a.trace,a.case_id),indent=2,ensure_ascii=False))
