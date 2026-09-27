# homeexchangeradar

Checks your saved HomeExchange searches (defined in `searches.json`, hosted
in this repo) and pings you on Telegram when a new listing shows up.

https://gerardcm.github.io/homeexchangeradar/

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

Each search entry can set `"exchange_type"` to control which kind of
exchange it matches:

| Value | Matches |
|---|---|
| `"all"` (default, or omitted) | Both reciprocal swaps and GuestPoints stays |
| `"guestpoints"` | Homes open to a GuestPoints stay (includes reciprocal-first homes that also accept GuestPoints, same as HomeExchange's own "see all homes open to GuestPoints exchanges" filter) |

```json
{
    "active": true,
    "name": "Central Paris 27",
    "exchange_type": "guestpoints",
    "bounds": { "...": "..." },
    "from": "2027-06-19",
    "to": "2027-06-20"
}
```

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
  the original script).
