# /test-agents

Quick smoke-test: verify both agent types respond correctly.

```bash
uv run python -c "
from claude_cli import call
s = call('Reply with exactly: SUPERVISOR_OK', agent='supervisor')
r = call('Reply with exactly: RESEARCHER_OK', agent='researcher')
print('supervisor:', s)
print('researcher:', r)
print('All agents OK' if 'OK' in s and 'OK' in r else 'FAILED')
"
```
