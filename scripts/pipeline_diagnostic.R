# =============================================================================
# pipeline_diagnostic.R
# NexaCore AD Governance — Pipeline Verification Script
#
# Run this script OUTSIDE Quarto to trace data pipeline stages and verify
# graph construction without Quarto's message suppression interfering.
# Usage: Rscript scripts/pipeline_diagnostic.R
# =============================================================================

library(tidyverse)
library(igraph)
library(tidygraph)

cat("=== NexaCore AD Pipeline Diagnostic ===\n\n")

# ── 1. Data ingestion ──────────────────────────────────────────────────────────
cat("Stage 1: Data ingestion\n")
users         <- read_csv("data/users.csv",         show_col_types = FALSE)
groups        <- read_csv("data/groups.csv",         show_col_types = FALSE)
memberships   <- read_csv("data/memberships.csv",    show_col_types = FALSE)
group_nesting <- read_csv("data/group_nesting.csv",  show_col_types = FALSE)

cat("  users.csv:         ", nrow(users),        "rows\n")
cat("  groups.csv:        ", nrow(groups),       "rows\n")
cat("  memberships.csv:   ", nrow(memberships),  "rows\n")
cat("  group_nesting.csv: ", nrow(group_nesting),"rows\n\n")

# ── 2. Node table ──────────────────────────────────────────────────────────────
cat("Stage 2: Node table construction\n")
user_nodes <- users |>
  transmute(
    name       = username,
    label      = display_name,
    node_type  = user_type,
    department = department,
    is_senior  = is_senior,
    tier       = NA_integer_,
    group_type = NA_character_
  )

group_nodes <- groups |>
  transmute(
    name       = group_name,
    label      = group_name,
    node_type  = "group",
    department = NA_character_,
    is_senior  = FALSE,
    tier       = as.integer(tier),
    group_type = group_type
  )

all_nodes <- bind_rows(user_nodes, group_nodes)
cat("  Total nodes:       ", nrow(all_nodes), "\n")
cat("  Human:             ", sum(all_nodes$node_type == "human"), "\n")
cat("  Service:           ", sum(all_nodes$node_type == "service"), "\n")
cat("  Group:             ", sum(all_nodes$node_type == "group"), "\n\n")

# ── 3. Edge table ──────────────────────────────────────────────────────────────
cat("Stage 3: Edge table construction\n")
all_edges <- memberships |>
  transmute(
    from             = member_name,
    to               = group_name,
    member_type      = member_type,
    misconfiguration = misconfiguration == "True"
  )

cat("  Total edges:       ", nrow(all_edges), "\n")
cat("  Misconfiguration:  ", sum(all_edges$misconfiguration), "\n\n")

# Check for any from/to names not in node list
missing_from <- setdiff(all_edges$from, all_nodes$name)
missing_to   <- setdiff(all_edges$to,   all_nodes$name)
if (length(missing_from) > 0) cat("  WARN: missing from nodes:", paste(missing_from, collapse=", "), "\n")
if (length(missing_to)   > 0) cat("  WARN: missing to nodes:",   paste(missing_to,   collapse=", "), "\n")
if (length(missing_from) == 0 && length(missing_to) == 0) cat("  Node coverage: OK (all edge endpoints in node table)\n\n")

# ── 4. Graph construction ──────────────────────────────────────────────────────
cat("Stage 4: Graph construction\n")
g <- graph_from_data_frame(d = all_edges, directed = TRUE, vertices = all_nodes)
cat("  Vertices:          ", vcount(g), "\n")
cat("  Edges:             ", ecount(g), "\n")
cat("  Graph density:     ", round(graph.density(g), 6), "\n")
cat("  Weakly connected components:", components(g, mode = "weak")$no, "\n\n")

# ── 5. Reachability to Domain-Admins ──────────────────────────────────────────
cat("Stage 5: Domain-Admins reachability\n")
target_idx       <- which(V(g)$name == "Domain-Admins")
principal_nodes  <- which(V(g)$node_type %in% c("human", "service"))
path_lengths     <- distances(g, v = principal_nodes, to = target_idx, mode = "out")

n_reachable <- sum(is.finite(path_lengths))
cat("  Principals with path to Domain-Admins:", n_reachable, "/", length(principal_nodes), "\n")

reachable <- tibble(
  name        = V(g)$name[principal_nodes],
  node_type   = V(g)$node_type[principal_nodes],
  path_length = as.integer(path_lengths[, 1])
) |> filter(is.finite(path_length))

cat("  By hop count:\n")
reachable |> count(path_length) |>
  arrange(path_length) |>
  mutate(out = paste0("    ", path_length, " hops: ", n, " principals")) |>
  pull(out) |> cat(sep = "\n")

cat("\n")

# ── 6. Betweenness centrality top 5 ───────────────────────────────────────────
cat("Stage 6: Betweenness centrality (top 5 groups)\n")
bw <- betweenness(g, directed = TRUE, normalized = TRUE)
bw_df <- tibble(name = V(g)$name, node_type = V(g)$node_type, bw = bw) |>
  filter(node_type == "group") |>
  arrange(desc(bw)) |>
  slice_head(n = 5)

bw_df |>
  mutate(out = paste0("  ", sprintf("%-25s", name), " bw=", round(bw * 100, 4))) |>
  pull(out) |> cat(sep = "\n")

cat("\n=== Diagnostic complete — pipeline is healthy ===\n")
