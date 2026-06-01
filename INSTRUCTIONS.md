# NexaCore Active Directory Identity Governance — Project Instructions

## 1. Project Overview
- **Short Description:** Graph-theoretic analysis of NexaCore's Active Directory topology to identify hidden privilege escalation paths from standard user accounts to Domain Admin.
- **Description:** This project models NexaCore's Active Directory environment as a directed graph and applies graph-theoretic analysis — shortest paths, centrality metrics, and reachability — to surface hidden privilege escalation routes. Using a synthetic but operationally realistic 175-principal topology (160 human users, 15 service accounts, 32 groups, 261 membership edges), the analysis demonstrates how six deliberate misconfigurations create multi-hop paths from unprivileged accounts to Domain Admin access. The project is intended to serve as a practical framework for identity governance reviews and AD security assessments in financial services environments.
- **Abstract:** Active Directory misconfigurations are among the most consistently exploited attack vectors in enterprise environments, yet they remain invisible to conventional access reviews. Point-in-time user-permission reports cannot surface the cumulative effect of nested group memberships accumulated over years of organic growth. This project applies graph theory to NexaCore's synthetic AD topology — 175 principals, 32 groups, and 261 membership edges — to answer a question that static reporting cannot: which standard accounts hold an unbroken chain of group memberships leading to Domain Admin? Using `igraph` and `tidygraph` in R, the analysis constructs the full privilege graph, computes shortest escalation paths, and ranks groups by betweenness centrality to identify which nodes serve as critical connectors in every escalation route. Six deliberate misconfigurations — spanning stale project memberships, over-provisioned service accounts, and a legacy pentest account never deprovisioned — create paths as short as four hops from a Finance Analyst to full domain control. The findings translate directly into a prioritized remediation backlog, demonstrating that graph-based identity analysis is both technically tractable and board-communicable.
- **Target Audience:** Information security leadership, enterprise risk officers, and board-level risk committees
- **Output Format:** HTML (self-contained)
- **Render Command:** `quarto render index.qmd`
- **Expected Output Path:** `output/index.html`
- **Data Sources:**
  - `data/users.csv` — 175 principals (160 human, 15 service); generated synthetically via `generate_ad_data.py`
  - `data/groups.csv` — 32 groups across 4 privilege tiers
  - `data/memberships.csv` — 261 membership edges (user→group and group→group), misconfiguration-flagged
  - `data/group_nesting.csv` — group→group subset for graph construction
  - `data/ou_structure.csv` — OU hierarchy reference
- **Project Status:** In Progress

---

## 2. Directory Structure

```
nexacore_ad_project/
├── data/                    # Raw synthetic AD datasets (CSV)
│   ├── users.csv
│   ├── groups.csv
│   ├── memberships.csv
│   ├── group_nesting.csv
│   └── ou_structure.csv
├── scripts/                 # Helper R scripts
│   └── pipeline_diagnostic.R
├── output/                  # Rendered HTML output
├── _brand.yml               # Brand configuration
├── _quarto.yml              # Project-level Quarto configuration
├── INSTRUCTIONS.md          # This file
└── index.qmd                # Main Quarto entry point
```

---

## 3. Document Sections — Required & Ordered

  3.1  **Setup** — Libraries, brand colors, theme_brand() definition, data ingestion
  3.2  **Introduction** — Problem statement: why static AD reviews miss escalation paths; NexaCore context
  3.3  **The NexaCore AD Topology** — Descriptive overview of the synthetic environment: principal counts, department distribution, group tier structure, OU hierarchy; 1–2 tables
  3.4  **Graph Construction** — Building the directed privilege graph with `igraph`/`tidygraph`; node and edge attribute assignment; graph summary statistics
  3.5  **Privilege Escalation Path Analysis** — Shortest-path analysis from standard users to Domain-Admins; the six misconfiguration edges; path trace visualizations (ggraph); narrative walkthrough of the most critical escalation chains
  3.6  **Centrality & Critical Nodes** — Betweenness centrality ranking; which groups serve as critical connectors in every escalation route; visualization of the full privilege graph colored by centrality and tier
  3.7  **Blast Radius Assessment** — For each misconfiguration, how many principals have a path to Domain-Admins through that edge; quantifying exposure
  3.8  **Remediation Prioritization** — Ranked remediation backlog derived from the graph analysis; effort vs. exposure matrix
  3.9  **Key Takeaways & Conclusion** — 2–3 insights (300–400 words) + conclusion (150–200 words); written as prose per writing standards
  3.10 **Session Information** — `sessioninfo::session_info()` chunk, `echo: false`
  3.11 **Footer** — Rendered with Quarto + package attribution line

---

## 4. YAML Header

```yaml
---
title: "Mapping the Invisible: Active Directory Privilege Escalation Through Graph Analysis"
subtitle: "An Identity Governance Case Study — NexaCore Financial Technologies"
author: "Patrick Lefler"
abstract: |
  Active Directory misconfigurations are among the most consistently exploited attack vectors
  in enterprise environments, yet they remain invisible to conventional access reviews.
  Point-in-time user-permission reports cannot surface the cumulative effect of nested group
  memberships accumulated over years of organic growth. This project applies graph theory to
  NexaCore's synthetic AD topology — 175 principals, 32 groups, and 261 membership edges —
  to answer a question that static reporting cannot: which standard accounts hold an unbroken
  chain of group memberships leading to Domain Admin? Using igraph and tidygraph in R, the
  analysis constructs the full privilege graph, computes shortest escalation paths, and ranks
  groups by betweenness centrality to identify which nodes serving as critical connectors in
  every escalation route. Six deliberate misconfigurations — spanning stale project
  memberships, over-provisioned service accounts, and a legacy pentest account never
  deprovisioned — create paths as short as four hops from a Finance Analyst to full domain
  control. The findings translate directly into a prioritized remediation backlog,
  demonstrating that graph-based identity analysis is both technically tractable and
  board-communicable.
date: June 3, 2026
format:
  html:
    code-fold: true
    code-copy: true
    code-overflow: wrap
    code-tools: false
    code-summary: "Display code"
    df-print: kable
    embed-math: true
    embed-resources: true
    fig-align: center
    fig-height: 6
    fig-width: 10
    highlight-style: arrow
    lightbox: true
    linkcolor: "#0166CC"
    number-sections: false
    page-layout: full
    smooth-scroll: true
    theme: sandstone
    toc: true
    toc-depth: 3
    toc-location: right
    toc-title: "Contents"
execute:
  echo: true
  warning: false
  message: false
html-math-method: mathjax
knitr:
  opts_chunk:
    comment: "#>"
---
```

---

## 5. Brand & Theme Configuration

`_brand.yml` is present in root. See file for full specification.

Brand color variables (defined in Setup chunk):
```r
brand_primary   <- "#1A1A2E"
brand_secondary <- "#16213E"
brand_accent    <- "#0F3460"
brand_highlight <- "#E94560"
brand_surface   <- "#F5F5F5"
brand_text      <- "#1A1A2E"

brand_palette <- c(
  primary   = brand_primary,
  secondary = brand_secondary,
  accent    = brand_accent,
  highlight = brand_highlight
)
```

Graph-specific color mapping (tier-based node coloring):
```r
tier_colors <- c(
  "1" = brand_highlight,   # Domain-Admins — red/highlight
  "2" = brand_accent,      # Privileged infrastructure — deep blue
  "3" = brand_secondary,   # Department senior/manager groups
  "4" = brand_surface,     # Standard department groups
  "human"   = "#4A90D9",   # Human user nodes
  "service" = "#E8A838"    # Service account nodes — amber warning
)
```

---

## 6. Visualization Rules

- Default stack: `ggraph` (graph layouts) → `ggplotly()` → `plotly` direct
- `ggraph` is the primary tool for all graph visualizations; use `layout = "sugiyama"` for DAG-style privilege hierarchy, `layout = "fr"` (Fruchterman-Reingold) for the full topology view
- `scale_fill_manual` / `scale_color_manual` applied throughout using `brand_palette` and `tier_colors`
- Misconfiguration edges rendered in `brand_highlight` (#E94560) with increased stroke width
- Escalation path traces rendered as highlighted subgraphs over a muted full-graph background

---

## 7. Table Rules

- Default: `kable` + `kableExtra` → `gt` → `DT::datatable()`
- Default kable setup:
```r
kable(
  data,
  format    = "html",
  digits    = 3,
  caption   = "Table N: [Description]",
  col.names = c("Col 1", "Col 2", "Col 3")
) |>
  kable_styling(
    bootstrap_options = c("striped", "hover", "condensed"),
    full_width        = TRUE,
    position          = "left",
    font_size         = 13
  )
```
- `DT::datatable()` used for the full membership edge list (261 rows) where interactive filtering adds value

---

## 8. R Libraries

```r
library(kableExtra)   # Table formatting
library(knitr)        # Document rendering
library(plotly)       # Interactive chart wrapping
library(scales)       # Axis and label formatting
library(sessioninfo)  # Session provenance
library(tidyverse)    # Data manipulation and ggplot2

# Project-specific
library(igraph)       # Core graph construction, path analysis, centrality
library(tidygraph)    # Tidy API for igraph objects
library(ggraph)       # Graph visualization (ggplot2 extension)
library(DT)           # Interactive datatable for edge list exploration
```

---

## 9. Writing Standards

- Voice: Third person, direct, precise
- Grammar: Vary sentence length deliberately. Avoid flat, homogeneous AI-generated rhythm.
- Structural Rules: Lead with the non-obvious insight, not the methodology. One idea per paragraph. No bullet-point dumps masquerading as analysis. Lists for genuinely enumerable items only. Minimize em-dashes.
- Banned vocabulary: delve, leverage (verb), harness, unlock, seamlessly, robust (outside statistical context), transformative, elevate, navigate (metaphor), landscape (metaphor), ecosystem (metaphor), paradigm, game-changer, cutting-edge, state-of-the-art, empower, innovative (unless citing a specific novel technique), holistic, synergy, streamline, deep dive (noun), unpack (metaphor), "it's worth noting", "it is important to note", "in today's world", "in conclusion" (never opens a closing paragraph)
- Domain-specific terms to use consistently:
  - **Principal** — any user or service account (never "account" generically)
  - **Domain-Admins** — always hyphenated, always capitalized as a proper noun when referring to the group
  - **Privilege escalation path** — preferred over "attack path" in governance contexts
  - **Misconfiguration** — preferred over "vulnerability" for AD group nesting issues
  - **Blast radius** — acceptable technical term; use consistently in Section 3.7
  - **Tier** — the four-level group hierarchy (Tier 1 through Tier 4)
- Number formatting: Percentages: one decimal place (99.2%). Monetary values: $X,XXX. Statistical intervals: bracket notation [lower, upper].
- Figures and tables carry their own narrative weight — captions should add information, not repeat axis labels.

---

## 10. Deliverables Checklist

- [ ] `index.qmd` — primary rendered document
- [ ] `_brand.yml` — confirmed in root
- [ ] `README.md` — complete
- [ ] Abstract — embedded in YAML, ~200 words
- [ ] Output HTML — confirmed self-contained (`embed-resources: true`)
- [ ] LinkedIn post (if requested)

---

## 11. README.md Structure

```
# Mapping the Invisible: Active Directory Privilege Escalation Through Graph Analysis

> An identity governance case study demonstrating how graph theory surfaces hidden privilege escalation paths in enterprise Active Directory environments.

Author: Patrick Lefler
Published: June 3, 2026
Rendered: [leave blank]

## Overview
...

## Tech Stack
- Language: R
- Framework: Quarto
- Primary Libraries: tidyverse, igraph, tidygraph, ggraph, kableExtra
- Output: Self-contained HTML

## Repository Structure
...

## Key Findings
...

## License
MIT License.

## Contact
Patrick Lefler | https://www.linkedin.com/in/patricklefler/ | patrick-lefler.github.io | https://substack.com/@pflefler
```

---

## 12. Open Issues & Decisions Log

- [2026-06-01] — Abstract word count: currently ~200 words; confirm acceptable or trim to 150
- [2026-06-01] — Graph layout selection: `sugiyama` preferred for hierarchy sections; `fr` for full topology; confirm both render cleanly at fig-width: 10
- [2026-06-01] — Date field in YAML: left as "YYYY-MM-DD" placeholder; author to update on confirmed clean build

---

## 13. Change Log

- [2026-06-01] — Initial project setup; INSTRUCTIONS.md, _brand.yml, _quarto.yml created; data directory populated with five synthetic AD CSVs (175 principals, 32 groups, 261 edges)
