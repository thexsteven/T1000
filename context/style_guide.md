# Style Guide T1000

Structural and stylistic conventions, derived from two sample theses (Kisro, DE; Rahimian, EN) and aligned with this project's actual setup.
Context: project thesis "T1000", DHBW Bad Mergentheim, Applied Computer Science (Bachelor of Science), training company Emerson Electric (Laatzen).

> This guide describes **structure, layout, and language style only** — it makes no content prescriptions. It serves as a formal template for the T1000 thesis.

---

## 1. Overall Structure and Length

- **Language:** English throughout (`english` document option). An **Abstract** in English is mandatory; the English thesis also supplies **Keywords**. (A German thesis would instead add a *Kurzfassung*.)
- **Main-part length:** ~25–30 pages (arabic page numbers from Chapter 1). Full document incl. front and back matter ~35–40 pages.
- **Page numbering:** front matter in Roman numerals (I, II, III, …), main part in arabic from 1, page number in the footer (outer/centered). The bibliography and appendix continue in Roman numerals after the main part.
- **Number of main chapters:** 6 numbered chapters (see §2).

### Document order

**Front matter (Roman numerals):**
1. Cover page — topic, "T1000", name, matriculation number; metadata block: processing period, course/student ID, training company / dual partner (location), supervisor at the training company, reviewer, degree, study program, DHBW location, submission date.
2. Confidentiality Clause (*Sperrvermerk*) — standard DHBW text; place/date/name/signature.
3. Declaration (*Erklärung*) — standard formula "independently written … no sources other than those stated"; place/date, signature.
4. Abstract (English).
5. Keywords (English thesis) — *or* Kurzfassung (German thesis).
6. Table of Contents.
7. List of Figures.
8. List of Tables and, if applicable, List of Listings / List of Abbreviations (glossary).

**Main part (arabic):** Chapters 1–6 (see below).

**Back matter (Roman numerals continue):**
- Bibliography.
- Appendix — large-format diagrams, sample documents, supplementary listings.

---

## 2. Chapter Logic and Lengths (Main Part)

Underlying pattern = **hourglass**: from broad foundations → to the concrete implementation → back to broad reflection.

| Ch. | Title | Function | Target length |
|-----|-------|----------|--------------|
| 1 | Introduction | Motivation, problem statement, objectives/research questions, approach, scope, structure of the thesis | 2–3 p. |
| 2 | Theoretical Foundations | Define all technical terms and concepts introduced in Chapter 1 | 6–8 p. (largest foundations chapter) |
| 3 | Methodology | The developed method/approach: reading & cleaning data → segmentation → alignment → overlay | 5–7 p. |
| 4 | Analysis | Practical core: apply the method to the case-study data set and evaluate the results | 8–10 p. (most extensive chapter) |
| 5 | Derivation of Recommendations | Interpret results, derive practical recommendations for day-to-day use | 2–4 p. |
| 6 | Conclusion | Compare against the stated objectives, name limitations, give an outlook | 1–2 p. |

**Structural logic in detail:**
- The **Introduction** explicitly announces the structure (a "Structure of the Thesis" section that walks through Chapters 2–6). It is split into sub-sections: Motivation, Problem Statement, Objectives and Research Questions, Approach, Scope.
- The **Theoretical Foundations** chapter defines exactly the terms named in the Introduction, in the same order. Deep nesting is allowed (down to level x.y.z, e.g. 2.3.1 / 2.3.2).
- The **Methodology** chapter describes the general approach and design decisions independently of the concrete data set. Together with the Analysis chapter it holds most of the code and the author's own figures.
- The **Analysis** chapter follows the real project flow (apply → observe → evaluate) against the case-study data. Here lie the results, the author's own figures, and result tables.
- The **Recommendations** chapter turns the analysis into actionable guidance for using the tool in practice.
- The **Conclusion** revisits the objectives set in the Introduction and checks each one; it honestly names limits/drawbacks and closes with an outlook on follow-up work.

**Nesting depth:** usually two levels (x.y), three (x.y.z) where needed. Split every main chapter into ≥ 2 sub-sections; no single lone sub-section.

---

## 3. Language Register and Phrasing Patterns

**Overall tone:** factual, descriptive-explanatory, technical but accessible. Explains concepts for a reader without deep prior knowledge.

**Person/Tense:**
- Prefer the impersonal passive and impersonal subjects ("this work", "the tool", "the pipeline reads …", "the data is aggregated …"). The first-person plural ("we use a Python script", "we decided to use …") is acceptable but should be used consistently, not mixed arbitrarily with the passive.
- Present tense for descriptions and definitions; past tense for the project narrative (what was done during the project).

**Technical terms:**
- Spell out on first mention, with abbreviation/expansion in parentheses: "ADC (Analog-to-Digital Converter)", "OOP (Object-Oriented Programming)", "HTML (HyperText Markup Language)".
- Keep established English technical terms; introduce and explain them once.

**Typical opening / transition formulas:**
- Chapter opener with preview: "This chapter introduces …", "In the following, … is described."
- Sequencing: "First, …", "Second, …", "A further important … is …", "The next point concerns …".
- Definition: "An X is …", "X denotes …", "By X we mean …".
- Back-reference: "As already described …", "With respect to the components mentioned above …".

**Paragraph construction:** manageable paragraphs (5–12 lines), one idea per paragraph. Use lists for criteria/principles/outlook points (bulleted or numbered).

**AI note:** where a section was produced with AI software (e.g. abstract, keywords, introduction), add a footnote "This … was generated with AI software." — keep this transparency convention where it applies.

---

## 4. Handling Figures, Tables, and Code

**Figures:**
- Numbered consecutively with a caption: "Figure N: Title (Author, Year)".
- **Always state the source** — for own graphics "Author's own work, 2026", otherwise cite as in the bibliography.
- Every figure is referenced and explained in the running text ("as shown in Figure N", "the figure above illustrates …").
- All figures listed in the **List of Figures** with title and page number.

**Tables:**
- Numbered analogously: "Table N: Title (source)". For extensive data tables, use a dedicated List of Tables.

**Code / Listings:**
- Code blocks in monospace, embedded near the running text, in small meaningful units (a header definition, constructor, loop, or query — not a whole file).
- **Each block is followed by a prose explanation**, often line by line / identifier by identifier ("`std::vector<float>` means that …", "the `for` loop iterates over …").
- Keywords, variable, and method names appear in monospace in the running text.

---

## 5. Citation Style and Density

**Style — Harvard / in-text (biblatex, `agsm`):**
- This thesis uses **in-text author–year citations** via biblatex. Use `\parencite{key}` for a parenthetical "(Author, Year)" reference and `\textcite{key}` when the author is part of the sentence ("Author (Year) shows …").
- Direct quotations go in quotation marks with the source; keep them sparse.
- Do **not** mix in a footnote citation style — stay with in-text author–year throughout.

**Density — staggered by chapter type:**
- **Theoretical Foundations:** high citation density, ~1–4 references per page; nearly every factual claim is backed. Direct quotations sparingly, to pin down central definitions.
- **Methodology / Analysis:** very low to no citation density — this is the author's own work and own figures. Cite only for adopted tool definitions or external methods.
- **Introduction / Conclusion:** few to no citations (the Introduction may cite to motivate the problem, as in the motivation and problem-statement sections).

**Bibliography (`ArbeitBib.bib`):**
- ~20–25 sources. A mix of web sources, textbooks, and papers.
- Uniform format via biblatex (`agsm` style), sorted alphabetically; for web sources include URL and access date.
- Every source cited in the text appears in the bibliography and vice versa.

---

## 6. Quick Checklist for the T1000

- [ ] Cover page with complete metadata block, confidentiality clause, declaration
- [ ] Abstract (EN) + Keywords (EN)
- [ ] Table of Contents, List of Figures, List of Tables / Abbreviations
- [ ] 6 main chapters in the hourglass pattern (foundations → implementation → reflection)
- [ ] Introduction announces the structure; Theoretical Foundations covers every term it named
- [ ] Technical terms spelled out on first mention + abbreviation
- [ ] Figures/tables numbered, source stated, referenced in the text
- [ ] Code in blocks + following prose explanation
- [ ] Citation density high in theory, low in implementation; one citation style (Harvard in-text) throughout
- [ ] Bibliography complete and consistent
- [ ] AI-generated sections marked with a footnote (where applicable)
