# homeexchangeradar

Checks your saved HomeExchange searches (defined in `searches.json`, hosted
in this repo) and pings you on Telegram when a new listing shows up.

## Setup

```bash
cp secrets.example.json secrets.json
```

Fill in `secrets.json` with your real values — Telegram bot token/chat id,
your HomeExchange session cookie, the calendar API bearer token, and the
local path for `notificationHistory.json`. This file is gitignored and
never leaves your machine/NAS.

`searches.json` (the list of active searches) stays in this repo and is
fetched at runtime from the raw GitHub URL — edit it here and every run
picks up the change automatically, no redeploy needed.

Run it:

```bash
pip install requests
python3 homeexchangeradar.py
```

Point Synology Task Scheduler (or cron) at that command on whatever cadence
you want checks to run.

## Notes

- The HomeExchange session cookie is a login session — it will expire.
  When notifications stop working, re-capture it from a logged-in browser
  session (dev tools → Network → any request to homeexchange.com → copy the
  `Cookie` header) and update `secrets.json`.
- `check_calendar()` exists but isn't wired into the main flow yet (matches
  the original script — the TODOs at the top are still open).
