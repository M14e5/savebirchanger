# Design: Called-In Update — 6 July 2026

## Context

On Wednesday 10 June 2026, Uttlesford District Council's planning committee
unanimously refused both City & Country applications (Stansted, 300 homes;
Birchanger, 180 homes). On 1 July 2026 the Secretary of State used new
call-in powers to take both applications out of the council's hands before
it could issue refusal notices. The whole case is now examined afresh at a
public inquiry run by an independent Planning Inspector, with the council
appearing to defend its refusal reasons and City & Country arguing its case.

Both parish councils and the residents' group intend to seek Rule 6 status
so expert evidence (flooding, traffic, noise) can be presented and the
developer's witnesses cross-examined on the community's behalf. This needs
hired experts and groundwork — no fundraising ask is being added yet.

The Planning Inspectorate will shortly confirm a timetable: statements due
within six weeks, inquiry itself expected late 2026 at the earliest, more
likely early 2027. Separately, any resident can write to the Inspectorate's
case officer with their views before a deadline expected around mid-August
2026 (exact date/address TBC, to be confirmed once published). Final
ministerial decision realistically 2027. This guarantees evidence is heard
and tested, not a particular outcome — echoing "won the first battle, not
the war."

## Decision: retire "victory" framing site-wide

Unlike the 11 June update (measured banner tweak, kept the victory-green
styling because the refusal was real and final at committee level), this
update fully retires the victory/celebration framing across the site. The
council's refusal is preserved as context/evidence of the council's
position, but the framing shifts to "the fight continues at inquiry" —
because the council will never issue that refusal notice, and the
call-in is now a fact, not a 21-day risk to stay vigilant against.

## Changes

### Homepage (index.html)
- Hero copy, "Decision Update" panel, and share-button messages (X,
  Facebook, Reddit, WhatsApp, Bluesky — static links + JS `shareMessage`)
  rewritten from "Victory! ...rejected" to explain the call-in and invite
  people to help make sure local evidence is heard at inquiry.
- Alert banner (`#decision-news`) retitled "CALLED IN — BOTH APPLICATIONS
  NOW GO TO A PUBLIC INQUIRY"; drops `.victory` green/confetti styling for
  a neutral/alert tone; explains in plain terms that the committee's vote
  stands as the council's case but Whitehall now decides.
- Objection meter: live counts (`hero-total`, `birchanger-count-hero`,
  `stansted-count-hero`, fed by `monitoring_data/latest.json` via the
  hourly geocoding cron) are frozen/relabelled as a record of the
  community response that helped win the unanimous refusal — no longer
  presented as a live milestone bar, since there is no equivalent feed
  for inquiry-stage submissions. That hero slot's call-to-action becomes
  a static "Write to the Planning Inspectorate" panel: deadline expected
  ~mid-August 2026, exact date/address "to be confirmed — sign up for
  updates."
- Timeline: replace old "Phase 6: Appeal & Call-in Window" (was a live
  21-day countdown) with:
  - Phase 6 (1 July 2026, completed): "CALLED IN BY THE SECRETARY OF
    STATE."
  - Phase 7 (now active): "PUBLIC INQUIRY PREPARATION" — timetable
    pending, statements due within six weeks, inquiry expected late
    2026/early 2027, Rule 6 status being sought, resident letters to the
    case officer due ~mid-August 2026 (TBC).
  - Phase 8 (upcoming): "INSPECTOR'S REPORT & MINISTERIAL DECISION" —
    realistically 2027.
  - Closing key-message callout → "ONE HURDLE WON, THE NEXT FIGHT IS AT
    INQUIRY", echoing "won the first battle, not the war" and the
    evidence-heard-not-outcome-guaranteed point.
- Action section: add a "Write to the Case Officer" card emphasising
  personal, objective, first-hand knowledge (lanes, traffic, flooding,
  school run, the fields, Bishop's Stortford growth) over emotional
  appeals; add Rule 6 explainer text (parish councils + residents' group
  seeking standing to present expert evidence and cross-examine
  witnesses) without a donation ask.
- Meta/OG description updated from "First hurdle won... unanimously
  refused" to reflect the call-in and inquiry.

### Village pages (birchanger.html, stansted.html)
- Alert banners → call-in news per village ("180 homes in Birchanger" /
  "300 homes in Stansted"), same tone as the homepage banner.
- Sticky CTA bar text ("First hurdle won - both applications refused!
  Stay informed in case of an appeal") → reflects the call-in/inquiry
  instead of a hypothetical appeal.

### timeline.html
- Same Phase 6/7/8 restructure as the homepage's inline timeline, kept in
  sync; key-takeaway box updated to match.

### documentation.html
- Short note near "Secretary of State Referral Documents" flagging the
  call-in has happened and that Inspectorate/inquiry documents will be
  added as published — no fabricated links.

### Blog post (Contentful — outside this repo)
Blog posts are pulled live from a Contentful CMS space referenced in
blog.html; editing files here can't publish a new post. Draft copy below
is ready to paste in once someone with Contentful access publishes it:

> **Title:** Called In: Both Applications Now Go to a Public Inquiry
>
> On 1 July 2026 the Secretary of State used new powers to "call in" both
> planning applications that Uttlesford's planning committee was minded to
> reject — the 300 homes at Forest Hall Road, Stansted Mountfitchet, and
> the 180 homes west of Birchanger Lane, Birchanger.
>
> In plain terms: although the committee voted unanimously on 10 June to
> refuse both schemes, the Government has taken the final decision out of
> the council's hands and will make it in Whitehall instead. The council
> will never get to issue its refusal notices. This doesn't undo the
> committee's vote — it means the whole case will now be examined afresh
> from where they left it.
>
> Both applications will be tested together at a public inquiry run by an
> independent Planning Inspector. The council will appear to defend its
> reasons for refusal — the local plan, housing numbers, the Green Belt
> argument — while the developer argues its case.
>
> The community can take part too, but only through a formal process: both
> parish councils and the residents' group intend to seek formal standing
> (known as "Rule 6" status) so that expert evidence can be presented and
> the developer's witnesses questioned on the community's behalf — covering
> flooding, road safety, and noise with objective evidence. This means
> hiring experts and doing the groundwork to be taken seriously.
>
> After the inquiry, the Inspector writes a report and recommendation, and
> the Minister makes the final decision — realistically in 2027. We should
> be honest: this process guarantees our evidence is heard and properly
> tested in public. It does not guarantee the outcome. The decision could
> go either way.
>
> Even without the call-in, City & Country would likely have appealed
> anyway, so we'd have ended up here one way or another. That's why we've
> been saying all along: we've won the first battle, but not the war.
>
> **What happens next, and one thing you can do now.** The Planning
> Inspectorate will shortly confirm the timetable — statements are needed
> within six weeks, and the inquiry itself is likely later this year at
> the earliest, more likely early next year.
>
> In the meantime, any resident can write to the Planning Inspectorate's
> case officer with their views on the called-in applications. There's a
> deadline, expected around mid-August — we'll confirm the exact date and
> address as soon as the Inspectorate publishes them.
>
> City & Country will be using their PR agency to try to flood the
> Planning Inspectorate with supportive responses, so we need the same
> level of support we saw during the original planning proposal.
>
> If you write, please use your own words and speak objectively: what you
> personally know about the lanes, the traffic, the flooding, the school
> run, the fields between our villages, and the growth of Bishop's
> Stortford carries far more weight with an Inspector than anything
> emotional.

## Deferred
- Exact Inspectorate deadline/address and case reference — to be added
  once published (site currently says "to be confirmed").
- Inquiry timetable details once the Inspectorate confirms them.
- Rule 6 fundraising mechanism, if one is set up later.
- Publishing the blog post above (needs Contentful access).
