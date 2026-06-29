# Advanced greetings — a lazy-loaded skill reference

This file is a **reference document** linked from `../SKILL.md`. It is *not* read
when the skill loads — the model only opens it when a request actually needs the
extra detail below. Keeping deep material out of `SKILL.md` keeps the skill's
always-loaded instructions short while the detail stays one hop away.

## Greeting styles

| Style | When to use | Example (name = `Felix`) |
|-------|-------------|--------------------------|
| Neutral | default, unknown context | `Hello, Felix.` |
| Warm | a teammate, a friendly ask | `Hey Felix — great to see you!` |
| Formal | first contact, external | `Good day, Felix.` |
| Playful | casual, internal demo | `Ahoy, Felix! 👋` |

Pick the lightest style that fits; when in doubt, stay neutral.

## Localization notes

A greeting is the most language-sensitive line there is. If the user signals a
language, open with the matching word rather than translating mid-sentence:

| Language | Greeting |
|----------|----------|
| English | Hello |
| German | Hallo |
| French | Bonjour |
| Spanish | Hola |
| Japanese | こんにちは |

Default to the language of the user's request. Never guess a name's origin to
pick a language — that is a common and avoidable mistake.

## Edge cases

- **No name given** → greet `world` (the workflow's own default).
- **A team, not a person** → greet the group (`Hello, Performance Dudes!`).
- **Multiple names** → one greeting that lists them, not several lines.
