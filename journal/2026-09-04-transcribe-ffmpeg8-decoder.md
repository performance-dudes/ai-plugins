# 2026-09-04 — transcribe: der Decoder, der an FFmpeg 8 zerbrach

## Was

`transcribe` 0.1.2 → **0.1.3**. `scripts/diarize_pyannote.py` lädt das Waveform
nicht mehr über `torchaudio.load`, sondern über `soundfile` und reicht es als
Tensor an pyannote weiter. Dazu ein Regressionstest (`validate.sh` §8), der den
Decoder-Pfad festnagelt, und der bis dahin fehlende Bump in
`.claude-plugin/marketplace.json`.

## Warum

Auf einem Mac mit Homebrew-FFmpeg 8 brach die Diarisierung ab, bevor sie begann.
Die Ursache liegt nicht in pyannote, sondern eine Schicht tiefer: `torchaudio.load`
delegiert seit torchaudio 2.9 an **torchcodec**, und torchcodec bindet gegen die
FFmpeg-Major-Versionen 4 bis 7. Unter FFmpeg 8 findet es keine passende
Bibliothek und scheitert beim Laden — nicht beim Dekodieren. Der Fehler sieht
deshalb nach einem Modell- oder Torch-Problem aus und führt in die falsche
Richtung.

Der Decoder-Umweg war ohnehin entbehrlich: pyannote nimmt das Waveform als
Tensor-Dict entgegen, die Datei muss also nur irgendwie in einen Tensor kommen.
`soundfile` (libsndfile) macht das ohne FFmpeg-Bindung.

## Zwei Dinge, die beim Nachbauen stolpern lassen

- **`sf.read` liefert `(frames, channels)`, pyannote will `(channels, frames)`.**
  Also transponieren — und danach `np.ascontiguousarray`, sonst trägt der Tensor
  ein negatives Stride durch die Pipeline. `always_2d=True` hält den Mono-Fall
  formgleich mit Stereo, sonst fehlt die Kanal-Achse genau dann, wenn man sie
  am wenigsten erwartet.
- **Der erste Regressionstest war grün auf dem Bug und rot auf dem Fix — wegen
  des eigenen Kommentars.** Ein `grep -q 'torchaudio\.load'` trifft die Zeile,
  die erklärt, warum `torchaudio.load` ersetzt wurde. Prosa im Code ist für
  einen Textmatcher nicht von Code zu unterscheiden: der Test muss auf
  `^[^#]*torchaudio\.load` prüfen. Gleiche Falle in jedem Ban-Wort-Test.

## Learnings

**Ein halber Version-Bump ist ein stiller Nicht-Release.** Der Branch bumpte
`plugins/transcribe/.claude-plugin/plugin.json`, nicht aber
`.claude-plugin/marketplace.json`. Wäre er so gemergt worden, hätte
`claude plugin update` weiter „already at latest version" gemeldet und den
kaputten Stand ausgeliefert — der Fix läge auf `main` und erreichte niemanden.
Genau dafür steht die Bump-Prüfung im Merge-Gate **vor** der Marker-Prüfung.
