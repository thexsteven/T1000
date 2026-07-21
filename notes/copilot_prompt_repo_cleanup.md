# Copilot Prompt — Clean, Thesis-Focused Workspace Structure

You are reorganizing the `t1000/` workspace so that a **thesis supervisor / examiner** who has never seen it before can orient themselves in under a minute. Optimize the top level for *reading and reviewing*, not for my personal scaffolding. Folder names in **English**.

## Hard rules — read first

1. **Do not move anything yet.** Work in two phases (below). Phase 1 is inventory + a written plan; only after I approve do you execute Phase 2.
2. **Use `git mv`** for every move/rename so Git history is preserved. This is a git repo with modified and untracked files — commit or note the current state before touching anything.
3. **Update every reference** you break: paths in `AGENTS.md`, in any `.md`, in `.html` (relative `src`/`href`/`fetch` paths, including the dashboard served on `127.0.0.1:8001`), and in `.py` files. After moving, grep the whole workspace for the old paths/filenames and fix them.
4. **`AGENTS.md` stays at the repo root** — it is the session-context file you read on startup; do not move or rename it.
5. **`session-handoffs/` and its `LATEST.md` symlink** are a coupled session-continuity system. Keep the folder at root unless you can fully update the symlink target and all `AGENTS.md` references; if in doubt, leave it at root.
6. **Do not open, edit, or delete the contents** of `t1000.backup-20260720122415/`. Move the folder as a whole into `archive/`.
7. **Never delete a file.** If something looks obsolete, move it to `archive/`, don't remove it.

## Phase 1 — Inventory and propose (stop and wait for my OK)

1. List every file and folder in `t1000/`, including the contents of `cycle_overlay/`, `outputs/`, and `session-handoffs/`.
2. For each item, state in one line: what it is, and which of my three thesis contributions or support categories it belongs to:
   - **Decision Tree** (e.g. `preprocessing_decision_tree.html`, `entscheidungsbaum_einfach.html`, criteria analyses)
   - **Data Pool** (validation/selection code, `pool_cycles.parquet`, generated outputs)
   - **HTML Cycle Visualization** (`cycle_overlay/`)
   - **Documentation / reasoning** (pipeline structure, dashboard architecture/review)
   - **Internal scaffolding** (weekly plan, copilot prompts, session handoffs)
   - **Config / examples** (`.yaml`, `.json`)
   - **Backup / obsolete**
3. Propose a target tree along these lines (adjust names if something fits better, but keep it this simple — no deep nesting):

   ```
   t1000/
   ├── README.md            # NEW — entry point (see Phase 2)
   ├── AGENTS.md            # unchanged, stays at root
   ├── .gitignore           # unchanged
   ├── docs/                # written documentation & reasoning
   ├── deliverables/        # the HTML results a reviewer opens
   ├── src/                 # code (cycle_overlay + validation/selection scripts)
   ├── config/              # yaml / json configuration & examples
   ├── notes/               # weekly plan, copilot prompts, other scaffolding
   ├── session-handoffs/    # unchanged, stays at root
   └── archive/             # backup + anything obsolete
   ```
4. Show the proposed move for every file as an explicit `old path → new path` list, and flag any move that would break a reference and how you will fix it.
5. **Stop here and wait for my confirmation.**

## Phase 2 — Execute (only after I approve)

1. Perform the moves with `git mv` in the approved order.
2. Fix all references (rule 3) and verify by grepping for the old paths — there should be zero remaining hits.
3. Create a concise **`README.md`** at the root as the reviewer's entry point. It should contain, in this order:
   - one-paragraph purpose of the project (data-quality preprocessing layer on top of the existing pipeline);
   - a short "Where to look" section mapping the three contributions (Decision Tree, Data Pool, HTML Visualization) to their folders/files;
   - a one-line description of each top-level folder;
   - a note that `AGENTS.md` and `session-handoffs/` are working context, not deliverables.
4. Report what changed and confirm nothing references the old locations.

## Optional follow-up (propose separately, do NOT bundle into Phase 2)

Some files have German names (`entscheidungsbaum_einfach.html`, `t1000_leitfaden_quellen.html`, `t1000_wochenplan.md`). Renaming them to English would improve consistency but is more disruptive (breaks references, git history, and possibly the served dashboard URL). List the proposed renames as a **separate** step for me to approve individually — do not rename files as part of the structural move.
