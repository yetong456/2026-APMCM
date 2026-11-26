# Problem D manuscript and reproducible experiments

[D_review.pdf](D_review.pdf) is the English manuscript. The review copy leaves the team number for its registered authors to complete. The summary, contents, main text, references and full program listings are in the PDF. The two full candidate pools were solved with the local Kaiwu CPU exact optimizer. There was no SPQC device experiment.

| File | Contents |
|---|---|
| [main.tex](main.tex) | Editable manuscript entry point |
| [artifacts/q1_holdout.csv](artifacts/q1_holdout.csv) | 3,703 composition-only Q1 predictions, trained on 02 |
| [artifacts/q23_full.csv](artifacts/q23_full.csv) | 8,112 frozen predictions from the 02+03 refit, including every Q2 row |
| [artifacts/score_runs.csv](artifacts/score_runs.csv) | SHA-256 digests and feature, fitting and prediction times |
| [artifacts/selections.csv](artifacts/selections.csv) | Exact Kaiwu selections for pools 07 and 08, pool runners-up and enumeration gaps |
| [artifacts/blind_minima.csv](artifacts/blind_minima.csv) | Direct scans of blind subsets 11 and 12 |
| [artifacts/block_runs.csv](artifacts/block_runs.csv) | All 338 nine-spin calls, block indices (alphabetical element order), ground-state tie counts, original scores and timings |
| [artifacts/group_folds.csv](artifacts/group_folds.csv) | Five-fold grouped development results |
| [artifacts/capacity_control.csv](artifacts/capacity_control.csv) | Matched-descriptor direct fits with 350, 700 and 1,050 trees versus the frozen mixture, two seeds and three pools |
| [artifacts/costs.csv](artifacts/costs.csv) | Timings, calls, integer ranges and tie counts |

The paper contains nine figures in the main text and two in the appendix. Each is a native vector PDF made from the underlying data or ideal cubic coordinates. The [Q3 budget comparison](figures/q3_budget.pdf) shows both 50-candidate hit counts and rank-one regret on the same 1,701 validation rows. The [integer tie example](figures/tied_block.pdf) links four minimum-cost cells to their original scores. Model colors, markers and element colors are shared across figures. The [three-family score maps](figures/family_landscapes.pdf) are a further figure in the supporting archive.

The gate replay checks the 3,969 archived seed-26 predictions. The separate capacity control replays the direct and mixture baselines for seeds 26 and 42, then refits larger direct models on file 02. Its 700-tree budget matches nominal training-row passes and its 1,050-tree budget matches the mixture's component tree count. Fitting times are measured separately for each run. Pair-bootstrap and seed-overlap results appear in [shortlist_sensitivity.csv](artifacts/shortlist_sensitivity.csv).

## Reproduce the numbers

From the repository root, use a Python 3.12 environment with the packages listed in `problem_d/requirements-lock.txt`. Keep all original D CSV files and the organizer's SHA-256 manifest and data notes in `problem_d/date/`. If starting from the support archive, supply this folder from the competition download. The official manifest also includes the original Chinese-named data notes.

The commands below use PowerShell and assume that `python` invokes the selected environment. Timing columns depend on machine load. With the repository or extracted support ZIP, the stored results are sufficient to compile the paper. Regenerating plots that read public properties or rerunning the experiments also requires the organizer’s original CSV files.

```powershell
python problem_d/exploration/audit_data.py
foreach ($seed in 26,42) {
    python problem_d/exploration/compare_surrogates.py --seed $seed --predictions "problem_d/results/validation_seed$seed.csv"
    python problem_d/exploration/test_innovation_ideas.py stress --seed $seed --predictions "problem_d/results/stress_seed$seed.csv"
    python problem_d/exploration/compare_physical_properties.py --seed $seed --predictions "problem_d/results/physical_seed$seed.csv"
}
python problem_d/exploration/test_innovation_ideas.py encoding --seed 26 --predictions problem_d/results/encoding_seed26.csv
python problem_d/exploration/audit_sdk_precision.py
python problem_d/paper/screen.py scores
python problem_d/paper/screen.py development
python problem_d/paper/solve.py
python problem_d/paper/gate_audit.py
python problem_d/paper/capacity_audit.py
python problem_d/paper/mechanisms.py
python problem_d/paper/figures.py
python problem_d/paper/material_figures.py
python problem_d/paper/perovskite_plates.py
python problem_d/paper/crystal_scenes.py
python problem_d/paper/tables.py
```

The Q1 predictions use seed 26 and the 02-only model. The Q2/Q3 refit uses the same seed and features. The SDK's public exact CPU solver works on these small blocks without interactive activation in the tested installation. The separate simulated-annealing backend prompted for official authorization. The paper's cost comparison uses the CPU backend.

## Compile the manuscript

With TeX Live and the APMCM template dependencies installed, run from this directory in PowerShell. The template class and configuration are included under `sources/latex/`. Install the template dependencies, including ctex, xeCJK, ulem, cprotect, bigfoot, appendix, placeins and needspace. The class uses Times New Roman when installed, then tries TeX Gyre Termes and Liberation Serif. Page breaks can vary with the chosen font.

```powershell
$env:TEXINPUTS = '.;../../sources/latex;' + $env:TEXINPUTS + ';'
xelatex -halt-on-error -interaction=nonstopmode -jobname=D_review main.tex
xelatex -halt-on-error -interaction=nonstopmode -jobname=D_review main.tex
xelatex -halt-on-error -interaction=nonstopmode -jobname=D_review main.tex
```

To insert the real registration number, set `\baominghao{}` in the entry file, rebuild and use the organizer's team-specific file name. The signed control sheet is a separate team document.

