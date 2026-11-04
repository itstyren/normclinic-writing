# Agent notes

This repository holds the manuscript of the NormClinic paper, written for a Nature Portfolio journal.

## Rules for every task

1. Pass all prose you write through the humanizer skill (`humanizer:humanizer`) before it goes into a file. This covers manuscript and SI text, the abstract, figure legends, cover letters and responses to reviewers, whether you draft them or revise them. Use the skill's file mode when you edit a file and its embedded mode when the text is part of a larger task. It edits prose only: leave LaTeX commands, equations, labels, citation keys and bib entries alone, and check afterwards that no fact, number or citation was added or lost. Nature style needs en dashes (`--` in LaTeX) in ranges and paired names, as in `5--7~pt`, `Fig.~2a--c` and `Mann--Whitney`. Humanizer's dash rule targets dashes that join clauses, so these stay.
2. Follow Nature style in writing and figures, as set out in [docs/nature_style.md](docs/nature_style.md). Read it before drafting a section or checking a figure. Where another skill's defaults differ, this file and `docs/nature_style.md` win: the ARS skills default to APA 7.0, and `academic-paper-coauthor` is written for IEEE journals and AI conferences.
3. The code is the reference. Method descriptions, equations, hyperparameters, environment settings and condition names must match the implementation. When the paper and the code disagree, report the mismatch with the code's `file:line` and wait for my decision; do not change either side on your own.
4. Every number in the text needs a source in the code repo: a table or CSV built by `analysis/`, a config file, or a run's saved metadata. Put the source in a LaTeX comment at the end of the line, e.g. `% src: analysis/figures/harvest_final.csv`. If a number has no source yet, leave it out and say so in your report. Never estimate one.
5. Cite only references verified as described under References.
6. The code repo is read-only unless I ask for a change there.

## Code repository

The code lives in `/home/tyren/coding/self_model/norm-clinic`, online at https://github.com/itstyren/norm-clinic; its own agent notes are in `CLAUDE.md` there. This manuscript repository is https://github.com/itstyren/normclinic-writing.

| What you need | Where it is |
|---|---|
| The method as the paper reports it: roles, protocol, research questions, baselines, ablations, analysis plan, open decisions | `docs/design.md` |
| The design loop's code-level contract | `docs/design_loop.md` |
| Why each choice was made; may lag the code, and the code wins | `docs/decisions.md` |
| Code structure, norm sandbox, compilation | `docs/architecture.md` |
| Environment audits, event features, fixed and handcrafted norms | `docs/environments.md`, `normclinic/reputation/events/` |
| Matrix games and payoff sweeps | `docs/matrix.md` |
| Run artifacts and metrics | `docs/runs.md` |
| Hyperparameters | `configs/train/<scenario>.yaml`, `configs/train/<scenario>_llm.yaml` |
| Human-written norm intents | `configs/human/` |
| Role prompts, for the SI | `normclinic/designer/prompts/*.md` |
| Runs that stand for each condition | `analysis/registry/<scenario>.yaml` |
| How each reported number is computed | `analysis/summary.py` |
| Figure style, condition colours and display names | `analysis/style.py` |
| Figure notebooks and their PDF and CSV output | `analysis/notebooks/`, `analysis/figures/` |

`outputs/` holds the raw runs and is large; the tables built by `analysis/` hold what the paper needs.

`docs/design.md` §9 lists the decisions still open, the target journal among them. Before you write something that depends on one of them, check its current state and say so in your report.

### Paper terms and code names

The paper groups the model calls into four roles, so a paper term can cover more than one code component.

| Paper | Code |
|---|---|
| Reviewer | Reviewer (`prompts/reviewer.md`) |
| Advisor, with its trial memory | Advisor (`prompts/advisor.md`) and Trial Summarizer (`prompts/trial_summarizer.md`) |
| Designer | Designer (`prompts/designer.md`) |
| Arbiter, gate (wait or wake) | Scheduler decision call (`prompts/scheduler.md`) |
| Arbiter, adoption | Judge decision call (`prompts/judge.md`); `prompts/judge_blind.md` is the ablation that adopts without pilot evidence |
| Matrix games, Coins, Harvest Open, Clean Up | scenarios `matrix`, `coins`, `harvest`, `cleanup` |
| κ, the weight of the reputation advantage | `ppo.REPUTATION_KAPPA` |

The condition display names in `analysis/style.py` (`LABELS`) are placeholders. When the paper settles on a name, tell me, so that the figures can follow.

## Files

```text
main.tex               the manuscript
references.bib         verified references only
figures/               final figures, placed here by hand
docs/nature_style.md   writing and figure rules
.claude/skills/nature-check/   word-count and figure checks against Nature's limits
build/                 build output and figure previews (gitignored)
```

Write one sentence per line in `main.tex`, so that diffs and edits stay local.

`main.tex` defines `\natfig{path}`, which places a figure at its natural size, and the `extfigure` and `exttable` environments for Extended Data items, which Nature numbers apart from main figures.

## Build and checks

- `latexmk` builds `main.tex` into `build/main.pdf`. `.latexmkrc` matches the LaTeX Workshop setup in VS Code (pdflatex, output in `build/`).
- After a build, fix undefined references and citations before reporting back.
- Run the `nature-check` skill's text check after every change to the text, and its figure check for every figure added to `figures/`.

## Figures

I place the final figures in `figures/` by hand. Data figures are drawn in the code repo by `analysis/notebooks/` with `analysis/style.py`, which applies Nature's figure rules; changing one means changing the code repo, so it waits for my request. Include a figure at its final size with `\natfig{<name>.pdf}`. Scaling it in LaTeX would change its 5-7 pt text.

## References

- Add an entry only after checking it against its DOI record (`curl -sL https://api.crossref.org/works/<doi>/transform/application/x-bibtex`) or its arXiv record (`https://export.arxiv.org/api/query?id_list=<id>`). Prefer the published version and keep the arXiv ID in `eprint`. Never write an entry from memory, and never cite a paper you have only seen cited elsewhere without checking it.
- Keys are the first author's surname, the year and the first word of the title, in lower case: `santos2018social`.
- Journal names use Nature's abbreviations (`J. Theor. Biol.`, `Proc. Natl Acad. Sci. USA`). Titles are in sentence case, with proper nouns and acronyms in braces (`{SocialJax}`).
- The style is `naturemag.bst` with superscript numbers from natbib. Put `\cite` after punctuation.
- `/ars-citation-check` can audit the list; tell it the style is Nature's numbered style.
- For the final submission, paste the contents of `build/main.bbl` into `main.tex` in place of `\bibliographystyle` and `\bibliography`, as Nature journals ask.

## Working on a writing task

1. Read the parts of `docs/design.md` that cover the section, and the code they describe.
2. Draft or revise in `main.tex`.
3. Pass the prose through humanizer.
4. Check each number against its source and each term against the table above.
5. Build, and run the `nature-check` text check.
6. Report what changed and every mismatch with the code.
