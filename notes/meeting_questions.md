# Supervisor Meeting — Questions to Confirm for the T1000 Thesis

**Author:** Steven Braun
**Audience:** Company / technical supervisor(s) at Emerson (Praxis-Betreuer)
**Date:** 2026-07-21
**Purpose:** Explain what I am building and why it helps the company, then get key
statements *confirmed* so they can be cited in the thesis. Deep numeric
derivations belong to Fatemeh (pipeline author) — see the last section.

---

## Part A — What I am doing and how it helps Emerson (say this first)

**What I am building**

- A **data-quality preprocessing layer** on top of the existing ERA recording
  pipeline that decides *which recorded actuator cycles are physically usable at
  all*, before any further analysis.
- Approach: **physical-plausibility checking** — domain/physics-based
  accept/reject gates, each rejection carrying an explicit `rejection_reason`.
  This is **methodologically independent from and complementary to** Fatemeh's
  statistical outlier detection (Median + MAD).
  Physics answers *"are these data usable at all?"*; statistics answers
  *"is this cycle unusual vs. its neighbours?"*
- Three deliverables:
  1. **Decision tree** — the accept/reject logic.
  2. **Data pool** — an index of passing cycles + a rejection log; raw files stay
     untouched.
  3. **HTML cycle dashboard** — a browsable view a test engineer opens daily.

**Why it helps Emerson**

- A trustworthy, **auditable pool** of valid ERA cycles — every rejection has a
  physical reason, so an engineer sees *what* is wrong, not just *that* something
  deviates.
- **Catches whole-batch faults** that a purely statistical method would absorb as
  "normal" (masking) — physics needs no healthy reference population.
- **Reproducible and non-destructive** — raw recordings stay intact, cycles are
  only *flagged*; the pool is an index. (Central scientific argument + audit
  guarantee.)
- Sensible ordering: apply the physical floor **first**, then run statistics on
  the cleaned pool — the two theses combine into one pipeline rather than compete.

---

## Part B — Questions to get confirmed

For each: the question, and why it matters for the thesis.

### 1. Motivation / problem statement
- [ ] Is it correct that recorded ERA data currently has **no automated physical-
      usability gate**, and that unusable cycles reaching analysis is a real,
      recognised problem here?
  - *Why:* lets me write the motivation as a confirmed company need, not an
    assumption.

### 2. Scope agreement / deliverables
- [ ] Do you agree that my three deliverables — **decision tree, data pool with
      rejection log, and HTML cycle dashboard** — are the right and sufficient
      scope for this task?
  - *Why:* locks scope before writing; protects me at the defense.

### 3. Users and usage
- [ ] Who exactly will use the pool and dashboard (**which team / role**), and in
      what workflow?
  - *Why:* turns "for engineers" into a concrete, named use case.

### 4. Complementarity vs. duplication (important)
- [ ] Do you confirm my physical-plausibility layer is a **distinct, independent
      contribution** alongside Fatemeh's statistical detection — first physical
      gate, then statistics on the cleaned pool?
  - *Why:* the single strongest argument that my work stands on its own. Get it on
    record.

### 5. Signal semantics / physics (company can confirm these)
- [ ] Is the ERA actuator **position-controlled**, following a predefined position
      trajectory?
  - *Why:* underpins choosing Position as the reference signal (today only
    justified via Fatemeh's ADR-007; a company confirmation strengthens it).
- [ ] What are the **physical meaning and units** of the Position signal, its
      expected **stroke range**, and its **rest value**?
  - *Why:* I need the unit to defend any position-based threshold as physically
    meaningful rather than a magic number.
- [ ] Which signals are **core vs. supplementary** — is **vibration** genuinely
      optional / duty-cycled?
  - *Why:* confirms the optional-vibration handling in dataset validation.

### 6. Data provenance
- [ ] Are the `ERAP_EXT_00X` recordings **representative production data**, and may
      I document their origin / conditions in the thesis?
  - *Why:* needed to argue the pool is representative.

### 7. Thresholds — close now or declare provisional? (decision I need)
- [ ] For the thesis, do you want the open thresholds **finalised from Stage-8
      distributions before I write**, or is it acceptable to **declare them openly
      as provisional**?
  - *Why:* in a physics-based approach an unjustified threshold is a real weakness;
    your stance decides my timeline and framing.

### 8. Sign-off
- [ ] Can you **approve the Confluence document** (pipeline overview + decision
      tree + standstill definition) before I begin writing?
  - *Why:* a hard gate before Schreibbeginn in my plan.

### 9. IP / publication constraints
- [ ] Any **confidentiality limits** on data, thresholds, or screenshots I can show
      in the thesis?
  - *Why:* avoids late rework.

---

## Defer to Fatemeh (NOT this meeting)

These are pipeline-internal numeric derivations — raise them with the master
student, not the company supervisor:

- [ ] Derivation of `movement_threshold = 1.0` (magic number, duplicated 3×).
- [ ] Session gap `3600 s` — ADR-006 says "Accepted", the code comment says
      "exploratory": which is current?
- [ ] Velocity scaling (blocks Variant B of the standstill definition).
- [ ] Confirmed cycle duration (~3.1 s vs. the outdated 1.81 s figure).
- [ ] Minimum session size N (proposed: 100).
