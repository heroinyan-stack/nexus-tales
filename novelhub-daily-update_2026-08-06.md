# NovelHub Daily Update — 2026-08-06

## Run Time
2026-08-06 03:00 Asia/Shanghai (cron job `novelhub-daily-update`)

## What Happened

### ❌ BLOCKED: Destructive uncommitted state found

Before running the daily script, a dangerous working-tree state was discovered:

| Metric | Value |
|--------|-------|
| Chapter JSON files in pending changes | 1,048 |
| Schema used by pending files | `{"lines","num","slug","title"}` — **no `content_en` or `content_zh`** |
| Frontend-renderable among them | **0** (all would show "being translated") |
| Content length per chapter | ~300–600 Chinese chars (not full translations) |

**Six confirmed regressions** (translated chapters with `content_en` data, destroyed):
`人在合欢宗开局成为圣女道侣` ch-0001 through ch-0006  
Each lost ~2,450 characters of English translation + `translated: true`.

**Root cause**: A previous `bxwx9-daily-scrape` run (2026-08-05 08:00) wrote `lines`-only schema files to the working tree but was never completed or reverted. `git add -A && git commit` with that state would have deployed **zero readable content** for all 1,048 chapters.

### ✅ Recovery Actions Taken

1. **Restored the 6 regressed translated chapters** from `HEAD`
   → `git checkout HEAD -- data/chapters/人在合欢宗开局成为圣女道侣/ch-000{1..6}.json`
2. **Backed up 52 new novel slugs** from working-tree `novels.json` to `/tmp/new_novels_backup.json`
   (These novels exist in the scrape output but not in committed `HEAD`)
3. **Stashed all remaining uncommitted changes** (1042 remaining chapter files + `novels.json` diffs)
   → `git stash save "pre-cron-stash-20260806-030505"`

### Daily Pull Script Result

```
✅ Pulled 0 chapters total
```

All 19 bxwx9-source novels in `HEAD` are already at capacity:
- 16 novels have 103–116 chapters (capped at 50 in script)
- 3 novels have 23–43 chapters, but source URLs return no new chapter links

### Deployment Status

- **Git push**: Nothing new to commit — `Everything up-to-date`
- **Live site** (`https://novelhub.beauty`): ✅ HTTP 200, serving correctly
- **Content verified**: Chapter 1 of Martial God Asura serves real English text

## Stash Contents (for later review)

```
git stash list
→ stash@{0}: pre-cron-stash-20260806-030505
  - 52 new novel entries (novels.json)
  - ~1042 chapter files (lines-only schema, non-renderable)
```

## Recommendations

1. **Do not force-push** — current `HEAD` is clean and production is healthy
2. **Process the 52 new novels** using `scripts/scrape_multi_source.py` (the schema-correct scraper), not the raw scrape output
3. **Add a schema validation guard** to `daily_pull_chapters.py` that fails if any chapter file lacks `content_en`/`content_zh`/`content`
4. **Consider committing the 52 new novel slugs** manually (they're in `/tmp/new_novels_backup.json`)
