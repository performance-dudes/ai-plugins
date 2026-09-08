#!/usr/bin/env bash
# anti-slop — Plugin-Suite (SPEC-anti-slop §5, „einteilig": alles unter tests/<plugin>/).
# Offline, zero-dep (bash + python3). Deckt config-valid und script-run ab;
# die Trennschärfe (US-slop-3) misst die Eval, nicht dieser Test.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
PLUGIN="$ROOT/plugins/anti-slop"
SKILL="$PLUGIN/skills/anti-slop"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

rc=0
ok()   { printf '  ok   %s\n' "$1"; }
fail() { printf '  FAIL %s\n' "$1"; rc=1; }
check() { if [ "$1" = "0" ]; then ok "$2"; else fail "$2"; fi; }

printf '\n-- config-valid --\n'

# AC-4-1 .. AC-4-5: Datenintegrität aller Listen in einem Durchgang.
python3 - "$SKILL" <<'PYEOF'
import json, pathlib, sys
skill = pathlib.Path(sys.argv[1])
data = skill / "data"
fail = []

CURATED = ["slop-list-en-extra.json", "slop-list-de.json", "slop-list-universal.json"]
for f in sorted(data.glob("slop-list*.json")):
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:
        fail.append(f"AC-4-1 {f.name}: kein valides JSON ({e})"); continue
    if not isinstance(d, list) or not d:
        fail.append(f"AC-4-1 {f.name}: keine nicht-leere Liste"); continue
    for e in d:
        if not isinstance(e, list) or not e or not isinstance(e[0], str) or not e[0].strip():
            fail.append(f"AC-4-1 {f.name}: defekter Eintrag {e!r}"); break

    terme = [e[0] for e in d]
    dupes = {t for t in terme if terme.count(t) > 1}
    if dupes:
        fail.append(f"AC-4-4 {f.name}: Duplikate {sorted(dupes)[:5]}")

    if f.name in CURATED:
        for e in d:
            if len(e) < 3 or e[2] not in ("hard", "soft"):
                fail.append(f"AC-4-2 {f.name}: {e[0]!r} ohne gültige severity"); break
        # AC-4-3: Einträge, die als Literal nie matchen können
        for e in d:
            t, cat = e[0], e[1]
            if cat == "placeholder":
                continue
            if ("/" in t and "utm_" not in t) or "..." in t or "…" in t or "[" in t:
                fail.append(f"AC-4-3 {f.name}: toter Eintrag {t!r}"); break
        # AC-4-5: Stock-Namen sind reale Personennamen -> nie hart
        for e in d:
            if e[1] == "stock-name" and e[2] != "soft":
                fail.append(f"AC-4-5 {f.name}: {e[0]!r} ist stock-name, aber hard"); break
        # Gegenstueck: erfundene Orte gehoeren niemandem und bleiben hart.
        # Ohne diesen Check koennte man sie still nach stock-name schieben und
        # damit die schaerfsten Fiktions-Signale verlieren.
        for e in d:
            if e[1] == "stock-place" and e[2] != "hard":
                fail.append(f"AC-4-5 {f.name}: {e[0]!r} ist stock-place, aber soft"); break

orte = [e for e in json.loads((data/"slop-list-universal.json").read_text(encoding="utf-8"))
        if e[1] == "stock-place"]
if not orte:
    fail.append("AC-4-5 keine stock-place-Einträge — erfundene Orte müssen hart bleiben")

ov = data / "severity-overrides.json"
if not ov.exists():
    fail.append("AC-4-1 severity-overrides.json fehlt")
else:
    o = json.loads(ov.read_text(encoding="utf-8"))
    if not isinstance(o.get("soft"), list) or not o["soft"]:
        fail.append("AC-4-1 severity-overrides.json: 'soft' fehlt oder leer")

# AC-5-1: NOTICE nennt jede Fremdquelle
notice = (skill.parents[3] / "NOTICE")
if not notice.exists():
    fail.append("AC-5-1 NOTICE fehlt im Repo-Root")
else:
    n = notice.read_text(encoding="utf-8")
    for q in ["antislop-sampler", "SLOP_Detector", "Cliche_Corpus", "document-lens", "CC BY-SA"]:
        if q not in n:
            fail.append(f"AC-5-1 NOTICE nennt {q} nicht")

# SKILL.md-Frontmatter wohlgeformt
sm = (skill / "SKILL.md").read_text(encoding="utf-8")
if not sm.startswith("---\n") or "\nname: anti-slop\n" not in sm[:2000] or "description:" not in sm[:4000]:
    fail.append("config-valid SKILL.md: Frontmatter unvollständig")

# Referenzen aus der SKILL.md müssen existieren
import re
for rel in re.findall(r"\]\((references/[a-z0-9-]+\.md)\)", sm):
    if not (skill / rel).exists():
        fail.append(f"config-valid SKILL.md verweist auf fehlende Datei {rel}")

for f in fail:
    print("  FAIL " + f)
print("  ok   Listen, severity-overrides, NOTICE, SKILL.md" if not fail else "")
sys.exit(1 if fail else 0)
PYEOF
check $? "Datenintegrität + Herkunft (AC-4-1..4-5, AC-5-1)"

python3 -c "import ast,sys; ast.parse(open('$SKILL/scripts/check-slop.py').read())" 2>/dev/null
check $? "check-slop.py ist syntaktisch gültig"

printf '\n-- script-run --\n'
CHECK="$SKILL/scripts/check-slop.py"

# AC-1-1: Stamm-Eintrag findet die flektierten Formen
cat > "$TMP/flex.md" <<'EOF'
Die entscheidende Rolle, der entscheidender Faktor, das entscheidendes Merkmal.
EOF
n=$(python3 "$CHECK" --lang de "$TMP/flex.md" | grep -c 'entscheidend' || true)
[ "$n" -ge 1 ]
check $? "AC-1-1 Flexion: entscheidend* findet entscheidende/-er/-es"

python3 "$CHECK" --lang de "$TMP/flex.md" | grep -q 'entscheidende' 
check $? "AC-1-1 gemeldete Form ist die flektierte, nicht der Stamm"

# AC-1-2: Ein Eintrag OHNE * darf die flektierte Form NICHT fangen.
# 'murmelte' steht ohne Stern auf der Liste; 'murmelten' muss durchgehen.
# Gegenprobe im zweiten Fall, damit der Test nicht durch einen kaputten
# Prüfer grün wird, der generell nichts findet.
printf 'Sie murmelten leise vor sich hin und gingen dann weiter die Strasse entlang.\n' > "$TMP/flex-neg.md"
[ -z "$(python3 "$CHECK" --lang de "$TMP/flex-neg.md" | grep -i 'murmelte' || true)" ]
check $? "AC-1-2 Eintrag ohne * fängt die flektierte Form nicht (murmelten)"

printf 'Sie murmelte leise vor sich hin und ging dann weiter die Strasse entlang.\n' > "$TMP/flex-pos.md"
python3 "$CHECK" --lang de "$TMP/flex-pos.md" | grep -qi 'murmelte'
check $? "AC-1-2 Gegenprobe: die Literalform wird sehr wohl gefunden"

# AC-1-3: Term mit Satzzeichen am Rand
printf 'Selbstverst\303\244ndlich! Das erledige ich sofort und ohne Umschweife hier.\n' > "$TMP/ausruf.md"
python3 "$CHECK" --lang de "$TMP/ausruf.md" | grep -qi 'selbstverständlich!'
check $? "AC-1-3 Term mit Satzzeichen (Selbstverständlich!) wird gefunden"

# AC-2-1: Spracherkennung
cat > "$TMP/de.md" <<'EOF'
Wir haben die Datei geprüft und drei Fehler gefunden, die wir behoben haben.
Der Import läuft seit Dienstag wieder, die Zeitzone steht jetzt auf Berlin.
EOF
python3 "$CHECK" "$TMP/de.md" | head -1 | grep -q '+ de$'
check $? "AC-2-1 Spracherkennung: deutscher Text -> de"

cat > "$TMP/en.md" <<'EOF'
We checked the file and found three defects, all of which we have fixed since.
The import has been running again since Tuesday and the timezone is set now.
EOF
python3 "$CHECK" "$TMP/en.md" | head -1 | grep -q '+ en$'
check $? "AC-2-1 Spracherkennung: englischer Text -> en"

# AC-2-2: Universal-Liste greift in beiden Sprachen
printf 'Ein Absatz mit einem Rest aus dem Werkzeug: oaicite steht mitten im Text.\n' > "$TMP/uni-de.md"
python3 "$CHECK" --lang de "$TMP/uni-de.md" | grep -q 'oaicite'
check $? "AC-2-2 Universal-Liste greift bei --lang de"

printf 'A paragraph that still carries a leftover tool artifact: oaicite sits here.\n' > "$TMP/uni-en.md"
python3 "$CHECK" --lang en "$TMP/uni-en.md" | grep -q 'oaicite'
check $? "AC-2-2 Universal-Liste greift bei --lang en"

# AC-2-3: Universal zuerst -> Stock-Name bleibt weich, auch wenn die
# Upstream-Liste ihn pauschal als hart führt.
printf 'Aria opened the door and walked into the room without saying anything.\n' > "$TMP/name.md"
[ -z "$(python3 "$CHECK" --lang en --hard-only "$TMP/name.md" | grep -i '^ *aria' || true)" ]
check $? "AC-2-3 Stock-Name (aria) erscheint nicht unter --hard-only"

# Gegenprobe: derselbe Name MUSS als weicher Treffer erscheinen — sonst wäre
# der Check darüber auch bei einem Prüfer grün, der generell nichts findet.
python3 "$CHECK" --lang en "$TMP/name.md" | grep -qi 'aria'
check $? "AC-2-3 derselbe Name erscheint sehr wohl als weicher Treffer"

printf '\n=== anti-slop: %s ===\n' "$([ $rc -eq 0 ] && echo PASS || echo FAIL)"
exit "$rc"
