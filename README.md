# Analysis code for displaced vertexing study with K-short mesons

### Prerequisites
This code requires a specific input file format.
It runs on ROOT ntuples that have been produced from MiniAOD with a custom ntuplizer.
Apart from standard lepton and jet analyzers, a custom analyzer for V0 reconstruction
was added in the ntuplizer.

### Workflow
Starting from the ntuples produced by the ntuplizer (usually with CRAB),
the following steps should be performed:
- skimming: select clean Z to mu+ mu- events, see skimming folder.
- v0building: select V0 candidates and calculate their properties, see v0building folder.
- analysis: compare V0 properties between data and simulation, see analysis folder.
