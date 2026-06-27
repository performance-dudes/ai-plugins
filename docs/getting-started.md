# Schnellstart: das `example`-Plugin benutzen

Der kürzeste Weg von „installieren" bis „es funktioniert".

## 1. Das Plugin installieren

Das Plugin kommt aus dem Marketplace `ai-plugins` (der „App-Store" dieses Repos).

```bash
claude plugin marketplace add performance-dudes/ai-plugins
claude plugin install example@ai-plugins
```

## 2. Ausprobieren

Tippe in einer Claude-Code-Sitzung:

```
/greet Felix
```

Du bekommst **eine** kurze Begrüßungszeile zurück.

Oder schreib einfach normal: *"begrüße die Performance Dudes"* — dann springt die
Skill `run-greet` von allein an und macht dasselbe.

## 3. Prüfen, ob alles heil ist

```bash
bash example/tests/validate.sh
```

Steht am Ende `ALL CHECKS PASSED`, ist alles in Ordnung.
