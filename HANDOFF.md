# Handoff notes

I don't have push access to GitHub from this session (no `gh` CLI, no token), so I
can't create the branch or push directly. Here's the fastest path to get this
live, using the files in this bundle.

## 1. Create the branch and add the files

From a local clone of `dfordev1/qusx`:

```bash
git clone https://github.com/dfordev1/qusx.git
cd qusx
git checkout -b followalong-app

# copy in the 6 files from this bundle (index.html, build_app.py,
# surah_index.json, qpc_v2_glyphs.json, reciters.json, README.md, HANDOFF.md)
# — e.g. if you unzipped this bundle to ~/Downloads/qusx_handoff:
cp ~/Downloads/qusx_handoff/*.{html,py,json,md} .

git add index.html build_app.py surah_index.json qpc_v2_glyphs.json reciters.json README.md HANDOFF.md
git commit -m "Add Qur'an follow-along app (letter/word/mushaf sync, all reciters, tajweed)"
git push -u origin followalong-app
```

If you'd rather not touch `main` at all, open a PR from `followalong-app` — GitHub
will show you the "Compare & pull request" button right after the push.

## 2. Turn on the live preview (GitHub Pages)

Once the branch (or a merged `main`) has `index.html` at the repo root:

- **Settings → Pages → Build and deployment → Source:** `Deploy from a branch`
- Pick the branch you just pushed, folder `/ (root)`
- Save. It publishes at `https://dfordev1.github.io/qusx/` within a couple of minutes.

(GitHub Pages can only serve one branch at a time per repo unless you use
environments/project sites — if `main` already serves something else, you may want
to point Pages at this new branch specifically, or merge first.)

## 3. Alternative if you don't want to use the terminal

GitHub's own web UI can do this without git locally:

1. Go to `https://github.com/dfordev1/qusx/tree/main` (or your default branch), click the branch dropdown → type a new branch name (`followalong-app`) → "Create branch".
2. Switch to that branch, click **Add file → Upload files**, and drag in all 6 files from this bundle.
3. Commit directly to that branch.
4. Then follow step 2 above to enable Pages.

## What I verified before handing this off

- Every feature (all 114 surahs load correctly, letter/word/mushaf modes, tajweed
  toggle, reciter switching, morphology tooltips, milestone break markers) was
  tested with Playwright against real fetched fixtures (HF audio/timing rows,
  this repo's own QUSX XML, real QCF V2/V4 font files) — not just eyeballed.
- No console errors in any of the tested paths (surah load, mode switching,
  reciter switching, tajweed toggle, word click-to-seek, playback highlighting).
- The three data sources are reconciled by `(surah, ayah, word-position)` —
  documented in `build_app.py`'s comments at each join point, since that's
  exactly where a future bug is most likely to hide if one of the three
  datasets' indexing conventions ever shifts.

## What's NOT done / open follow-ups

- No automatic retry if a live fetch fails mid-load (surfaces an error message,
  requires re-selecting the surah) — worth adding if flaky connections are a concern.
- Tajweed coloring is COLRv1-only (no Firefox OT-SVG fallback wired in, though
  Quran Foundation does host that variant too — see the tutorial doc for the path).
- The "propose upstream QUSX improvements" list from earlier in this conversation
  (the embedded-space-in-word data issue, undocumented `fragment`/`id`/`sajda type`
  attributes, no lightweight JSON export, no documented consumer example) is a
  separate, not-yet-drafted piece of work if you want it turned into actual issues/PRs
  against this repo's schema itself.
