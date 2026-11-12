# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. It is a living document; extend it as the work goes on.

## What this is
The analysis framework for a CMS displaced-vertexing study with V0s (K0S, Λ). It compares data and simulation for the number of reconstructed K0S as a function of the radial displacement Δ2D (`_RPV`) in Z→μμ events, after normalizing simulation to data at small Δ2D. Results go into AN-20-111 and DP-2024-010 (TRK POG). The study was first done on Run 2 (pre-UL/UL); active work is on Run 3 (2022–2025).

## Related repository: the ntuplizer
- **Current (Run 3):** `/user/jbierken/CMSSW_15_0_17/src/V0Analysis/V0Analyzer`, a separate git repo with its own `CLAUDE.md`. It is a CMSSW `EDAnalyzer`, forked from heavyNeutrino/multilep, that rebuilds V0s from `packedPFCandidates`+`lostTracks` (`src/K0Analyzer.cc`). It writes `blackJackAndHookers/blackJackAndHookersTree` plus `hCounter`, `nVertices`, `nTrueInteractions`. CRAB output goes to `/pnfs/iihe/cms/store/user/jbierken/K0sAnalysis/NTuples/MINIAOD/{data,sim}/v<N>/`.
- **Legacy (Run 2):** `ntuplizer/heavyNeutrino` in this repo. It is kept for reference only and is not built or used.
- Jet tagging in the ntuplizer is being reworked (DeepJet → ParticleNet/UParT for Run 3). The ntuplizer output must keep matching what `skimming/skim_ztomumu.cc` reads. See [Interface contract](#ntuplizer--skimmer-interface-contract).

## Pipeline
All steps run with CMSSW sourced (`cmsenv` in `CMSSW_15_0_17`, python3, ROOT, uproot, awkward). Most scripts use relative paths (`sys.path.append('../')`, `python3 ../plotting/...`), so **run them from their own directory**.

1. **Skim** (`skimming/`): `make -f make_skim_ztomumu`, then `./skim_ztomumu <in> <out>`, or batch via `skim_submit.py -i <samplelist> -o <outdir>`. The selection keeps events with exactly 2 POG-medium muons (pT > 30/25 GeV, |η| < 2.4, opposite charge), `_passTrigger_mm`, |mμμ − mZ| < 10 GeV and no b-tagged jet (DeepJet `b+bb` > loose WP from `bTagThreshold(campaign, year)`). It adds `_nimloth_*` (event) and `_celeborn_*` (muon) branches. Campaign and year are parsed from the **input file path** (`getYearFromFileName`).
2. **V0 building** (`v0building/`): `v0builder.py -i <in> -o <out> [-s legacy]`, batch via `v0builder_submit.py`, merge via `merge.py`/`mergeeras.py`. Selection is in `v0selections.py::selection_legacy`. It writes trees `laurelin` (K0S) and `telperion` (Λ) with `_RPV`, `_RPVSig`, `_mass`, `_pt`, `_eta`, `_phi`, `_weight`, `_nTrueInt`, …, and copies `hCounter`.
3. **Analysis** (`analysis/`), driven by `mcvsdata_submit.py`:
   ```bash
   cd analysis
   python3 mcvsdata_submit.py -i <filedir> -v run3 -c config_ksvars.py -o <outdir> \
       [-e default|perera|<era> ...] [--runmode local|condor] [--fitstrategy legacy|adaptive]
   ```
   - `-v/--version` ∈ `run2preul`, `run2ul`, `run3`. `-e default` uses the hard-coded era list in the submit script, which gets edited often.
   - `mcvsdata_getfiles.py` maps eras to input files (MC dir names in `mcdirdict`, data in `datadirdict`), luminosities (`tools/lumitools.py`) and the DY cross-section (6688 pb for Run 3).
   - For each era × variable × bkgmode × normalization × binning, the submit script writes `config.json`, `variable.json`, optionally `sidevariable.json`/`normvariable.json`/`yvariable.json`, into `<outdir>/<era>/<var>_<bkg>_<norm>_<bins>/`. It then runs `mcvsdata_fill.py` (→ `histograms.root`) and `../plotting/mcvsdataplotter[2d].py` (→ png).
   - Variable configs: `config_ksvars.py`, `config_ks2dvars.py`, `config_lavars.py`, `config_controlvars.py`, `config_ksvars_detector.py` (each exports a `config` dict). `configs_old/` is unused.
   - `mcvsdata_submit_all.py` is an older Run 2 convenience looper with hard-coded `/pnfs/.../llambrec/` paths.

## `analysis/mcvsdata_fill.py` (core logic)
- `get_histogram(...)` processes one file and returns `(counts, errors, confidence, confidence_error)`.
- MC weights: `_weight`, multiplied by the pileup reweight (`reweighting/pileup/pileupreweighter.py`, `PileupReweighter(campaign, year_pu)`). They are normalized to their own sum, then scaled by xsec×lumi. Per-era names (e.g. `2024C`, `2022postEEF`) are mapped back to the pileup year by stripping era letters.
- **MC even/odd split (2024/2025):** both years use the 2024 MC sample. `splitparity` (`even` → 2024, `odd` → 2025) comes from `get_mc_split_info` in `mcvsdata_getfiles.py` and is applied as a hash of event/run number, so the two halves are statistically independent. Every branch read must be masked with `splitmask` consistently.
- **Background modes:** `None` (plain histogram) or `sideband`. In sideband mode, every bin of the main (and y) variable gets an invariant-mass fit via `fitting/count_peak.py::count_peak_unbinned(mode='hybrid', fit_strategy=...)`, and fit plots go to `--sideplotdir`.
- **Normalization modes:** `lumi`, `yield`, `eventyield` (uses the `nimloth` tree), and `range`. `range` scales total simulation to data in the `normvariable` range, typically `_RPV` ∈ [0, 0.5] cm, and is the main physics result.
- If `--normmode` is not given, simulation xsec and lumi are set to 1.

## Fitting (`fitting/count_peak.py`, `tools/fittools.py`)
The signal model is a Gaussian or double Gaussian on a pol1/pol2 background in the K0S mass window 0.44–0.56 GeV.
- `--fitstrategy legacy` (default) chooses the model from effective-entry thresholds (1000 and 20000).
- `--fitstrategy adaptive` fits all four combinations and keeps the best χ²/ndf. See `ADAPTIVE_STRATEGY_SUMMARY.md`.
- Each TF1 needs a unique name (`funcname`) when several are fitted on one histogram.

## Ntuplizer ↔ skimmer interface contract
`skimming/skim_ztomumu.cc` breaks quietly when this contract drifts. Check it whenever the V0Analyzer changes:
- The tree path is `blackJackAndHookers/blackJackAndHookersTree`. Histograms in that directory are copied over.
- Fixed array sizes must match the ntuplizer headers: `nL_max = 20` (`LeptonAnalyzer.h`), `nJets_max = 100` (`JetAnalyzer.h`).
- Branches read: `_nL`, `_nLight`, `_nMu`, `_lPOGMedium`, `_lPt`, `_lEta`, `_lPhi`, `_lE`, `_lCharge`, `_passTrigger_mm`, `_nJets`, `_jetPt`, `_jetEta`, `_jetPhi`, `_jetDeepFlavor_b`, `_jetDeepFlavor_bb`. The skim assumes muons are stored first in the lepton arrays.
- Switching the b-veto tagger (e.g. to `_jetParticleNet_BvsAll`) requires changing the branch reads, the `SetBranchStatus` re-enables and the WP table in `bTagThreshold`.
- Downstream, `v0building/v0builder.py` reads `_V0*` branches, `hCounter` and `nTrueInteractions` from the same directory.

## Skimmer pitfalls (fixed 2026-11-12, keep in mind)
- Any branch read in the skim event loop must be re-enabled after the `SetBranchStatus("_jet*", 0)`-style disables, because `GetEntry` does not fill disabled branches. `_jetPt` was missing, so the jet pT cut and the b-veto did nothing. Skims made before the fix (all of `/pnfs/.../K0sAnalysis/skim_results/run3/` as of 2026-11-12) effectively have **no b-veto**, and `_nimloth_nJets` is ~0 in them.
- `getYearFromFileName` must check sub-campaigns before their parent year (2022EE before 2022, 2023BPix before 2023). Data is matched on the era (Run2022E/F/G, Run2023D) and MC on the campaign name (`Run3Summer22EE`, `RunIII2024Summer24`, …). Unknown years now throw in `bTagThreshold` instead of silently returning 0.
- Test the skimmer without real ntuples by compiling a harness that does `#define main skim_main` + `#include "skim_ztomumu.cc"`. Build it inside `cmsenv`: the system ROOT in `/usr/bin` lacks `Math/Vector4D.h`.

## Known issues (open)
- In 2024 MC (the `RunIII2024Summer24MiniAODv6` skims), `_jetDeepFlavor_b/_bb` are all −1000, meaning the tagger label is missing in the ntuple. The b-veto can therefore never fire for 2024/2025 MC, while it can in data. This is being addressed in the V0Analyzer jet-tagging rework.
- In the `normmode=='range'` block of `mcvsdata_fill.py`, `file_total` is computed but no longer used (it was a leftover diagnostic).
- `mcvsdata_submit.py` hard-codes `CMSSW = '/user/jbierken/CMSSW_15_0_17'`.

## Conventions
- Tree names follow Tolkien naming: `laurelin` (K0S), `telperion` (Λ), `nimloth` (event-level), `celeborn` (muon branches).
- The repo is checked out under both `/ada_mnt/ada/user/jbierken/...` and `/user/jbierken/...`; these are the same files.
- `results/` holds committed example configs (Run 2 UL). Generated outputs (root/png) are not committed.
- There is no test suite or linter. `python3 -m py_compile` is the minimal check; real runs need the CMSSW environment and access to `/pnfs`.
