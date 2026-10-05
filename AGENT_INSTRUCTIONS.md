# Agent & User Guide: Systematic Slide Maker

This guide provides the complete protocol for an **AI Agent** or **Human** to generate, customize, and maintain presentation decks using `slide-maker`.

---

## 1. Core Operating Principle

> **Rule for AI Agents**: Never modify files in `template/` or any `.typ` source files.
> All content, styling, color palettes, fonts, and layouts are controlled exclusively through `slides.yaml` and assets placed in `assets/`.

---

## 2. Compilation & Verification Commands

```bash
# Compile slides.yaml into slides.pdf (runs in < 1 second)
./slide-maker build

# Watch mode (auto-recompiles on every save to slides.yaml)
./slide-maker watch

# Export each slide as a high-resolution PNG to dist/slides/
./slide-maker export-images
```

---

## 3. Metadata & Theme Configuration (`meta`)

```yaml
meta:
  # 1. Theme Selection
  theme: "academic"          # Options: "academic" (default) | "minimal" | "modern"

  # 2. Named Color Palette (Overrides accent and theme colors)
  palette: "oxford"          # Options: "oxford" | "crimson" | "emerald" | "amber" | "slate" | "indigo"

  # 3. Custom Hex Overrides (Optional - fine-grained control)
  colors:
    accent: "#1e40af"        # Bullets, category rules, stat numbers, borders
    primary: "#0f172a"       # Main headings and primary body text
    muted: "#475569"         # Subtitles, labels, and header/footer metadata
    background: "#ffffff"    # Slide canvas color
    border: "#cbd5e1"        # Divider rules and subtle separators

  # 4. Font Selection (Optional)
  font: "Libertinus Serif"   # Options: "Libertinus Serif" (default) | "New Computer Modern" | "DejaVu Serif"

  # 5. Presentation Info
  title: "CS 739: Distributed Systems Architecture"
  faculty: "Department of Computer Sciences"
  presenter: "Prof. Alan Kay"
  date: "Fall Semester 2026"
```

---

## 4. Slide Layout Reference

Each item under `slides:` must define a `layout` (or `type`):

### A. Title Slide (`layout: "title"`)
Used for the opening hero slide.
```yaml
- layout: "title"
  title: "Consensus Protocols in Distributed Storage"
  subtitle: "Formal Mechanisms of Raft, Multi-Paxos, and Viewstamped Replication"
  faculty: "Department of Computer Sciences • Systems Group" # Optional override
  presenter: "Prof. Alan Kay"                                # Optional override
  date: "Lecture 08 • Fall 2026"                            # Optional override
```

---

### B. Academic Bullets (`layout: "content"`)
High-density content with bold terminology and an optional thesis callout.
```yaml
- layout: "content"
  category: "FOUNDATIONS"        # Uppercase category tag shown above title
  title: "The Consensus Problem: Formal Bounds"
  subtitle: "State Machine Replication under Asynchronous Network Assumptions"
  bullets:
    - "**FLP Impossibility Result**: Deterministic asynchronous consensus is impossible in the presence of crash failures."
    - "**Partially Synchronous Models**: Practical systems circumvent FLP by introducing randomized timers $\Delta$."
    - "**State Machine Replication**: Replicas execute identical sequences of deterministic transitions from $S_0$."
  callout: "Consensus guarantees strict non-divergence of committed logs across partitions."
```

---

### C. Split Slide with Diagram / Image (`layout: "split-diagram"` or `"split-image"`)
2-column layout pairing analytical bullets with a vector SVG or image.
```yaml
- layout: "split-diagram"
  category: "PROTOCOL MECHANICS"
  title: "Raft: Quorum-Based Log Replication"
  subtitle: "Normal operation flow and write replication under leader authority"
  image: "assets/consensus-diagram.svg"   # Path relative to project root
  caption: "Figure 1: Leader appends entries to local log before dispatching RPCs."
  image_position: "right"                # "right" (default) or "left"
  bullets:
    - "**Client Proposal**: Client issues mutation $v=42$ exclusively to the established leader."
    - "**AppendEntries RPC**: Leader broadcasts parallel RPCs to all registered peers."
    - "**Commit Threshold**: Once replicated across quorum $\\lfloor N/2 \\rfloor + 1$, entry commits."
```

---

### D. Comparative Analysis (`layout: "comparison"`)
Clean side-by-side trade-off matrix without card-clutter.
```yaml
- layout: "comparison"
  category: "ARCHITECTURAL TRADE-OFFS"
  title: "Comparative Analysis: Raft vs Multi-Paxos"
  subtitle: "Deconstructing architectural simplicity versus operational throughput"
  left_title: "Raft (Strong Leader)"
  left_bullets:
    - "**Log Discrepancy Prevention**: Entries flow unidirectionally from Leader to Followers."
    - "**Understandability Metric**: Formally designed to eliminate overlapping leader states."
  right_title: "Multi-Paxos (Decentralized)"
  right_bullets:
    - "**Flexible Roles**: Any replica can propose; phase-1 can be amortized across instances."
    - "**Complex Invariants**: Log hole resolution introduces subtle edge cases."
  conclusion: "Raft reduces operational bugs in control planes; Multi-Paxos excels in geo-replicated DBs."
```

---

### E. Quantitative Metrics Grid (`layout: "stat-grid"`)
Display 2 to 4 prominent empirical metrics or benchmark results.
```yaml
- layout: "stat-grid"
  category: "EMPIRICAL BENCHMARKS"
  title: "Empirical Performance Under Cluster Degradation"
  stats:
    - value: "14.2k"
      unit: "ops/sec"
      label: "Peak Write Throughput"
      description: "3-node NVMe Raft cluster with fsync batching"
    - value: "3.1"
      unit: "ms"
      label: "P99 Commit Latency"
      description: "Local area gigabit network interconnect"
    - value: "180"
      unit: "ms"
      label: "Leader Failover Time"
      description: "Heartbeat interval 50ms, timeout 150-300ms"
    - value: "0"
      unit: "anomalies"
      label: "Linearizability Violations"
      description: "Jepsen partition injection suite verification"
  summary: "**Empirical Finding**: Randomized follower timeouts prevent split-vote livelocks with >99.7% probability."
```

---

### F. Code Walkthrough (`layout: "code"`)
Syntax-highlighted code block paired with explanatory bullets.
```yaml
- layout: "code"
  category: "IMPLEMENTATION"
  title: "Leader Election Timeout State Transition"
  language: "python"
  code: |
    def handle_election_timeout(self):
        self.current_term += 1
        self.state = NodeState.CANDIDATE
        self.voted_for = self.node_id
        for peer in self.peers:
            self.send_request_vote(peer_id=peer, term=self.current_term)
  bullets:
    - "**Term Advance**: Monotonic clock increments immediately upon transition."
    - "**Self-Voting**: Candidate casts vote for itself prior to dispatching network RPCs."
```

---

## 5. Text & Math Formatting Rules

* **Bold**: Use standard markdown asterisks (`**key term**`) to highlight technical concepts.
* **Math Formulas**: Use Typst native math syntax (`$E = m c^2$`, `$floor(N/2) + 1$`, `$Delta$`, `$alpha$`).
  * Common LaTeX macros (`\Delta`, `\lfloor`, `\rfloor`, `\leq`, `\geq`, `\times`) are automatically sanitized into Typst equivalents.
* **Inline Code**: Use single backticks (`` `variable_name` ``).

---

## 6. Slide Density Rules

* **Max Bullets Per Slide**: Keep content slides to 3–5 bullets.
* **Punchy Statements**: Avoid multi-sentence essay paragraphs within bullets.
* **Visual Diversity**: Avoid having 3 identical bullet slides in a row. Alternate with `split-diagram`, `comparison`, or `stat-grid`.
