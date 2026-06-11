# Design: Committee Rejection Update — 11 June 2026

## Context

On Wednesday 10 June 2026, Uttlesford District Council's planning committee
**unanimously refused** both City & Country applications (Stansted and
Birchanger). The Local Plan 2021-2041 has been **adopted**; it identifies
Birchanger as not an appropriate location for new housing allocations and
meets housing targets without building on Green Belt around Stansted.

It is not over: City & Country may appeal to the Planning Inspectorate, and
the government has 21 days (to ~1 July 2026) to call the decision in. The
written decision notice has **not yet arrived**, so exact refusal terms are
unknown.

## Decision: measured update now, full pivot later

Agreed approach: a **measured banner update**, not a full homepage redesign.
The big "victory pivot" waits until the written decision arrives and the
call-in window closes.

## Changes

### Homepage (index.html)
- Alert banner → victory-green "FIRST HURDLE WON — BOTH APPLICATIONS
  UNANIMOUSLY REJECTED" with vigilance caveats (appeal possible, 21-day
  call-in window, written decision awaited).
- Hero "Deadline Update" box → "Decision Update" box with the same news.
- Objection progress bar reframed as a thank-you record ("Your objections
  made the difference"); milestone tooltips moved to past tense; live
  counters kept as a record of opposition.
- "Object now" guidance lines removed; share-button text (static and in JS)
  changed to spread the news instead of soliciting objections.
- Timeline: Phase 4 (Local Plan) and Phase 5 (Decision) marked complete;
  new Phase 6 "Appeal & Call-in Window" marked active.
- "THIS IS NOT A DONE DEAL!" box → "FIRST HURDLE WON — STAY VIGILANT".
- "Object to the Plan" action card → "Stay Vigilant" (newsletter signup).
- All "emerging Local Plan" wording → "adopted Local Plan 2021-2041".
- Meta/OG descriptions updated to reflect the refusal.

### Village pages (birchanger.html, stansted.html)
- Alert banners ("application expected imminently… 21 days to object") →
  refusal news for each village's application.
- Sticky CTA bar ("Every objection matters — add yours today!") →
  stay-informed message.
- "Object to the Plan"-style action cards softened to vigilance framing.

### timeline.html
- Phases 1–5 marked completed (consultations, EIA, application, Local Plan
  adoption, committee refusal on 10 June 2026).
- Phase 6 → active "Appeal & Call-in Window".
- Key takeaway box updated to first-hurdle-won framing.

### styles.css
- New `.alert-banner.victory` variant (green palette, 🎉 icon).

## Deferred (for when the written decision arrives / window closes ~1 July 2026)
- Publish exact refusal reasons + links to decision notices.
- Full victory hero redesign.
- Blog announcement post (Contentful, outside this repo).
- Long-term shape of the site if the window passes quietly.

## Operational note
The local git repo had corrupt loose objects (empty files under
`.git/objects/`); repaired on 11 June 2026 by moving them aside and
re-fetching from origin.
