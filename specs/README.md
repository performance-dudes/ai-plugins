# specs/

Produkt-/Tech-Specs des Repos. **Intent: was & warum.** Regeln (voll:
[`specs/repo-conventions/0001_product_repo-conventions.md`](repo-conventions/0001_product_repo-conventions.md)):

- **Nie unter `docs/`.** Spec = Intent, Docs = Erklärung der Komponenten.
- **Benennung** `<NNNN>_<type>_<plugin>[_<topic>].md` — `<type>` ∈ {`product`,`tech`}
  macht die Spec am Namen erkennbar (Pflicht). Beispiel:
  `0001_product_ocr.md`. Je Plugin ein Unterordner `specs/<plugin>/`
  (oder flach — fast egal, solange der Name klar ist); repo-weite Specs in eigenem
  Unterordner (z. B. `repo-conventions/`).
- Spec **zuerst**, PR **früh** öffnen (Spec-Driven TDD, `craft/spec-driven-tdd`).
