# api_keys/

One place for the pipeline's API keys, **without ever committing a key to git**.

| Name | Used by | Needed for |
|---|---|---|
| `TWOSPEAKER_API_KEY` | `pipeline.py` (`--api-key`), `voiceover_engine.py` | generating voiceovers with TwoSpeaker (the docu/ videos use your recorded voiceovers and need no key) |
| `GOFILE_TOKEN` | `docu/tools/deliver.py` | optional: upload finished videos into your gofile account (links last longer) |

## Where to put the values (pick one)

1. **Claude Code on the web (recommended):** add them as environment variables / secrets of the cloud
   environment (environment menu in the session's title bar → Edit → environment variables or API
   credentials), using the names above. Every new session gets them automatically, and Claude reads
   them by name. Nothing is pasted into the chat and nothing is stored in the repo.
2. **Your own computer:** copy `keys.example.env` to `api_keys/keys.env` and fill it in.
   `keys.env` is git-ignored by `api_keys/.gitignore`, so it stays on your machine.

Code reads keys through `docu/tools/keys.py`: an environment variable wins, otherwise
`api_keys/keys.env`.

```python
from keys import get
token = get("GOFILE_TOKEN")          # None when not set
```

Never paste a key into a chat message, a commit, a README or a build.py.
