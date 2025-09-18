# Cursor Agent Verify Report (Template)

Date: {{date}}
Repo: {{repo}}

## System
- OS: Windows 11 Pro
- GPU: RTX 4060 (8 GB)
- Driver/CUDA: ~577.00 / 12.x
- Python: 3.11.4
- Cursor: {{cursor_version}}

## Env
- GITHUB_TOKEN: present (env)
- CONTEXT7_API_KEY: {{present|absent}}

## MCP
- Servers visible: Context7, GitHub, Filesystem, SQLite, Memory
- Tests summary:
  - Context7: {{OK|FAIL}} — {{note}}
  - Filesystem: {{OK|FAIL}} — {{note}}
  - SQLite: {{OK|FAIL}} — {{note}}
  - Memory: {{OK|FAIL}} — {{note}}
  - GitHub: {{OK|FAIL}} — {{note}}

## GPU (nvidia-smi)
```
{{nvidia_smi}}
```

## PyTorch
```
{{torch_info_json}}
```

## TensorFlow
```
{{tf_info_json}}
```

## Actions / Runner
- Runner state: {{online|offline}} (labels: self-hosted, windows, gpu)
- Latest runs:
  - ML Test (GitHub-hosted): {{status}} link: {{url}}
  - ML Long (self-hosted): {{status}} link: {{url}}

## Artifacts
- {{artifact_list}}

## Security
- PAT rotated: {{yes|no}}
- Secrets in logs: {{found|not found}}

## Decisions and Next Steps
- TF Strategy: CPU‑only (Windows), WSL2 GPU — backlog
- Schedule: weekly verify + cleanup
- Known issues: {{none|list}}