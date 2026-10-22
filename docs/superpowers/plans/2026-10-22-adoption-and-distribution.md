# Limekit / Limer — Adoption & Distribution Plan

**Created:** 2026-10-22
**Owner:** Omega Msiska
**Spans two repos:** `Limekit` (framework, branch `limekit-2.0`) and
`Limer-Limekit` (launcher, branch `limekit-2.0-port`)

**Status key:** `TODO` · `IN PROGRESS` · `DONE` · `BLOCKED` · `DEFERRED` · `DROPPED`

---

## The distribution model (the decision everything else follows from)

Limekit the framework is **never installed by users**. One download — Limer,
frozen with PyInstaller — contains Python, Qt and Limekit. A user downloads it,
unzips it, runs it, and writes Lua. No Python install, no pip, no toolchain.

The Limekit repository is for framework developers, and is the only place
Python is mentioned.

**This model is correct and is the project's biggest competitive advantage over
every other "GUI for language X" project.** It is also, as of today, not yet
true in code — see Phase 1, which is why Phase 1 blocks the launch.

### Verified today (2026-10-22)

| Fact | Evidence |
|---|---|
| A frozen Limer refuses to run projects | `Limekit/limekit/launcher.py:51-59`, surfaced at `Limer-Limekit/scripts/app/core/project_runner.lua:93-97` |
| The 1.x released Limer spawns a bare `python`/`python3` from PATH | `limekit/core/bootstrap/subprocess_runner.py:22-33` (on `origin/main`) — so the *current* release needs Python installed to run a project, which is why the old README asked for it |
| The frozen entry script hardcodes its own bundle as the project | `limekit/build/entry_script.py` — no flag to run an arbitrary project path |
| 714 tests pass | `python -m pytest` (offscreen) |
| Neither repo has a LICENSE file | `git ls-files` |
| Both repos' default branches are still 1.x | `origin/main`, `origin/master` |

**Conclusion:** "download Limer and go" needs one mechanism built — a frozen
Limer must be able to re-launch *itself* as a project runner. That is Phase 1.

---

## Phase 0 — Zero-risk wins `IN PROGRESS` (only 0.5, the GIFs, remains)

Nothing here can break anything. Do it first.

| # | Task | Status |
|---|---|---|
| 0.1 | Add `LICENSE` to both repos | `DONE` 2026-10-22 — GPLv3 (canonical FSF text, md5 `1ebbd3e3…`) in both; `setup.py` now declares GPLv3 and `MANIFEST.in` ships the file. See license note |
| 0.2 | Rewrite `Limekit/README.md`: framework-dev audience, users sent to Limer Releases | `DONE` 2026-10-22 — code sample run headless and verified |
| 0.3 | Rewrite `Limer-Limekit/README.md`: lead with "download, unzip, run". Drop the `.rar`, the Python install steps, the "3 compressed files", and "I do not have a Mac" | `DONE` 2026-10-22 — describes the Phase 1 target; do not merge to `master` before Phase 1 lands |
| 0.4 | Ship releases as `.zip`, never `.rar` | `DONE` 2026-10-22 — now `python package_portable.py --zip` (see 1.9), writing `Limer-<version>-<os>.zip` that unpacks to one `Limer/` folder |
| 0.5 | Record two GIFs — the Designer, and the Inspector editing a live app — and put them at the top of Limer's README | `BLOCKED` — needs a human screen recording; shot list below |
| 0.6 | Add CI: `.github/workflows/ci.yml` in both repos, matrix over ubuntu/windows/macos | `DONE` 2026-10-22 — every command verified locally; first GitHub run: Windows and macOS pass, Ubuntu fails -- see CI follow-ups. Limekit: `pytest` (already covers import-linter, the three generator no-op checks and all 2.0 demo boots). Limer: its 36 checks + API-index staleness, plus a hand-triggered 3-OS PyInstaller build uploading zips |
| 0.7 | Delete Limer's dead code | `DONE` 2026-10-22 — owner approved; 14 files, 1,538 lines removed with `git rm` (list below). Limer's 36 checks pass and it boots |
| 0.8 | Remove the stale 1.x comments and the 1.x `misc/templates/hello.lua` | `DONE` 2026-10-22 — stale comments fixed; template removed with 0.7. Other 1.x mentions in Limer are accurate history and stay |

**License note.** GPLv3 was kept because it is what Limekit already declared,
and because Limer bundles Limekit and so must be GPL-compatible anyway. The
open question remains: GPLv3 on the framework tells anyone wanting to ship a
closed app that they cannot. PySide6 itself is LGPL. If the goal is adoption,
LGPL or Apache-2.0 on the framework is the move; Limer itself can stay GPL. As
sole copyright holder the owner can relicense at any time — but before the
launch is far cheaper than after people have built things.

**0.5 shot list** (≈15 s each, 1280×800, light theme):
1. *Designer* — open Designer → drag a Label and a LineEdit into a form → drag
   a Button below → double-click it, type "Sign in" → Ctrl+R shows the real
   window.
2. *Inspector* — run the `kanban` example → open the Inspector → click a card
   in the tree → change its text in Properties → the running app updates.

**0.7 deletion list** (all tracked in git, all verified unreferenced):
`scripts/views (TO REFACTOR)/` · `scripts/common/` · `scripts/config/` ·
`scripts/app/modals/` · `misc/templates/` · `scripts/gui/tabs/properties_tab copy.lua` ·
`scripts/app/core/build_manager.lua` · `scripts/app/bootstrap.lua` ·
`scripts/app/core/init.lua` · `scripts/app/core/utils.lua` ·
`scripts/app/core/config/constants.lua` · `scripts/gui/tabs/console.lua`.
One command, from `Limer-Limekit/` — reversible with `git restore --staged . && git checkout -- .`:

```
git rm -r -q "scripts/views (TO REFACTOR)" scripts/common scripts/config scripts/app/modals misc/templates "scripts/gui/tabs/properties_tab copy.lua" scripts/app/core/build_manager.lua scripts/app/bootstrap.lua scripts/app/core/init.lua scripts/app/core/utils.lua scripts/app/core/config/constants.lua scripts/gui/tabs/console.lua
```

---

## CI follow-ups `IN PROGRESS` (C.3 left)

From the first real run on GitHub (Limekit's workflow, after the push on
2026-10-22): **windows-latest/3.12 ✅ · macos-latest/3.12 ✅ ·
ubuntu-latest/3.10 ❌ · ubuntu-latest/3.12 ❌** (failed in under a minute).

| # | Task | Status |
|---|---|---|
| C.1 | Ubuntu fails on both Python versions | `DONE` 2026-10-22 — the job log (688 passed, **1 failed**) showed it was not environmental: `test_fontcombobox_onitemselect_guarded` assumed which font a QFontComboBox starts on. It starts on the system default font -- far down the list on Windows, item 2 on Ubuntu -- so `setCurrentIndex(2)` was a change on Windows and a no-op on Ubuntu, and `onItemSelect` (Qt's currentIndexChanged) rightly fired only on Windows. The test now picks an item that is not current. Framework unchanged. Note: `ubuntu-latest` moved to Ubuntu 26 on 2026-10-19 |
| C.2 | Node.js 20 deprecation | `DONE` 2026-10-22 — `actions/checkout`, `actions/setup-python` and `actions/upload-artifact` moved to `@v7` in both workflows; each v7 tag's `action.yml` checked to declare `node24`. Confirmed by the next CI run |
| C.3 | Once green: add CI badges to both READMEs | `TODO` |

---

## Phase 1 — Make "download and run" actually true `IN PROGRESS` ⬅ **blocks launch**

**Decision (2026-10-22): Limer is no longer frozen with PyInstaller.** It ships
as a folder holding a real portable CPython (python-build-standalone, the
builds `uv` uses) with Limekit and its dependencies installed, plus a ~100 KB
`Limer.exe` that starts it. To the user nothing changes: unzip, double-click.

Why: a real interpreter makes both halves of the problem disappear. Running a
project already spawns `sys.executable -m limekit` (`launcher.py:48`), and
building already runs `sys.executable -m PyInstaller` (`build/builder.py:125`).
Inside a frozen Limer, `sys.executable` is `Limer.exe`, which is why both are
broken today — and PyInstaller cannot run inside a frozen app at all, since it
launches helper interpreters through `sys.executable` for its Qt hooks
(`PyInstaller/compat.py:467`, `utils/hooks/qt/__init__.py`). Rejected
alternatives: a frozen Limer re-executing itself as a project runner (fixes
Run, not Build); a generic runtime copied per app (a second mechanism); a
separately downloaded builder pack (ships a second ~200 MB Python+Qt, lets the
two drift apart, and adds a download at the moment a user wants to share).

The launcher is pip's own script launcher (`distlib`'s `w64.exe`), whose
shebang supports a `<launcher_dir>\` prefix — so it finds the Python beside it
with no compiler and no absolute paths.

| # | Task | Status |
|---|---|---|
| 1.1 | `package_portable.py` in Limer: fetch a pinned, checksum-verified portable CPython; install Limekit and pinned dependencies into it; copy Limer's project in; write `Limer.exe`; zip it | `DONE` 2026-10-22 — CPython 3.13.16 (python-build-standalone `20261003`, sha256 cross-checked against GitHub's digest and the release's SHA256SUMS); deps pinned in `portable-constraints.txt` to the versions the suite passes on; `Limer.exe` is pip's `w64.exe` launcher with Limer's icon and a `<launcher_dir>` shebang |
| 1.2 | Trim what Limekit never uses (Qt WebEngine, translations, Qt tools) and measure the zip | `DONE` 2026-10-22 — 503 MB removed; **221 MB unpacked, 84 MB zip**. `opengl32sw.dll` kept on purpose (software OpenGL for machines without GPU drivers) |
| 1.3 | Isolate the bundled Python from the user's machine: no `PYTHONPATH`, `PYTHONHOME` or user site-packages leaking in — for Limer and for every project it runs | `DONE` 2026-10-22 — `-I` on Limer's process, `PYTHON*` cleared and `PYTHONNOUSERSITE=1` for its children. Verified with a poisoned `PYTHONPATH`/`PYTHONHOME`/`PYTHONSTARTUP`: Limer ignores them; the same poison without the launcher loads the fake package (control) |
| 1.4 | Inspector in the portable build | `DEFERRED` — set aside by owner 2026-10-22 |
| 1.5 | Prove it on Windows with no Python visible | `DONE` 2026-10-22 — automated checks (see 1.8/1.9 era notes above: boots as bundled `pythonw.exe -I`, `sys.ProjectRunner` runs 2.0 and 1.x projects, full suite on the trimmed Python, all 2.0 demos against the installed copy, poisoned-environment isolation). **GUI check:** the downloaded `Limer.exe` driven through Windows UI Automation with real windows — New Project → name → Create Project → Yes (default icon) → Run → the project's own window appeared, running on the bundled `pythonw.exe` → Stop ended it. PASS |
| 1.6 | Build (user apps) from the portable Limer | `DONE` 2026-10-22 — PyInstaller ships in the bundle (`limekit[build]`, pinned in `portable-constraints.txt`; +17 MB unpacked). Verified on the bundle with no Python on PATH: `sys.ProjectBuilder` (Limer's Build path, under `pythonw`) built the README sample in 50 s into a single 45 MB exe, which ran with no Python on PATH, its click handler fired, exit 0 |
| 1.7 | Linux and macOS portable builds, assembled and smoke-tested in CI | `TODO` — after Windows is proven |
| 1.8 | **Found by 1.5:** `playsound` missing from Limekit's `setup.py`, though the 1.x engine imported it at module level (`engine/app_engine.py:11`) — every 1.x project crashed on start in an installed Limekit. First pinned; then, at the owner's request, **removed entirely**: the import and `Sound` global, `utils/sound.py`, `app.playSound` in the 1.x runtime, the build hidden-import, all four dependency files, and the test that required it. No app used it (only an autocomplete word list in the 1.x "limekit ide" demo). Verified: 1.x engine imports with `playsound` blocked; the 1.x calculator runs; suite 666 passed. Also untracked `.vscode/PythonImportHelper-v2-Completion.json`, a 12k-line generated editor cache that was committed | `DONE` 2026-10-22 |
| 1.9 | Release builds must come from `package_portable.py`. `build.py`/`build_folder.py` now say NOT FOR RELEASES (a frozen Limer cannot run projects); the CI build job assembles the portable build instead | `DONE` 2026-10-22 |

**Phase 1 follow-ups (not blocking):** a third-party notices file in the bundle
(CPython's `LICENSE.txt` and the Qt/PySide licenses already ship in it; the
launcher's should be added); `Limer.exe`'s file properties still read "Simple
Launcher"; bump `app.json` `version` before the release zip is named.

---

## Phase M — Migrate 1.x projects to 2.0 automatically `DROPPED` 2026-10-22

**Dropped by the owner:** there are unlikely to be 1.x projects in the wild,
the 1.x engine still runs any that exist (verified: the 1.x calculator runs
in portable Limer), and 46 of the 52 1.x demos are already hand-ported as
`2.0-examples`. The research survives below for the day the 1.x engine is
retired; the started code (Lua lexer + tests, index-shift scanner) was moved
out of the repo, not committed.

What the research found, worth keeping: 2.0 is not a rename of 1.x. The 1.x
engine injects 136 globals and a 94-function `app` table; the 52 demos call
68 method names that exist nowhere in 2.0 (`Table` was redesigned:
`setItemText`→`setCellText`, `setMaxRows`→`setRowCount`, 0-based→1-based);
1.x already passed `self` first to handlers, so handler shapes carry over.

Requested by the owner 2026-10-22: when Limer opens a 1.x project, offer to
migrate it. The kernel spec always planned this (`limekit migrate`, spec §5:
"the demos are the migration corpus"); it was never built.

**Design.** A Python codemod in Limekit (`python -m limekit migrate <project>`),
because it needs real tooling and tests; Limer reaches it through the bundled
interpreter. It works on **tokens, not regex** — a small Lua lexer, so strings,
comments and long brackets are never rewritten, and a name the user declared
`local` is never mistaken for a 1.x global. It *offers*, never acts silently:

1. Limer detects a 1.x project on open (`getApiVersion`) and shows
   "This is a Limekit 1.x project — migrate to 2.0?"
2. On yes: copy the project to `<name>-1x-backup` first, always.
3. Rewrite mechanically: flat globals → `ui.X` / `chart.X` with `require`
   lines added; `app.*` → `fs.FileSystem` / `sys.System` / `ui.Theme` /
   `ui.Dialogs`; `images()/scripts()/misc()` → `res.Resources.*`; renamed
   classes and methods; `Modal(parent, title)` → `Modal(title, parent)`;
   `"api": "2.0"` into `app.json`.
4. 0-based → 1-based: literal indexes are shifted; anything it cannot prove
   (a variable index) gets a `-- MIGRATE:` comment instead of a guess.
5. Removed APIs with no 2.0 equivalent (`app.weightedGraph`,
   `Menu:buildFromTemplate`, …) are left in place with a `-- MIGRATE:` note.
6. Show a report — what changed, what needs a human — then offer Run.

The source of truth for the mappings is `limekit-docs/source/migrating.rst`
plus the 1.x runtime (`limekit/lua/limekit.lua`, engine part names) and the
2.0 registry's alias table.

| # | Task | Status |
|---|---|---|
| M.1 | Lua lexer + rewrite engine with scope awareness (locals shadow globals) | `TODO` |
| M.2 | Rule tables: globals, `app.*`, resources, renames, constructor swaps, removals | `TODO` |
| M.3 | Index shifting for literals; `-- MIGRATE:` flags for the unprovable | `TODO` |
| M.4 | `python -m limekit migrate` with backup and a report | `TODO` |
| M.5 | **Corpus test:** run it over the 52 1.x demos; success = each migrated demo boots clean on the 2.0 engine (`test_demo_smoke` machinery), then turns their 52 xfails into passes | `TODO` |
| M.6 | Limer: detect on open, offer, back up, migrate, show the report | `TODO` |

**Honest limit:** a codemod can make most apps *run*; it cannot prove every
index shift is right, which is why it flags rather than guesses. Expect
`-- MIGRATE:` comments in real apps.

---

## Retire the 1.x engine `DONE` 2026-10-22

Owner's decision, following Phase M being dropped. The 1.x engine was ~172
files / 11,000 lines -- about the size of all of 2.0 -- and only ran 1.x
projects.

| # | Task | Status |
|---|---|---|
| R.1 | Remove `engine/`, `components/`, `core/`, `utils/`, `gui/`, `lua/`, `config/`, `runner.py`, `main.py`, `build/project_builder.py`, the stale `limekit/requirements.txt` | `DONE` — moved to `_archive/limekit-1x-engine/` beside the repos (the tool's safety check refused a `git rm` that would have discarded uncommitted edits); last committed versions remain in git history |
| R.2 | A 1.x project is recognised and refused with a pointer to the migration guide, by Run (`launcher.ProjectRunner`) and Build (`AppBuilder`) alike; Limer says so in its console instead of starting it | `DONE` — verified with the archived 1.x calculator: message, exit 1, nothing started |
| R.3 | Build: one entry script; 1.x hidden imports and the `limekit/lua` bundling removed | `DONE` — a real build from source ran (`TEXT=Clicked!`, exit 0) |
| R.4 | Tests: 1.x demo xfails, engine-dispatch and shim tests replaced; new guard `test_the_1x_engine_stays_retired` (proved to fail on a planted 1.x import) | `DONE` — 689 passed, 0 xfailed |
| R.5 | Limer: Inspector's engine check and the "engine" console wording removed (one engine) | `DONE` |
| R.6 | Docs: README, concepts, index, migrating, questions no longer promise 1.x keeps running; Sphinx builds clean with `-W` | `DONE` |
| R.7 | limekit-demos: 53 1.x demo folders off the v2 branch; preserved on branch `1.x-demos` and in `_archive/limekit-1x-demos/` | `DONE` |
| R.8 | `qtmodern` dropped from `requirements.txt` (imported nowhere) | `DONE` |

---

## Side work — branding and About `DONE` 2026-10-22

| # | Task | Status |
|---|---|---|
| B.1 | Redesign Limer's About after Doxa's brand card: frameless navy modal, fades in, fades out on click/Esc/Enter/Space; Limer's version read from its own `app.json` instead of hard-coded | `DONE` — `scripts/gui/modals/about.lua`. First built as a rounded card inside a transparent window; on real Windows 11 the system drew a 1px border round the transparent margin, so it looked like two components (headless renders could not show it). Reworked at the owner's request: the modal itself is the navy surface, no card, radius or shadow of its own. Verified solid to every edge under both themes; all dismissals still fade. Then a ✕ close button, top-right, sharing the icon's row so the card did not grow; verified the ✕, Esc and a click all fade it out |
| B.2 | Naveto Tech logo in the About (`images/about/naveto-tech.png`, from `final-pills-c/png/naveto-horizontal-dark.png` at 800 px); the card's surface is the logo's own navy `#1B1B3A` so it sits on it seamlessly | `DONE` |
| B.3 | Replace Rézolu with Naveto Tech. No Rézolu text remained anywhere (tracked, ignored or binary files, all four repos); restored as Naveto Tech the three places the earlier removal commit (`dfd70a5`) emptied: `app.json` copyright, the About's company line, `scripts/main.lua` header | `DONE` |
| B.4 | Framework: `ui.Modal` gains `setFrameless`/`isFrameless`, `opacity`, `fadeIn`/`fadeOut`, `setOnMousePress` — splash screens and cards for any Limekit app. `setFrameless` is opaque on purpose (see B.1). 5 tests; stubs and API index regenerated | `DONE` |
| B.5 | Framework: `ui.Image:setImageSize` scales for the screen's pixel ratio (was blurry at 125–200% display scaling) — every Limekit app's images get sharper. Test fails on the old code, passes on the new | `DONE` |
| B.6 | "Take bytes" → Naveto Tech | `DONE` 2026-10-22 — owner approved; 37 occurrences in 36 files (34 1.x demo files incl. `app.json` copyrights and the "limekit ide" demo's title/About, plus docs `conf.py` copyright and getting-started); byte-level swap, none left |
| B.7 | Limer has no high-resolution logo: its icon is a 64 px lime, soft above ~125% scaling in the About and as `Limer.exe`'s icon | `TODO` — needs a proper Limer mark (SVG or ≥256 px) |

---

## Phase 2 — Correctness bugs that will bite real users `DONE` 2026-10-22

All 12 fixed test-first; Limekit suite 693 passed (from 666), Limer 39 checks. 2.1 (colon syntax) and 2.8–2.10 were started by a background agent, stopped by the owner, and finished/reviewed in the main session.

| # | Task | Status |
|---|---|---|
| 2.1 | **Colon calls on raw Qt objects fail.** `obj:method()` raises "takes no arguments (1 given)"; only `obj.method()` works. Every raw Qt object handed to Lua is a trap — including the close event at `widgets/window.py:233`, which breaks "unsaved changes?" prompts. Either wrap these objects or stop passing them (the `Container._key_name` note at `widgets/container.py:33` already chose wrapping) | `DONE` 2026-10-22 — general fix: one lupa attribute getter makes every Qt-native method colon-safe (`kernel/bridge/runtime.py`), retrying the literal call only when Qt refuses the arguments, so `w.isAncestorOf(w)` still works. Close veto: `onClose` returning `false` keeps a Window/Modal open; handlers get a `CloseRequest` (`ignore()`/`accept()`) instead of the raw QCloseEvent (`widgets/base.py`) |
| 2.2 | **Errors in `require`d files lose their line number.** The regex matches only `[string "..."]` (`kernel/errors.py:35`), so every multi-file app reports `line=None` and jump-to-error dies. Load file modules under a source name the parser recognises | `DONE` 2026-10-22 — a project searcher loads required files under project-relative names (`kernel/app.py`), so runtime and syntax errors report `scripts/lib/helper.lua:N` |
| 2.3 | **Builds silently break if `luac` is on PATH.** Bytecode is written under a `.lua` name (`build/lua_compiler.py:65`) and the 2.0 entry point reads it as UTF-8 text (`kernel/app.py:58`). Also: a failed `luac` is ignored (`lua_compiler.py:79-80`), and a system `luac` may be the wrong Lua version for lupa's 5.4 | `DONE` 2026-10-22 — no `luac` at all: the build stages the project as source (`build/staging.py`); `lua_compiler.py` removed |
| 2.4 | **A frozen app dies silently on a Lua error** — `build/entry_script.py` never catches `LuaError`. Show a message box | `DONE` 2026-10-22 — the 2.0 entry script shows the error in a message box (and stderr) and exits 1 |
| 2.5 | Build errors print to stdout but are parsed from stderr, so `onBuildError` never fires (`build/runner.py:415` vs `:515`) | `DONE` 2026-10-22 — markers read line by line from stdout and stderr; a failed (not only crashed) build also fires `onBuildError` |
| 2.6 | A project path containing `'` breaks the generated build script (`build/runner.py:400`) | `DONE` 2026-10-22 — every value in the generated build script and the spec goes through `repr()`; tested with `Bob's App` paths |
| 2.7 | Packaging bundles only `scripts/`, `images/`, `misc/`, `app.json`, `.require` (`build/spec_generator.py:67-116`) — any other data file is dropped silently. Bundle the project, or warn | `DONE` 2026-10-22 — the whole project ships, minus `.git`, `__pycache__`, top-level `build`/`dist`, `.preview`, `*.spec` |
| 2.8 | **Designer emits properties alphabetically** (`design_model.lua:633-646`), so `setCurrentIndex` lands before `setItems` and the index is lost. Order by dependency | `DONE` 2026-10-22 — content props (items, range) emitted before selection props (currentIndex, value) |
| 2.9 | A design named `images` overwrites the generated `scripts/designed/images.lua` (`files.lua:83`) — reserve the name | `DONE` 2026-10-22 — `images` reserved, with a clear message (`Files.validName`) |
| 2.10 | Generated design modules build their widgets at `require` time, so a designed dialog cannot be opened twice. Emit a factory function | `DONE` 2026-10-22 — generated modules export `M.new()`; README, code preview and tests updated |
| 2.11 | `None` inside a list makes a Lua hole (`kernel/bridge/convert.py:83-84`), so a SQL NULL truncates `ipairs` over a row | `DONE` 2026-10-22 — a list holding None gets `n` (Lua's `table.pack` convention); lists without None unchanged; documented on the db service |
| 2.12 | Correct the sandbox claims in `kernel/bridge/runtime.py:9-27`. `__import__` is still reachable via `widget.__class__.__init__.__globals__`, and `as_attrgetter`, `os` and `io` are available. Fine for trusted desktop code; document it honestly, and add an `attribute_filter` before anything loads third-party plugins or templates | `DONE` 2026-10-22 — comments now say plainly it is not a sandbox, and what a real boundary would need; no filter added |

---

## Phase 3 — Developer experience `TODO`

| # | Task | Status |
|---|---|---|
| 3.1 | Write `.luarc.json` into every new project so lua-language-server finds the bundled stubs with no setup (`project_creator.lua:137-213`) | `TODO` |
| 3.2 | Make `file.lua:42` in Limer's console clickable — jump to the file (needs 2.2) | `TODO` |
| 3.3 | Stop flagging any output line containing "error" as an error (`project_runner.lua:195-203`) | `TODO` |
| 3.4 | Let the user choose where projects live; today it is hardcoded to `Documents/limekit projects` (`app/core/config/paths.lua:10`) | `TODO` |
| 3.5 | More project templates than the single one — blank, form, table+SQLite, tabbed app | `TODO` |
| 3.6 | A test harness for *user* apps: a headless mode plus a Lua assertion helper, so an app's logic can be tested | `TODO` |
| 3.7 | A VS Code extension: stubs, syntax, a Run command | `TODO` |
| 3.8 | Hot reload — the watcher currently only refreshes the file tree (`project_watcher.lua`) | `TODO` |
| 3.9 | Document the generator order in CONTRIBUTING (done in the README; move or mirror it) | `DONE` 2026-10-22 |

---

## Phase 4 — The complex-app walls `TODO`

These are what stop Limekit being used for ambitious software. Ranked by how
much each unlocks.

| # | Task | Status |
|---|---|---|
| 4.1 | **Canvas / custom painting.** A `ui.Canvas` with an `onPaint` handler and a `Painter` object (lines, rects, text, images, paths). Unlocks editors, diagrams, games, visualisations. The pixel-editor demo is 1,024 `ui.Label`s *because this is missing* | `TODO` |
| 4.2 | **Drag and drop for app code.** `setDraggable`, `setDropTarget`, `onDrop`. The kanban demo says so itself at `2.0-examples/kanban/scripts/main.lua:13`. DesignSurface and ImageBrowser already do it internally — expose it | `TODO` |
| 4.3 | **Workers that carry data.** One Lua state means a worker running Lua blocks every handler, and `sys.Signal.relay()` takes no arguments (`services/concurrency.py:144`). Either a separate Lua state per worker exchanging messages, or a Python-side task API. Needed for anything that streams progress | `TODO` |
| 4.4 | **HTTP client.** `net.get`/`post`, async, JSON in and out. Nothing in a 2026 app framework can skip this | `TODO` |
| 4.5 | **Model-driven tables.** `Table` is item-based (`widgets/table.py:69`); 100k cells took ~1.1s and there is no virtualisation. A row-provider API would fix large data | `TODO` |
| 4.6 | **Settings storage** — a `QSettings` wrapper, so apps can remember window size and preferences | `TODO` |
| 4.7 | `System.execute` is synchronous, `shell=True`, 30s cap (`services/system.py:44-66`) — async, and argument-list form to kill the injection risk | `TODO` |
| 4.8 | Extend `require_gui_thread` to hand-written methods; today it guards generated setters only (`kernel/declarative.py:126`), so `appendText` and `setCellText` are unchecked | `TODO` |
| 4.9 | A sanctioned raw-Qt escape hatch, so a missing wrapper is never a dead end | `TODO` |
| 4.10 | Designer gaps: signal wiring, menus/toolbars, size policies, stylesheets, multi-select, custom widgets | `TODO` |
| 4.11 | i18n and accessibility | `TODO` |

---

## Phase 5 — Merge, release, launch `TODO`

| # | Task | Status |
|---|---|---|
| 5.1 | Merge `limekit-2.0` → `main` and `limekit-2.0-port` → `master`. **Until this happens every visitor reads the 1.x README** — 75 commits in Limekit and 30 in Limer are invisible | `TODO` |
| 5.2 | Tag `2.0.0` in both repos | `TODO` |
| 5.3 | CI release workflow: Windows, Linux and macOS builds attached to every GitHub Release | `TODO` |
| 5.4 | macOS: build on a GitHub `macos-latest` runner (free for public repos — no Mac needed). Document the Gatekeeper right-click→Open step until there is a signing certificate | `TODO` |
| 5.5 | Linux: an AppImage or tarball, plus the Qt system libraries listed in `docker/Dockerfile:19-24` | `TODO` |
| 5.6 | Publish the framework to PyPI for contributors (`pip install limekit`) — users still just download Limer | `TODO` |
| 5.7 | Settle the naming. Three names (Limekit, Limer, "Limer-Limekit") and a `Tools.rar` nobody can identify. Pick one story: **Limekit is the framework, Limer is the app** — and say it in one line at the top of both READMEs | `TODO` |
| 5.8 | Launch: Show HN, r/lua, r/neovim, r/programming, the Roblox DevForum, a PR to awesome-lua, and a write-up on the declarative kernel design | `TODO` |

**Do not start 5.8 until Phase 1 is done and Phase 2's build bugs are fixed.**
A first impression does not come back, and the single thing that will be tested
hardest by a stranger is "download it and make something run".

---

## Positioning (for the launch copy)

The pitch is **not** "a Lua wrapper over Qt". Python developers will use PySide
directly, and that framing invites the comparison.

The pitch is: **one download, and you write desktop apps in Lua.** The audience
is people who already know Lua and have never had a way to put a native window
in front of their code — Neovim users, Roblox/Luau developers, LÖVE and
game-modding people.

Two things no comparable project has, and both should be a GIF above the fold:

1. The **live Inspector** — pick a widget in a *running* app, edit its
   properties, run Lua inside it.
2. The **Designer** — real widgets in real layouts, generating clean Lua.

And the strongest line of all, once Phase 1 and 1.6 are done: **your users
don't need to install anything either.**
