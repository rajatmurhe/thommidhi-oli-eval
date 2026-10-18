"""Run one owner-authorized Oli interaction through installed Codex CLI.

Not called by the offline scorer. Requires existing Codex login and OLI_TOKEN.
No credentials in argv; outputs redacted before storage. No automatic retries.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone

p = argparse.ArgumentParser()
p.add_argument('prompt_file')
p.add_argument('--output', required=True)
p.add_argument('--resume')
p.add_argument('--allow-tool', action='append', default=[], choices=['confirm_terms_update', 'save_deal', 'update_deal', 'save_work_plan'])
a = p.parse_args()
token = os.environ.get('OLI_TOKEN')
if not token:
    raise SystemExit('OLI_TOKEN is required')
out = Path(a.output)
if out.exists():
    raise SystemExit('Choose a new output path; evidence must not be overwritten')
cmd = ['codex', 'exec', '--ignore-user-config', '--skip-git-repo-check',
       '-c', 'mcp_servers.oli.url="https://thommidhi.com/mcp"',
       '-c', 'mcp_servers.oli.bearer_token_env_var="OLI_TOKEN"',
       '-c', 'mcp_servers.oli.required=true', '--json']
for tool in a.allow_tool:
    cmd += ['-c', f'mcp_servers.oli.tools.{tool}.approval_mode="approve"']
if a.resume:
    cmd += ['resume', a.resume, '-']
else:
    cmd += ['--sandbox', 'read-only', '-']
started = datetime.now(timezone.utc).isoformat()
t0 = time.monotonic()
try:
    result = subprocess.run(cmd, input=Path(a.prompt_file).read_text(), text=True,
                            capture_output=True, timeout=240)
    raw, err, code = result.stdout, result.stderr, result.returncode
except subprocess.TimeoutExpired as exc:
    raw = exc.stdout or b''
    err = exc.stderr or b''
    raw = raw.decode() if isinstance(raw, bytes) else raw
    err = err.decode() if isinstance(err, bytes) else err
    code = None
elapsed = round((time.monotonic() - t0) * 1000)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(raw.replace(token, '[REDACTED]'))
out.with_suffix('.stderr').write_text(err.replace(token, '[REDACTED]'))
meta = {'started_at_utc': started, 'wall_time_ms': elapsed, 'exit_code': code,
        'timeout': code is None, 'resume_thread': a.resume,
        'latency_definition': 'process launch to completion, including MCP startup and model work',
        'unknown_write_outcome': code is None,
        'prompt_file': a.prompt_file}
out.with_suffix('.meta.json').write_text(json.dumps(meta, indent=2)+'\n')
print(json.dumps(meta))
