# mechanic — cost-tier routing (active)

Route before spawning:

```
needs a DECISION (design·debug unknown·review·prose·relevance) -> general-purpose
needs CODE/CONTEXT understanding to apply a decided change     -> "mechanic"
trivial + VOLUME (batch/whole file/long scan)                  -> "mechanic:errand"
trivial + SINGLE item                                          -> INLINE, do not spawn
```

- An agent run costs ~4x a plain turn: one lone trivial item is cheaper inline.
- Unsure between two tiers -> take the higher one. Under-routing pays cheap attempt
  + premium retry; over-routing just overpays.

Parallelism:

- Fan out N agents in ONE message block; sequential spawns pay overhead, gain nothing.
- One agent per independent chunk; never more agents than chunks.
- Read-only fan-out: always safe, go wide.
- Writing fan-out: file sets MUST be disjoint — name each agent's paths. Not
  partitionable -> run sequentially.
- Parallelise within a stage; a stage consuming another's output waits.
