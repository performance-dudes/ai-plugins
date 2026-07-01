# Onboarding UI Patterns

UI-side implementation of patterns that drive activation and conversion in onboarding flows.
These are the components, animations, and microcopy that *deliver* the strategy.

> **Strategy layer (separate skill):** This reference is the UI **execution** only —
> components, layout, motion, microcopy. The conversion-/PLG-psychology behind *whether* to
> use a pattern (aha-moment framework, paywall placement, decision matrices) lives in the
> **conversion skill (sales plugin)**, not here. Read both together when designing or
> auditing a flow — strategy without UI fails to ship; UI without strategy ships the wrong thing.

## Table of Contents

1. [Tooltips & Microcopy as Teaching Devices](#1-tooltips--microcopy-as-teaching-devices)
2. [Live Form Validation](#2-live-form-validation)
3. [Multi-Step Form Layout](#3-multi-step-form-layout)
4. [Empty-State Nudges](#4-empty-state-nudges)
5. [Persistent Onboarding Checklist](#5-persistent-onboarding-checklist)
6. [Permission-Prime Screen](#6-permission-prime-screen)
7. [Loader-as-Delight](#7-loader-as-delight)
8. [Mascots & Micro-Celebrations](#8-mascots--micro-celebrations)
9. [Onboarding-UI Anti-Patterns](#9-onboarding-ui-anti-patterns)

---

## Why a Separate Reference

The main SKILL.md covers the visual primitives — colors, typography, buttons, layouts,
generic motion. Those primitives are necessary but not sufficient for onboarding flows.
Onboarding has its own UI vocabulary because it does a different job: not "show information"
but "carry a brand-new user through their first 60 seconds without losing them."

That job has consistently-evidenced patterns (Mural's checklist drove **+10% week-1 retention**;
House's split form drove **+15% conversion**). This file collects them as ready-to-paste
components with the *why* attached.

---

## 1. Tooltips & Microcopy as Teaching Devices

**Use when:** the flow exposes a concept the user may not understand (financial terms, technical
configs, domain-specific jargon). Cake Equity uses this to demystify equity vesting schedules
without front-loading a tour.

**Principle:** Teach in context, not in advance. A tooltip on the *exact* field that needs
explanation is read 3-5x more often than a dedicated tutorial step.

```html
<label for="vesting-cliff">
  Vesting cliff
  <button
    type="button"
    class="info-trigger"
    aria-label="What is a vesting cliff?"
    aria-describedby="vesting-cliff-tooltip"
    data-tooltip-target="vesting-cliff-tooltip"
  >ⓘ</button>
</label>
<input id="vesting-cliff" type="number" min="0" max="48" />

<div id="vesting-cliff-tooltip" role="tooltip" hidden>
  The minimum time before any equity vests. Most companies use 12 months —
  if you leave before that, you keep nothing.
</div>
```

```css
.info-trigger {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--neutral-500);
  cursor: help;
  border-radius: 50%;
}

.info-trigger:hover,
.info-trigger:focus-visible {
  color: var(--primary);
  background: var(--primary-tint);
}

[role="tooltip"] {
  position: absolute;
  max-width: 28ch;
  padding: 8px 12px;
  background: var(--neutral-900);
  color: white;
  font-size: 0.8125rem;
  line-height: 1.4;
  border-radius: 6px;
  z-index: 10;
}
```

**Microcopy checklist:**
- One concept per tooltip — don't stack ideas
- Use the user's language, not domain jargon (Voice-of-Customer principle)
- End with a *concrete example* if possible ("Most companies use 12 months — …")
- Reassure when the field has irreversible consequences ("You can change this later")

---

## 2. Live Form Validation

**Use when:** the field has discoverable rules (password strength, username availability,
email format, phone format). Replaces "Submit → server error → fix → retry" with
"keep typing → green checks appear."

**Principle:** Real-time feedback removes a reason to drop off. The user sees the rules
*as they type*, so they never reach a frustrating "rejected" state.

```html
<label for="password">Create a password</label>
<input
  id="password"
  type="password"
  required
  minlength="12"
  aria-describedby="password-rules"
/>

<ul id="password-rules" class="password-rules">
  <li data-rule="length">At least 12 characters</li>
  <li data-rule="uppercase">One uppercase letter</li>
  <li data-rule="number">One number</li>
  <li data-rule="symbol">One symbol</li>
</ul>
```

```javascript
const rules = {
  length: (v) => v.length >= 12,
  uppercase: (v) => /[A-Z]/.test(v),
  number: (v) => /\d/.test(v),
  symbol: (v) => /[^A-Za-z0-9]/.test(v),
};

const input = document.getElementById('password');
const items = document.querySelectorAll('.password-rules li');

input.addEventListener('input', (e) => {
  const value = e.target.value;
  items.forEach((li) => {
    const rule = li.dataset.rule;
    li.classList.toggle('met', rules[rule](value));
  });
});
```

```css
.password-rules {
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
  font-size: 0.8125rem;
}

.password-rules li {
  position: relative;
  padding-left: 24px;
  color: var(--neutral-500);
  transition: color 200ms ease;
}

.password-rules li::before {
  content: "○";
  position: absolute;
  left: 0;
  color: currentColor;
}

.password-rules li.met {
  color: var(--success);
}

.password-rules li.met::before {
  content: "✓";
}
```

**Anti-pattern:** Validating *only on blur*. Users mash Submit, see an error, blur, see another
error. Validate on `input`. Submit-time validation is the *backstop*, not the primary signal.

**Accessibility:** The `<ul>` referenced via `aria-describedby` ensures screen readers announce
the rules together with the field. Animate state changes with class transitions, not removed/added
DOM nodes — screen readers re-announce removed nodes confusingly.

---

## 3. Multi-Step Form Layout

**Use when:** a single form has more than 5–7 fields *or* it covers visibly different concerns
(account info + preferences + payment). House saw **+15% conversion** by splitting one signup
form into multiple screens.

**Principle:** A long single form telegraphs effort upfront. Splitting fields into screens with
a progress bar transforms "fill in everything" into "answer one question, tap, repeat" — each
tap feels like progress instead of remaining work.

```html
<div class="multi-step-form" aria-labelledby="step-title">
  <header class="step-header">
    <p class="step-counter" aria-live="polite">Step 2 of 4</p>
    <progress max="4" value="2" aria-label="Onboarding progress">50%</progress>
    <h1 id="step-title">What are your goals?</h1>
  </header>

  <fieldset>
    <!-- 1-3 fields per step max -->
  </fieldset>

  <footer class="step-footer">
    <button type="button" class="btn-secondary">Back</button>
    <button type="submit" class="btn-primary">Continue</button>
  </footer>
</div>
```

```css
.multi-step-form {
  max-width: 480px;
  margin: 0 auto;
  padding: 24px;
}

.step-header {
  margin-bottom: 32px;
}

.step-counter {
  font-size: 0.8125rem;
  color: var(--neutral-500);
  margin: 0 0 8px;
}

progress {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  margin-bottom: 16px;
}

progress::-webkit-progress-bar { background: var(--neutral-200); border-radius: 2px; }
progress::-webkit-progress-value { background: var(--primary); border-radius: 2px; transition: all 300ms ease; }

.step-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 32px;
}

@media (max-width: 480px) {
  .step-footer { flex-direction: column-reverse; gap: 8px; }
  .step-footer button { width: 100%; }
}
```

**Rules of thumb:**
- 1–3 fields per step (more = the screen feels like a long form again)
- Always show progress (counter + bar) — perceived-length engineering
- Always allow `Back` — irreversible steps hurt completion
- On mobile: primary CTA is full-width, sticks to the bottom of the screen
- Persist partial state across steps (and ideally across sessions) — losing answers is unforgivable

---

## 4. Empty-State Nudges

**Use when:** the user has just finished onboarding and lands on a page with no content yet
(empty inbox, empty workspace, empty project list). The bad version: a tour pop-up. The good
version: a small visual nudge inline with the empty state.

**Principle:** Don't paste a guided tour over the empty page. Make the empty state itself the
guide. T-Do apps do this beautifully — instead of "There's nothing here, take this tour", they
show a single contextual hint at the spot where the user *would* take action.

```html
<section class="empty-state">
  <div class="empty-state-illustration" aria-hidden="true">
    <!-- Lightweight SVG illustration, not a stock photo -->
  </div>
  <h2>Your first project</h2>
  <p>Projects keep related tasks together. Tap below to create one — you can rename or delete it later.</p>
  <button type="button" class="btn-primary">Create your first project</button>
  <p class="nudge">
    <span aria-hidden="true">↑</span>
    Most teams start with a "Q1 Goals" project.
  </p>
</section>
```

```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 48px 24px;
  max-width: 360px;
  margin: 0 auto;
}

.empty-state-illustration {
  width: 120px;
  margin-bottom: 24px;
  opacity: 0.85;
}

.nudge {
  margin-top: 12px;
  font-size: 0.8125rem;
  color: var(--neutral-500);
  font-style: italic;
}
```

**Anti-pattern:** Pop-up tour with "Next → Next → Next → Got it!" buttons. Universally
dismissed without reading. Replace with inline nudges at each empty state.

**When to use a tour anyway:** Genuinely complex multi-pane apps (IDEs, design tools) where
the *layout* itself needs explanation. Even then, prefer "click anywhere to dismiss" + a
persistent help button over forced sequential clicks.

---

## 5. Persistent Onboarding Checklist

**Use when:** the product has 3–7 setup tasks the user should complete in their first session
or week. Mural replaced popup tour with this pattern → **+10% week-1 retention**.

**Principle:** A checklist creates *task satisfaction* (each tick is a small win). Critically,
it **stays accessible after dismissal** — users frequently complete onboarding tasks days later
when they finally need that feature.

```html
<aside class="onboarding-checklist" aria-labelledby="checklist-title">
  <header>
    <h2 id="checklist-title">Get started</h2>
    <p class="progress-text">3 of 6 done</p>
    <button type="button" class="collapse-toggle" aria-expanded="true" aria-controls="checklist-items">
      <span class="sr-only">Collapse checklist</span>
      <svg aria-hidden="true">…</svg>
    </button>
  </header>

  <ol id="checklist-items">
    <li class="done"><a href="/profile">Complete your profile</a></li>
    <li class="done"><a href="/team">Invite a teammate</a></li>
    <li class="done"><a href="/integrations">Connect your calendar</a></li>
    <li class="active"><a href="/projects/new">Create your first project</a></li>
    <li><a href="/settings/notifications">Set up notifications</a></li>
    <li><a href="/templates">Try a template</a></li>
  </ol>
</aside>
```

```css
.onboarding-checklist {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 320px;
  background: white;
  border: 1px solid var(--neutral-200);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  z-index: 50;
}

.onboarding-checklist header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--neutral-100);
}

.onboarding-checklist ol {
  list-style: none;
  padding: 8px;
  margin: 0;
}

.onboarding-checklist li a {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  text-decoration: none;
  color: var(--neutral-700);
  transition: background 150ms ease;
}

.onboarding-checklist li a:hover { background: var(--neutral-50); }

.onboarding-checklist li::before {
  content: "○";
  display: inline-block;
  width: 16px;
  color: var(--neutral-300);
}

.onboarding-checklist li.done a { color: var(--neutral-400); text-decoration: line-through; }
.onboarding-checklist li.done::before { content: "✓"; color: var(--success); }
.onboarding-checklist li.active::before { content: "→"; color: var(--primary); }

@media (max-width: 768px) {
  .onboarding-checklist {
    bottom: 0;
    right: 0;
    left: 0;
    width: 100%;
    border-radius: 12px 12px 0 0;
  }
}
```

**Rules:**
- Show progress count prominently (`3 of 6 done`) — completion bias kicks in
- Allow collapse, never force-close. Many users complete tasks days later
- Persist completion state server-side (not just localStorage) so the list survives device switches
- Auto-hide after 100% completion (nobody wants a permanent "all done!" reminder)

---

## 6. Permission-Prime Screen

**Use when:** about to call any browser/OS permission API — notifications, geolocation,
camera, microphone, contacts. Brilliant and Calm both use this pattern; once a user denies
the native prompt, you typically can't ask again without sending them to OS settings.

**Principle:** Earn the permission first. Show a custom screen that explains *the outcome*
the user gets, then trigger the native prompt only after they say yes. The "Maybe later"
path must NOT call the native API — that preserves your ability to ask again later.

```html
<div class="permission-prime" role="dialog" aria-labelledby="prime-title">
  <div class="prime-visual">
    <!-- Mock-up of the actual notification the user will receive -->
    <div class="notification-preview" aria-hidden="true">
      <strong>Brilliant</strong>
      <p>Time for today's lesson — 5 minutes will keep your streak alive.</p>
    </div>
  </div>

  <h1 id="prime-title">Stay on track</h1>
  <p>We'll send one short reminder per day, at the time you choose. You can turn it off any time.</p>

  <button type="button" class="btn-primary" data-action="enable">
    Enable notifications
  </button>
  <button type="button" class="btn-tertiary" data-action="defer">
    Maybe later
  </button>
</div>
```

```javascript
document.querySelector('[data-action="enable"]').addEventListener('click', async () => {
  // Triggers the native prompt
  const result = await Notification.requestPermission();
  if (result === 'granted') {
    // Subscribe + confirm to user
  } else {
    // Show a soft "you can enable later in settings" message
  }
});

document.querySelector('[data-action="defer"]').addEventListener('click', () => {
  // CRITICAL: do NOT call requestPermission() here
  // Just dismiss the prime screen and remember to ask again later
  dismissPrimeScreen();
  scheduleReprompt({ days: 7 });
});
```

**Critical rule (most-broken in the wild):** The "Maybe later" path must never trigger the
native permission API. Once denied, browsers and iOS lock you out — re-asking requires the
user to manually re-enable in OS settings, which they won't do. Treat the native prompt
budget like a single bullet — only fire when you're confident the user will say yes.

**What to put on the prime screen:**
- A *concrete example* of what the permission unlocks ("a daily reminder at the time you pick")
- A *visual mock-up* of the notification, location pin, etc. — show, don't tell
- A way out that doesn't burn the permission budget

---

## 7. Loader-as-Delight

**Use when:** any synchronous operation that takes >300ms — verification, search, generation,
plan creation. Bumble animates even routine loading states (like phone-number verification),
which is one of the cheapest ways to turn perceived waiting into perceived progress.

**Principle:** Loading screens are inevitable; *boring* loading screens are not. A small
animation, a contextual message, or a value re-affirmation ("Building your personal plan…")
turns waiting into anticipation.

```html
<div class="loader" role="status" aria-live="polite">
  <div class="loader-animation" aria-hidden="true">
    <!-- Inline SVG with CSS animation, not a GIF (sharper + smaller) -->
    <svg viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="40" />
    </svg>
  </div>
  <p class="loader-message">Building your personal plan…</p>
  <p class="loader-context">Based on your answers, this will take about 5 seconds.</p>
</div>
```

```css
.loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 24px;
}

.loader-animation svg {
  width: 64px;
  height: 64px;
  animation: rotate 1.4s linear infinite;
}

.loader-animation circle {
  fill: none;
  stroke: var(--primary);
  stroke-width: 4;
  stroke-linecap: round;
  stroke-dasharray: 251;
  stroke-dashoffset: 75;
  transform-origin: 50% 50%;
  animation: dash 1.6s ease-in-out infinite;
}

@keyframes rotate { to { transform: rotate(360deg); } }
@keyframes dash {
  0%   { stroke-dashoffset: 220; transform: rotate(0deg); }
  50%  { stroke-dashoffset: 60;  transform: rotate(135deg); }
  100% { stroke-dashoffset: 220; transform: rotate(360deg); }
}

.loader-message {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.loader-context {
  font-size: 0.8125rem;
  color: var(--neutral-500);
  margin: 0;
}

@media (prefers-reduced-motion: reduce) {
  .loader-animation svg,
  .loader-animation circle { animation: none; }
  .loader-animation::after { content: "Loading…"; }
}
```

**Levers for perceived speed:**
- Show *what* is loading, not just *that* something is ("Personalising your feed…")
- If you know the duration, say it ("about 5 seconds")
- For long operations, swap messages every 1.5–2s ("Building plan…" → "Adding goals…" → "Almost ready…")
- Always honour `prefers-reduced-motion` — the spinner becomes a text label

**Skeleton loaders** are a complementary pattern: show the shape of the upcoming UI greyed-out
during fetch. Better than spinners for content lists; worse than animated loaders for
single-screen waits where the user has nothing to anticipate.

---

## 8. Mascots & Micro-Celebrations

**Use when:** the product has a long onboarding flow (>20 screens) or wants a memorable
brand voice. BitePal's user-named raccoon mascot is the textbook example — 61 onboarding
screens that don't feel long because the mascot makes each step feel like a relationship
moment.

**Principle:** Long flows survive *if and only if* they create emotional touchpoints along
the way. A mascot is the most ergonomic vehicle: it personalises tone ("Pip thinks you're
ready!"), absorbs friction ("Pip is checking your answers…"), and creates micro-celebrations
("Pip is so proud of you!") that re-energise the user.

**Implementation guidance:**
- Don't bolt a mascot onto an existing flow — design the flow around it
- Give the mascot a single, repeatable visual style (one face, multiple expressions)
- Let the user *name* the mascot if it makes sense (pets, tutors, plants) — naming creates ownership
- Use the mascot at three moments: routine waits (loaders), milestones (achievements), and recoveries (errors)
- Keep mascot messages short (≤2 lines) — long mascot dialogue grates fast

For the visual production of the mascot itself, image prompts, and sprite-sheet workflow,
hand off to the `image-toolkit` skill.

**Micro-celebrations** without a mascot:
- Confetti burst on first action (CSS-only or canvas-confetti library)
- Number ticker on first metric (`useCountUp`)
- Subtle haptic feedback on mobile (`navigator.vibrate(15)`) — single short pulse, not a long buzz

---

## 9. Onboarding-UI Anti-Patterns

| Anti-pattern | Why it fails | Replace with |
|---|---|---|
| Welcome carousel of 3–5 feature slides | Users swipe through without reading; high drop-off at slide 2 | Outcome-first single welcome screen + try-before-signup |
| Forced sequential pop-up tour | Universally dismissed; nothing remembered | Inline empty-state nudges + persistent checklist |
| Long single signup form | Telegraphs effort; abandonment at field 5+ | Multi-step form with progress bar |
| Native permission prompt with no priming | One denial = locked out | Permission-prime screen with mock-up |
| "Maybe later" that calls the native API | Burns permission budget instantly | Defer button must NOT trigger the native prompt |
| Generic spinner with no context | Every second feels like 3 | Loader with what-is-happening message |
| Quiz that disappears into the void | User feels like data donor; no commitment | Quiz with visible personalised outcome screen |
| Tour pop-up over an empty state | Stacks two pieces of friction at once | Empty state IS the guide |
| Auto-trigger video sound on welcome screen | Users immediately bounce to mute or close | Default mute; user opts into sound |
| Onboarding even when first-touch = aha (AI chat, search) | Every screen is conversion loss | Skip onboarding entirely — drop user into the product |

---

## How to Apply This in a UI Audit

When reviewing an onboarding flow's UI:

1. **Welcome screen.** Carousel of features, or product in action / try-before-signup?
2. **Forms.** Single long form, or multi-step with progress?
3. **Validation.** Submit-then-error, or live as-you-type?
4. **Concept-heavy fields.** Front-loaded glossary screen, or contextual tooltips?
5. **Permissions.** Bare native prompt, or pre-prime screen with mock-up?
6. **Loaders.** Bare spinner, or contextual message + (if known) duration?
7. **Empty state after onboarding.** Pop-up tour, or inline nudges + persistent checklist?
8. **Long flow (>20 screens).** Boring, or has a mascot / micro-celebrations / value re-emphasis?
9. **`prefers-reduced-motion`.** Animations honoured, or forced on everyone?

For *whether* a pattern should be present at all (strategy), hand off to the
**conversion skill (sales plugin)** — conversion-/PLG-psychology lives there, not here.

---

## Source

Mobbin — *I Studied 1,460 Onboarding Flows. Here's What I Found.* (2026, ~10 min)
https://www.youtube.com/watch?v=Qsq-Sj_rojU — pattern attributions cited inline.
