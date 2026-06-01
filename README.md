# Mapping the Invisible: Active Directory Privilege Escalation Through Graph Analysis

> An identity governance case study demonstrating how graph theory surfaces hidden privilege escalation paths in enterprise Active Directory environments that static access reviews cannot detect.

**Author:** Patrick Lefler
**Published:** [date]
**Rendered:** 

---

## Overview

This project applies graph-theoretic analysis to a synthetic but operationally realistic Active Directory topology — NexaCore Financial Technologies — to identify hidden privilege escalation paths from standard user accounts to Domain Admin. The environment comprises 175 principals (160 human, 15 service accounts), 32 groups organized across four privilege tiers, and 261 directed membership edges. Six deliberate misconfigurations are embedded in the topology, each with a plausible origin story drawn from common enterprise AD anti-patterns.

Using `igraph` and `tidygraph` in R, the analysis constructs the full privilege graph, computes shortest escalation paths, ranks groups by betweenness centrality, and quantifies the blast radius of each misconfiguration edge. The outputs — path traces, centrality rankings, and a remediation backlog — are designed to be both technically precise and communicable to non-technical risk stakeholders.

## Tech Stack

- **Language:** R
- **Framework:** [Quarto](https://quarto.org/)
- **Primary Libraries:** tidyverse, igraph, tidygraph, ggraph, kableExtra, plotly
- **Data Generation:** Python (`generate_ad_data.py`, `random.seed(42)`)
- **Output:** Self-contained HTML (`embed-resources: true`)

## Repository Structure

```
nexacore_ad_project/
├── data/                    # Synthetic AD datasets (CSV)
│   ├── users.csv            # 175 principals with OU, title, type
│   ├── groups.csv           # 32 groups across 4 privilege tiers
│   ├── memberships.csv      # 261 directed membership edges
│   ├── group_nesting.csv    # Group-to-group nesting subset
│   └── ou_structure.csv     # OU hierarchy reference
├── scripts/
│   └── pipeline_diagnostic.R  # Out-of-Quarto pipeline verification
├── output/                  # Rendered HTML output
├── _brand.yml               # Brand configuration (NexaCore)
├── _quarto.yml              # Project-level Quarto configuration
├── INSTRUCTIONS.md          # Project standards and conventions
└── index.qmd                # Main Quarto document
```

## Key Findings

1. **Six misconfigurations create paths to Domain-Admins from ordinary principals.** A Finance Analyst with no suspicious direct group memberships reaches full domain control in four hops, passing through `Finance-Managers`, `Backup-Operators`, and `IT-Admins`. The path was created by a stale project nesting from 2019 that was never cleaned up.

2. **`Backup-Operators` is the critical connector.** Betweenness centrality analysis identifies `Backup-Operators` as the highest-centrality node in the privilege graph — the group through which the greatest number of escalation paths pass. Remediating the `Finance-Managers → Backup-Operators` edge reduces the exposed principal count by 17 in a single change.

3. **Service accounts are the blind spot.** Two of the six misconfigurations involve service accounts (`svc-reporting` in `IT-Admins`, `svc-pentest` in `Network-Admins`). Both are invisible in standard user access reviews because they fall outside the human principal certification process.

## Reproducing the Analysis

```bash
# Generate synthetic AD data
python3 generate_ad_data.py

# Verify pipeline (optional, outside Quarto)
Rscript scripts/pipeline_diagnostic.R

# Render the document
quarto render index.qmd
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

Patrick Lefler | [LinkedIn](https://www.linkedin.com/in/patricklefler/) | [patrick-lefler.github.io](https://patrick-lefler.github.io) | [Substack](https://substack.com/@pflefler)
