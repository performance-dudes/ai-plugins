#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Build a blind routing prompt by INJECTING the real object under test.

The golden rule (see ../README.md and the repo CLAUDE.md): an eval tests the
REAL object — the actual agent descriptions and task prompts — never a paraphrase
copied into the harness. A copy drifts from the plugin and then measures itself.

So this builder READS, at runtime:
  • the verbatim frontmatter `description:` of the real agents/*.md (that string IS
    what a live orchestrator sees in its registry), and
  • the task prompts straight from routing/ground_truth.yaml,
and assembles the router prompt from those. Change a description in the plugin and
the next build tests the changed plugin — zero duplication, zero drift.

To keep the run BLIND and leak-free it: strips every answer field (route/trap/
capability/note) from the cases, replaces the telling case ids (i01…/g04… leak the
route via their prefix) with neutral t01… ids in a DETERMINISTIC shuffle (stable
across runs, no RNG), and writes an idmap so a captured run can be translated back
to case ids for scoring.

Usage:
    # 1. build the blind prompt + idmap from the REAL plugin
    uv run evals/routing/build_router_prompt.py \
        > /tmp/router_prompt.md            # idmap → routing/.idmap.json

    # 2. feed /tmp/router_prompt.md to N fresh agents (blind); collect each JSON

    # 3. translate a captured agent JSON back to case-keyed predictions
    uv run evals/routing/build_router_prompt.py --translate run1.json \
        > /tmp/predictions.yaml
    uv run evals/scripts/score_routing.py --pred /tmp/predictions.yaml
"""

import argparse
import hashlib
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
EVALS = os.path.dirname(HERE)
PLUGIN = os.path.dirname(EVALS)
GROUND_TRUTH = os.path.join(HERE, "ground_truth.yaml")
IDMAP = os.path.join(HERE, ".idmap.json")
AGENTS = {  # route label -> the REAL file whose description is injected verbatim
    "errand": os.path.join(PLUGIN, "agents", "errand.md"),
    "mechanic": os.path.join(PLUGIN, "agents", "mechanic.md"),
}
# general-purpose is a Claude Code built-in; its registry description, verbatim.
GENERAL_PURPOSE_DESC = (
    "General-purpose agent for researching complex questions, searching for code, "
    "and executing multi-step tasks. When you are searching for a keyword or file "
    "and are not confident that you will find the right match in the first few tries "
    "use this agent to perform the search for you."
)


def _frontmatter_description(md_path):
    """Return the verbatim `description:` value from a .md's YAML frontmatter —
    the real string, read from the real file, never a hand-kept copy."""
    with open(md_path, "r", encoding="utf-8") as fh:
        text = fh.read()
    _, fm, _ = text.split("---", 2)
    data = yaml.safe_load(fm)
    return " ".join(data["description"].split())  # normalise folded whitespace


def _neutral_order(cases):
    """Deterministic, RNG-free shuffle: order by a hash of the case id, so the
    balanced 4×5 structure and the route-hinting prefixes are hidden, yet the
    mapping is stable across runs (reproducible eval)."""
    return sorted(cases, key=lambda c: hashlib.sha1(c["case"].encode()).hexdigest())


def build():
    gt = yaml.safe_load(open(GROUND_TRUTH, encoding="utf-8"))
    ordered = _neutral_order(gt["cases"])
    idmap = {}
    task_lines = []
    for i, c in enumerate(ordered, 1):
        tid = f"t{i:02d}"
        idmap[tid] = c["case"]
        task_lines.append(f"{tid}: {c['prompt']}")   # PROMPT ONLY — no answer fields

    errand = _frontmatter_description(AGENTS["errand"])
    mechanic = _frontmatter_description(AGENTS["mechanic"])

    prompt = f"""You are the ORCHESTRATOR of a Claude Code session. The `mechanic` plugin is
installed, exposing two subagent types. For each task choose ONE route. You are
ONLY classifying the route — do NOT perform any task.

Options:

1. route = "inline"
   Handle it yourself in the main loop, WITHOUT spawning any subagent.

2. route = "errand"   (subagent_type "mechanic:errand")
   Registry description, verbatim:
   \"\"\"{errand}\"\"\"

3. route = "mechanic"   (subagent_type "mechanic")
   Registry description, verbatim:
   \"\"\"{mechanic}\"\"\"

4. route = "general-purpose"   (premium built-in)
   Registry description, verbatim:
   \"\"\"{GENERAL_PURPOSE_DESC}\"\"\"

Decide each task on its merits from these descriptions. Return ONLY a JSON array,
one object per task, no prose:
[{{"id":"<id>","route":"<inline|errand|mechanic|general-purpose>","reason":"<=10 words>"}}]

TASKS:
""" + "\n".join(task_lines) + "\n"

    with open(IDMAP, "w", encoding="utf-8") as fh:
        json.dump(idmap, fh, ensure_ascii=False, indent=2)
    return prompt


def translate(agent_json_path):
    idmap = json.load(open(IDMAP, encoding="utf-8"))
    raw = json.load(open(agent_json_path, encoding="utf-8"))
    preds = []
    for row in raw:
        case = idmap.get(row["id"])
        if case:
            preds.append({"case": case, "route": row["route"]})
    return {"model": f"router-from-real-object:{os.path.basename(agent_json_path)}",
            "predictions": preds}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Inject the real object into a blind routing prompt.")
    ap.add_argument("--translate", metavar="AGENT_JSON",
                    help="translate a captured agent-output JSON back to case-keyed predictions YAML")
    args = ap.parse_args(argv)
    if args.translate:
        sys.stdout.write(yaml.safe_dump(translate(args.translate), sort_keys=False, allow_unicode=True))
    else:
        sys.stdout.write(build())
    return 0


if __name__ == "__main__":
    sys.exit(main())
