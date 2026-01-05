# Dream Data Sources — Dataset Catalog

This file inventories major data sources useful for scientific/technical work on dreaming and dream-adjacent phenomena (dream reports, content annotations, and paired sleep physiology). It focuses on **publicly documented** datasets and repositories.

> **Note on ethics & licensing**
> Many “dream datasets” are personal narratives. Always check each source’s license/terms, de-identification status, and IRB/ethics requirements before use.

---

## Curated dream-report corpora (text)

### DreamBank (Domhoff & Schneider)
- **What it contains:** A large, anonymized archive of written dream reports from research studies and other structured sources (explicitly *not* from “dream-collecting websites”).
- **Scale:** “Over 20,000” dream reports on the landing page; an older methods paper describes “over 22,000” dream reports (as of May 2008), with substantial English and German content.
- **Modality / format:** Free-text dream narratives, organized into “sets” (groups) and “series” (individual journals).
- **Access:** Public web search interface; reports are “anonymized” (names/places changed).
- **Extra annotations:** Hall & Van de Castle (HVDC) codings are available for **2,000+ English** reports and **437 German** reports (per the DreamBank documentation/paper).
- **Primary links:**
  - Homepage: https://dreambank.net/
  - Methods paper (reprint): https://dreams.ucsc.edu/Library/domhoff_2008c.html

### Sleep and Dream Database (SDDb) — Kelly Bulkeley
- **What it contains:** A searchable library of dream reports plus demographic/sleep surveys.
- **Scale:** Site text describes **44,500+** dream reports from **16,000+** participants; the site also displays **“Database of 44,556 dream reports.”**
- **Modality / format:** Free-text dream narratives; survey/metadata fields for analysis.
- **Access:** Public web search and analysis tools.
- **Primary link:** https://sleepanddreamdatabase.org/

### SDDb snapshot export (Zenodo)
- **What it contains:** A **CSV export** of the entire SDDb dream-report library, intended for reproducible research/version control.
- **Scale:** The repository packages a file named `dream-export.csv` (tens of MB).
- **Access:** Open via Zenodo; includes documentation of how the export was obtained (blank search → export CSV).
- **Primary link:** https://zenodo.org/records/11662064

---

## Crowd-sourced / social dream-report corpora (text)

### Reddit r/Dreams corpus (as analyzed in Das et al., EPJ Data Science 2025)
- **What it contains:** Dream reports posted to Reddit’s **r/Dreams** community.
- **Scale:** The paper reports analysis of **44,213** dream reports.
- **Access:** The paper documents the corpus as a data source; actual redistribution of Reddit content may be constrained by Reddit’s policies and licensing.
- **Primary link (paper):** https://link.springer.com/article/10.1140/epjds/s13688-025-00554-w

---

## Dream reports paired with EEG/PSG or other sleep neurophysiology

### DREAM database (Dream EEG and Mentation database)
- **What it contains:** A standardized, FAIR-oriented database that **aggregates metadata** about studies/datasets that pair sleep M/EEG/PSG data with dream/mentation report classifications (and often raw reports), across labs.
- **Initial release scale (Nature Communications, 2025):** **20 datasets**, **505 participants**, **2,643 awakenings**.
- **Access:** The paper states the database can be accessed directly via **10.26180/22133105**. Datasets that are open can be downloaded via the “Data URL” field in the database’s “Datasets” table; restricted datasets require contacting the listed corresponding author.
- **Primary links:**
  - Paper (PMC mirror): https://pmc.ncbi.nlm.nih.gov/articles/PMC12350935/
  - Database DOI/landing: https://doi.org/10.26180/22133105
  - (Referenced in paper) Database table download: https://bridges.monash.edu/articles/dataset/The_DREAM_database/22133105?file=49774971

### Dream2Image (multimodal: EEG + dream text + AI-generated images)
- **What it contains:** Aligned **EEG segments preceding awakenings**, **verbatim dream report transcripts**, and **AI-generated images** derived from those reports.
- **Scale:** **38 participants**, **31+ hours** of EEG, **129** aligned dream samples; includes EEG windows at **T-15s, T-30s, T-60s, T-120s** before awakening.
- **Access:** Open access on Hugging Face (and described in an arXiv paper).
- **Primary links:**
  - Dataset: https://huggingface.co/datasets/opsecsystems/Dream2Image
  - Paper: https://arxiv.org/abs/2510.06252

---

## Sleep-physiology repositories useful for dream studies
*(Not necessarily paired with dream reports, but often used in dreaming/mentation research pipelines.)*

### Sleep-EDF Database Expanded (PhysioNet)
- **What it contains:** Whole-night polysomnography (PSG) recordings with **manual sleep-stage scoring** (hypnograms).
- **Scale:** **197** whole-night PSG recordings.
- **Signals:** EEG, EOG, chin EMG, event markers; some records include respiration and body temperature.
- **Access:** Open on PhysioNet; DOI listed on PhysioNet.
- **Primary links:**
  - Dataset: https://physionet.org/content/sleep-edfx/1.0.0/
  - DOI: https://doi.org/10.13026/C2X676

### Montreal Archive of Sleep Studies (MASS)
- **What it contains:** An open-access, collaborative PSG archive intended as a benchmarking resource for sleep-analysis algorithms.
- **Scale (paper abstract):** Whole-night recordings from **200 participants** pooled from multiple protocols/labs; includes standard PSG channels and respiration.
- **Access notes:** The abstract indicates access requires affiliation with a research institution and local ethics/IRB approval.
- **Primary links:**
  - Project page: https://ceams-carsm.ca/en/mass/
  - Paper (PubMed): https://pubmed.ncbi.nlm.nih.gov/24909981/

### National Sleep Research Resource (NSRR)
- **What it contains:** A large NHLBI-supported repository for sharing polysomnography, actigraphy, and questionnaire-based sleep data across cohorts/trials and other studies.
- **Scale (Sleep Research Society article, Apr 2025):** “Over **nine terabytes** of data from **50** unique datasets” (at time of writing).
- **Access:** Central portal at sleepdata.org; many datasets require application/approval (varies by study).
- **Primary links:**
  - Portal: https://sleepdata.org/
  - Repository description (re3data): https://www.re3data.org/repository/r3d100011861
  - Overview article: https://sleepresearchsociety.org/unlock-new-opportunities-in-sleep-research-with-the-nsrr/

### DREAMS Databases (sleep micro-events; Zenodo)
- **What it contains:** A family of PSG datasets and tools from the DREAMS project, including annotated micro-events (e.g., spindles, K-complexes, REMs) and an apnea dataset.
- **Example scale:** DREAMS Apnea Database includes **12** whole-night PSG recordings (expert-annotated respiratory events).
- **Access:** Open via Zenodo (with accompanying PDF documentation and code).
- **Primary link:** https://zenodo.org/records/2650142

---

## Derived / annotated dream datasets

### “Our Dreams, Our Selves” — HVDC-style automatic annotations for DreamBank reports (Dryad)
- **What it contains:** Algorithmic annotations of **20k+** DreamBank dream reports using an NLP operationalization of the **Hall–Van de Castle** coding system (e.g., characters, interactions, etc.).
- **Access:** Open dataset on Dryad (linked to a Royal Society Open Science paper describing the method).
- **Primary links:**
  - Dataset: https://datadryad.org/dataset/doi:10.5061/dryad.qbzkh18fr
  - Associated paper DOI (as listed on Dryad): http://dx.doi.org/10.1098/rsos.192080

---

## Mobile / app-based dream logging datasets

### The Dream Drop — Research Data Hub
- **What it contains:** Monthly, anonymized, geo-tagged dream logs (downloadable zip files) aimed at academic research use.
- **Access:** The site states data are available **exclusively for academic research** and require “appropriate credentials” (contact required).
- **Primary link:** https://thedreamdrop.com/research-files/

