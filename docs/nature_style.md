# Nature style for this manuscript

Read this before drafting or revising any part of the paper or any figure. The limits below were checked on 2026-11-04 against the journals' own pages:

- Nature Machine Intelligence, content types: https://www.nature.com/natmachintell/content
- Nature Machine Intelligence, formatting after acceptance: https://www.nature.com/natmachintell/submission-guidelines/aip-and-formatting
- Nature Human Behaviour, content types: https://www.nature.com/nathumbehav/content
- Nature Communications, Article: https://www.nature.com/ncomms/submit/article
- Nature's figure guide: https://research-figure-guide.nature.com/figures/

Check the target journal's page again before submission.

## Target journal and limits

The journal has not been chosen (open decision 8 in the code repo's `docs/design.md`). Until it is, write to Nature Machine Intelligence's limits. They are the tightest of the three candidates, so a text that fits them fits the other two.

| Article | Nature Machine Intelligence | Nature Human Behaviour | Nature Communications |
|---|---|---|---|
| Main text, excluding abstract, Methods, references and legends | 3,500 words | 5,000 words | about 5,000 words |
| Abstract | 150 words, unreferenced | 150 words, unreferenced | 200 words, no references |
| Display items (figures and tables) | 6 | 8 | up to 10 |
| References | about 50 | no limit | about 70 |
| Introduction | no heading | no heading | headed "Introduction" |
| Other | up to 10 Extended Data figures | | title at most 15 words; Methods usually under 3,000 words; each legend at most 350 words |

The `nature-check` skill counts the text against these limits.

Nature Machine Intelligence states that it edits papers heavily so that non-specialists can read them. Write for a reader from machine learning or behavioural science who does not know reputation-based learning or this codebase.

## Article structure

The parts in order, all in `main.tex`:

| Part | Rules |
|---|---|
| Title | Short and specific, sentence case, at most 15 words |
| Abstract | One paragraph, no references, no equations |
| Introduction | No heading (NMI, NHB) |
| Results | Topical subheadings |
| Discussion | No subheadings |
| Methods | Short subheadings |
| Data availability, Code availability | Required statements after Methods |
| References | One numbered list in order of first citation |
| Acknowledgements, Author contributions, Competing interests | After the references |
| Extended Data | Numbered apart from main figures |

Supplementary Information, when it is needed, is a separate document with its own numbering.

## Writing each part

Abstract. Readers outside the field read it first. A common order: one or two sentences of context, the gap, a sentence beginning "Here we", the main results with their numbers, and what follows from them. Define any abbreviation it uses, or avoid it.

Introduction. Move from the general problem to the specific gap the paper addresses, and close with a paragraph that says what this paper does and finds, usually opening with "Here we". Nature papers have no roadmap paragraph ("Section 2 describes ...").

Results. Each subsection answers one question. Its subheading states the finding as a short sentence ("X reduces Y") in place of a topic ("Analysis of Y"). Open a subsection with what was tested and why, give the result with its numbers and statistics, and cite the figure panels. Keep mechanics in Methods. One sentence of method in Results is fine when the reader needs it to follow the result.

Discussion. No subheadings. The first paragraph restates the main findings in plain terms. Then come interpretation, relation to prior work, limitations stated directly, and implications. Refer back to results without repeating their numbers.

Methods. Give enough detail to reproduce the work. Hyperparameters go in tables in Extended Data or the SI. Methods may cite new references; their numbers continue from the main text. The Code availability statement names the repository and, once archived, its DOI.

Supplementary Information. Items are Supplementary Notes, Figures, Tables and so on, each numbered on its own (Supplementary Note 1, Supplementary Fig. 1). Terms match the main text.

## Language

- Nature journals use British spelling (behaviour, modelling, colour, analyse), as do the code repo's docs. Copy editors impose house style after acceptance, so consistency matters more than any single choice.
- Use the active voice with "we". Use the past tense for what was done and found, and the present tense for what a figure shows and for established facts.
- Avoid claims of priority or novelty ("for the first time", "novel", "unprecedented"). Say what the work does; the comparison with prior work shows what is new.
- Define each abbreviation at first use, separately in the abstract and in the main text. Keep the set small (LLM, MARL, IPPO, PPO, SSD) and do not coin abbreviations for conditions or roles.
- Give each concept one name and keep it across text, figures and tables. The paper terms are listed in `AGENTS.md`.
- Use "significant" only for statistical significance, with the test named.
- No footnotes. Websites are cited in parentheses in the text, never in the reference list.
- The humanizer skill's patterns apply throughout. In scientific prose the usual offenders are inflated significance ("crucial", "pivotal"), stacked hedges, contrasts that set up a claim nobody made, and a closing sentence that repeats the result.

## Numbers, units and statistics

- Use numerals for measurements and counts, with a space before the unit (`5~pt`, `89~mm`) and commas in numbers of four digits or more in text (3,500).
- Variables are italic and units upright. Number the equations that the text refers to and cite them as "equation (1)".
- Follow the statistics plan in the code repo's `docs/design.md` §6.2. Every comparison gives n and what n counts (independent training seeds), the summary statistic (mean ± s.d., or median and interquartile range when outcomes are bimodal), the test (Mann-Whitney U, two-sided, with the multiple-comparison correction named) and the exact P value. P is an italic capital (`\textit{P} = 0.003`); below 0.001 write `\textit{P} < 0.001`.
- Report the size of a difference with an interval, not a P value alone.
- Take every number from its source in the code repo and note the source in a LaTeX comment (see `AGENTS.md`).

## Cross-references and citations

- Figures: Fig. 1, Fig. 1a, Fig. 1b,c, Fig. 2a-d (LaTeX `Fig.~\ref{fig:x}a--d`), Figs. 2 and 3. Also Table 1, Extended Data Fig. 1, Extended Data Table 1, Supplementary Fig. 1, Supplementary Table 1, Supplementary Note 1, equation (1).
- Cite figures in parentheses at the end of the clause they support, "(Fig. 2a)", in numerical order of first mention. Every Extended Data item is cited in the main text.
- References are superscript numbers placed after punctuation. In LaTeX, put `\cite` after the comma or full stop: `among strangers.\cite{santos2018social}`.
- Cite the published version of a paper when one exists. Unpublished work and papers in preparation are mentioned in the text with their authors, not listed.
- Datasets and code with a DOI may be cited in the reference list.

## Figures

The data figures come from the code repo's `analysis/` (see `AGENTS.md`). Its `analysis/style.py` applies these rules to matplotlib figures, and the `nature-check` skill checks any figure PDF against them, including draw.io exports.

### Rules for every figure

| Property | Requirement |
|---|---|
| Width at final size | 89 mm (one column), 120 or 136 mm (1.5 columns) or 183 mm (two columns). Nature Machine Intelligence's upload guide asks for at most 180 mm, so a two-column figure may need to shrink by 3 mm at acceptance |
| Height | At most 170 mm, leaving room for the legend |
| Font | Arial or Helvetica, embedded as editable TrueType; no Type 3 fonts and no text converted to outlines |
| Text size | 5-7 pt at final size |
| Panel labels | 8 pt bold upright lowercase (a, b, c) at the top left of each panel |
| Lines | 0.25-1 pt at final size |
| Colour | A colour-blind-safe palette (Wong, as in `analysis/style.py`), no red-green contrasts, and colour never the only cue: add markers, line styles or direct labels |
| Text colour | Black, or white on dark fills; explain colours with a key |
| Format | Vector PDF; any raster element at 300 dpi or more |
| Decoration | No gridlines, drop shadows, gradients or 3D effects |

### Conventions shared by all figures

- Each condition has one colour in every figure, taken from `COLORS` in `analysis/style.py`. Schematics use the same colours for the same things.
- Axis labels are in sentence case with the unit in parentheses, for example "Environment steps (millions)".
- Panels that are compared share axis ranges and sit on a common grid.
- Draw each figure at its final size and include it in LaTeX with `\natfig{...}`, which does not scale. A figure scaled in LaTeX no longer has 5-7 pt text.
- Schematics follow the same font, size and line rules as data figures and use flat colours.

### Legends

- Start with a bold title sentence that says what the figure shows, then describe each panel in order: `\caption{\textbf{Title.} \textbf{a},~... \textbf{b},~...}`. The caption package adds "Fig. 1 |".
- State what the centre values and the error bars or bands show, n and what it counts, the tests and P values, and any smoothing.
- Keep method detail in Methods. A legend explains only what is needed to read the panels.
- Keep each legend under 350 words (Nature Communications' limit). The `nature-check` skill reports every legend's length.

### Extended Data and Supplementary figures

Nature Machine Intelligence allows up to 10 Extended Data figures. Each fits on one page with its legend and follows the same rules as main figures, because the journal does not restyle them. Supplementary figures are for material that does not suit Extended Data. Each one also fits on one page with its legend.
