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

Each search entry can set `"exchange_types"` to a list matching the site's
own "Exchange type" filter chips:

| Value | Site chip | Sent to the API as |
|---|---|---|
| `"all"` | All types | `available` |
| `"gp"` | Guest points | `guest-wanted` |

Use `["all", "gp"]` to tick both, same as the site does. Leave the key out
for no filter at all, which also includes reciprocal homes.

```json
{
    "active": true,
    "name": "Central Paris 27",
    "exchange_types": ["all", "gp"],
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

## Running it on a schedule

Point Synology Task Scheduler (or cron, or a systemd timer) at `run.sh`
instead of running `homeexchangeradar.py` directly — it does a
`git pull --ff-only` before every run, so the script itself (not just
`searches.json`) always picks up the latest fix without a manual redeploy:

```bash
bash run.sh
```

It must live inside a real git checkout of this repo for the pull to work;
`secrets.json` stays local and untouched. If you were pointing the
scheduler straight at `python3 homeexchangeradar.py` before, switch it to
`run.sh` now — otherwise code fixes pushed to GitHub never reach wherever
it's actually running.

## Notes

- The HomeExchange session cookie is a login session — it will expire.
  When notifications stop working, re-capture it from a logged-in browser
  session (dev tools → Network → any request to homeexchange.com → copy the
  `Cookie` header) and update `secrets.json`.
- `check_calendar()` exists but isn't wired into the main flow yet (matches
  the original script).
