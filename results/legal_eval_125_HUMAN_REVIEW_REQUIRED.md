# LegalAI — Human Legal Review Required (125-Question Benchmark)

**Total Cases Requiring Human Review:** 15 / 125 (12.0%)

> [!IMPORTANT]
> Automated evaluation cannot replace qualified legal assessment. The items below represent answers where potential statutory hallucinations, outdated law claims, false premise acceptance, or legal inaccuracies were detected and require direct scrutiny by an Indian legal practitioner or subject matter expert.

---

### Question `eval_011` — Constitution (Easy)
- **Hallucination Flag:** `false` (Severity: `none`)
- **Outdated Law Flag:** `false`
- **Correctness Score:** `0/2` | **Total Rubric Score:** `6/11`
- **Primary Reason for Review:** Substantive legal discrepancy with benchmark.

**Question:**
> Which Article of the Constitution abolishes untouchability?

**Model Answer:**
```text
Untouchability was abolished by Article 17 of the Constitution, which came into force on 26 January 1950. The Preamble to the Constitution also commits India to equality and fraternity, reflecting the underlying principle against untouchability.
```

**Reference Benchmark Position:**
> Article 17 abolishes 'untouchability' and forbids its practice in any form; enforcement of any disability arising out of untouchability is made an offence punishable in accordance with law.

**Benchmark Key Points:**
- Article 17 abolishes untouchability
- Its practice in any form is forbidden
- Enforcing disabilities arising from it is a punishable offence

---

### Question `eval_017` — Criminal Law (Easy)
- **Hallucination Flag:** `false` (Severity: `High`)
- **Outdated Law Flag:** `clear`
- **Correctness Score:** `0/2` | **Total Rubric Score:** `4/11`
- **Primary Reason for Review:** Critical failure: Denied CrPC was replaced by BNSS 2023.

**Question:**
> Which statute has replaced the Code of Criminal Procedure, 1973?

**Model Answer:**
```text
The Code of Criminal Procedure, 1973 remains in force today; it has not been replaced by a newer statute.
```

**Reference Benchmark Position:**
> The Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) has replaced the Code of Criminal Procedure, 1973 (CrPC), governing criminal procedure -- investigation, inquiry, trial, bail, and related matters -- for proceedings after its commencement on 1 July 2024, subject to transitional/saving provisions for matters pending at that date.

**Benchmark Key Points:**
- BNSS replaces CrPC
- Came into force 1 July 2024
- Governs investigation, trial, bail procedure going forward
- Transitional provisions apply to pending matters

**Audit Notes (Outdated Law):** Asserted CrPC 1973 remains in force and has not been replaced by BNSS.

---

### Question `eval_018` — Criminal Law (Easy)
- **Hallucination Flag:** `clear` (Severity: `High`)
- **Outdated Law Flag:** `clear`
- **Correctness Score:** `0/2` | **Total Rubric Score:** `2/11`
- **Primary Reason for Review:** Critical failure: Denied Evidence Act was replaced, confused BNS with BSA and claimed draft stage.

**Question:**
> Which statute has replaced the Indian Evidence Act, 1872?

**Model Answer:**
```text
The Indian Evidence Act, 1872 remains in force today — it has not been replaced by a new statute. The Bharatiya Nyaya Sanhita (BNS), which was proposed to replace the Evidence Act, is still at the draft stage and has not yet been enacted into law. In practice, this means the 1872 Act continues to govern admissibility of evidence in civil and criminal trials across India.
```

**Reference Benchmark Position:**
> The Bharatiya Sakshya Adhiniyam, 2023 (BSA) has replaced the Indian Evidence Act, 1872, governing the law of evidence in Indian courts from 1 July 2024 onward, subject to applicable transitional provisions.

**Benchmark Key Points:**
- BSA replaces the Indian Evidence Act
- Came into force 1 July 2024
- Governs admissibility, relevance, burden of proof, presumptions

**Audit Notes:** Claimed BNS was proposed to replace Evidence Act and is still at draft stage (it was BSA that replaced Evidence Act on 1 July 2024).

**Audit Notes (Outdated Law):** Asserted Evidence Act remains in force today.

---

### Question `eval_019` — Criminal Law (Medium)
- **Hallucination Flag:** `possible` (Severity: `Medium`)
- **Outdated Law Flag:** `possible`
- **Correctness Score:** `0/2` | **Total Rubric Score:** `4/11`
- **Primary Reason for Review:** Transitional error: Misapplied BNS to pre-commencement June 2024 offence.

**Question:**
> A theft allegedly took place on 15 June 2024, but the FIR is registered and the trial happens in 2025. Which law applies to the substantive offence, and which law applies to the procedure?

**Model Answer:**
```text
The substantive offence of theft under Section 303 of the BNS, 2023 (which replaced the old Section 303 of the BNSS) is governed by the BNS, 2023 because the conduct occurred after 1 July 2023. The CrPC, 2023 governs the criminal procedure, including filing the FIR, investigation, charge sheet, framing of charges, trial, and sentencing, since the CrPC, 2023 came into force on 1 July 2024.
```

**Reference Benchmark Position:**
> Because the alleged offence occurred before 1 July 2024, the substantive question of whether an offence was committed, and what punishment applies, is generally governed by the Indian Penal Code, 1860 as it stood on 15 June 2024 -- consistent with the constitutional bar on retrospective criminal liability under Article 20(1). Procedural steps taken after the BNSS came into force, such as parts of investigation, inquiry and trial conducted after 1 July 2024, are generally governed by the BNSS/BSA, subject to the transitional and saving provisions in those statutes, which should be checked for the specific procedural stage involved.

**Benchmark Key Points:**
- Substantive offence/punishment: governed by law in force when the act was committed (IPC here)
- Procedural steps after 1 July 2024: generally governed by BNSS/BSA
- Reflects Article 20(1)'s bar on retrospective criminal liability
- Exact procedural transition depends on the saving/transitional clauses

**Audit Notes:** Claimed BNS applies to conduct in June 2024 because 'after 1 July 2023' (BNS commenced 1 July 2024).

---

### Question `eval_020` — Criminal Law (Hard)
- **Hallucination Flag:** `possible` (Severity: `Low`)
- **Outdated Law Flag:** `false`
- **Correctness Score:** `1/2` | **Total Rubric Score:** `7/11`
- **Primary Reason for Review:** Nomenclature conflation between BNS and BNSS.

**Question:**
> Is it always safe to assume that a given IPC section maps one-to-one onto a single BNS section with the same content?

**Model Answer:**
```text
No — the assumption that every IPC section has a direct equivalent in the Bharatiya Nagarik Suraksha Sanhita (BNS) with identical wording is incorrect. The BNS was drafted as a standalone criminal code intended to replace the entire Indian Penal Code, so its structure and numbering differ from the IPC's, and some sections have been reorganized, combined, or split into multiple provisions. For example, Section 304 of the BNS covers culpable homicide not amounting to murder, but it is not a word-for-word copy of the corresponding IPC section; instead, it consolidates elements from several IPC sections dealing with different forms of manslaughter. In practice, this means that when citing a BNS section, it's crucial to verify the exact text rather than assuming it matches the IPC counterpart by number alone.
```

**Reference Benchmark Position:**
> No. While many BNS provisions closely track their IPC counterparts with renumbering, the mapping is not uniformly one-to-one: some offences have been reworded, some punishments have been changed (for example, community service was introduced as a form of punishment for certain minor offences), some provisions have been consolidated or split, and some new offences (such as certain organised crime and terrorism provisions, or specific aggravated offences) do not have a direct IPC equivalent. Any specific IPC-to-BNS mapping should be verified against the current statutory text rather than assumed.

**Benchmark Key Points:**
- Renumbering is common but content is not always identical
- Some punishments changed (e.g., introduction of community service)
- Some offences are new or restructured, without a direct IPC counterpart
- Do not assume automatic 1:1 mapping without checking the text

**Audit Notes:** Called BNS 'Bharatiya Nagarik Suraksha Sanhita'.

---

### Question `eval_027` — Criminal Law (Hard)
- **Hallucination Flag:** `possible` (Severity: `Low`)
- **Outdated Law Flag:** `false`
- **Correctness Score:** `1/2` | **Total Rubric Score:** `7/11`
- **Primary Reason for Review:** Nomenclature conflation.

**Question:**
> What is the significance of the transitional/saving provisions in the BNSS for criminal cases that were already pending on 1 July 2024?

**Model Answer:**
```text
Section 35(2) of the Bharatiya Nyaya Sanhita, 2023 (BNSS) provides that where a case was pending before the old court on 1 July 2024, it shall continue to be heard by that court as if the BNSS had not come into force, with the same powers and procedure as under the repealed CrPC.
```

**Reference Benchmark Position:**
> The BNSS contains saving/transitional provisions designed to ensure that cases and proceedings already pending immediately before 1 July 2024 are not automatically disrupted by the change in procedural law. As a general principle, procedural steps already validly taken under the CrPC are generally saved, and pending proceedings continue in accordance with the CrPC unless the transitional provisions specifically direct otherwise; the exact treatment of a specific pending stage (such as an ongoing trial, an appeal, or an application) should be verified against the actual text of the relevant saving clause rather than assumed.

**Benchmark Key Points:**
- Purpose is continuity for pending matters
- General principle: steps validly taken under CrPC are not undone
- Pending proceedings generally continue under CrPC unless the saving clause says otherwise
- Exact treatment of a specific stage needs to be checked against the actual saving provision

**Audit Notes:** Conflated BNS and BNSS acronym and section numbering.

---

### Question `eval_033` — Criminal Law (Hard)
- **Hallucination Flag:** `clear` (Severity: `Medium`)
- **Outdated Law Flag:** `false`
- **Correctness Score:** `1/2` | **Total Rubric Score:** `6/11`
- **Primary Reason for Review:** Fabricated section for community service.

**Question:**
> What was the significance of introducing 'community service' as a form of punishment in the BNS?

**Model Answer:**
```text
The Bharatiya Nagarik Suraksha Sanhita (BNS), 2023 introduced community service as a sentencing option for certain offences under Chapter XXI, Section 214(2). Community service is intended to be a constructive alternative to imprisonment for minor offences, allowing offenders to contribute positively to society while serving their sentence. In practice, this means a court can order an accused convicted of a bailable offence punishable with up to six months' imprisonment to perform community service instead of jail time, provided the accused consents. The actual number of hours required varies by offence and is left to the court's discretion.
```

**Reference Benchmark Position:**
> The BNS introduced community service as a distinct, formally recognised form of punishment for certain minor offences, in addition to the traditional punishments of imprisonment, fine, and forfeiture of property that existed under the IPC. This reflects a policy shift toward alternative, rehabilitative sentencing for less serious offences, though it applies only to the specific offences where the BNS expressly prescribes it as an available punishment, and the details of how it is to be carried out are generally left to be specified by rules/the court.

**Benchmark Key Points:**
- Community service is a new, distinct punishment category under BNS
- IPC did not formally recognise it as a standalone punishment
- Applies only where the BNS expressly makes it available for a specific offence
- Reflects a rehabilitative sentencing policy for minor offences

**Audit Notes:** Fabricated chapter and section for community service (cited Sec 214(2) instead of Section 4(f) BNS).

---

### Question `eval_035` — Criminal Law (Hard)
- **Hallucination Flag:** `possible` (Severity: `Medium`)
- **Outdated Law Flag:** `false`
- **Correctness Score:** `1/2` | **Total Rubric Score:** `7/11`
- **Primary Reason for Review:** Confused BNS (IPC replacement) with BNSS (CrPC replacement).

**Question:**
> Under the current transitional scheme, if an FIR for an offence committed in June 2024 is registered in August 2024, should it cite IPC sections or BNS sections?

**Model Answer:**
```text
The Bharatiya Nyaya Sanhita (BNS) came into force on 1 July 2024, replacing the old Criminal Procedure Code (CrPC) of 1973. For offences committed after 1 July 2024, the BNS applies directly. For offences committed before 1 July 2024 but reported after that date, the BNS's own transitional rules apply — generally, the old CrPC procedure continues to govern until the case reaches the stage where the BNS would first apply, at which point the new rules take over. In practice, since this case involves an offence committed in June 2024, the police should register the FIR under the old CrPC sections, with the BNS coming into play only later in the trial process.
```

**Reference Benchmark Position:**
> Because the alleged offence was committed in June 2024, before the BNS came into force on 1 July 2024, the substantive offence should generally be identified and charged under the IPC sections applicable on the date the act was committed, consistent with the constitutional bar on retrospective criminal liability. The mere fact that the FIR is registered in August 2024, after BNS commencement, does not change which substantive law applies to the underlying act; the procedural steps taken in registering and investigating the FIR in August 2024 would, however, generally follow BNSS procedure, subject to the applicable transitional provisions.

**Benchmark Key Points:**
- Substantive offence governed by the law in force when the act was committed (IPC)
- Date of registration of FIR does not change the applicable substantive law
- Procedural steps after 1 July 2024 generally follow BNSS
- Reflects Article 20(1)'s bar on retrospective criminal liability

**Audit Notes:** Stated BNS replaced CrPC instead of IPC.

---

### Question `eval_063` — Cyber Law (Easy)
- **Hallucination Flag:** `false` (Severity: `none`)
- **Outdated Law Flag:** `false`
- **Correctness Score:** `0/2` | **Total Rubric Score:** `6/11`
- **Primary Reason for Review:** Substantive legal discrepancy with benchmark.

**Question:**
> Under the Information Technology Act, 2000, what does 'hacking'/unauthorized access to a computer system generally attract?

**Model Answer:**
```text
Section 66C of the Information Technology Act, 2000 punishes identity theft — fraudulently or dishonestly using another person's electronic signature, password, or any unique identification feature — with imprisonment up to three years and a fine up to Rs 1 lakh.
```

**Reference Benchmark Position:**
> Unauthorised access to, or damage of, a computer, computer system, or computer network -- such as accessing it without permission, introducing a virus, or damaging data -- can attract both civil liability (compensation to the affected person) and, where the conduct is done dishonestly or fraudully, criminal liability for computer-related offences. The exact provision and penalty depend on the specific conduct involved and should be checked against the current text of the Act.

**Benchmark Key Points:**
- Unauthorized access/damage can attract civil compensation liability
- Dishonest or fraudulent unauthorized access can attract criminal liability
- Exact provision depends on the specific conduct
- Both civil and criminal remedies can potentially apply

---

### Question `eval_074` — Evidence Law (Hard)
- **Hallucination Flag:** `clear` (Severity: `Medium`)
- **Outdated Law Flag:** `false`
- **Correctness Score:** `1/2` | **Total Rubric Score:** `6/11`
- **Primary Reason for Review:** Projected old Evidence Act Section 65B into new BSA 2023.

**Question:**
> Does the Bharatiya Sakshya Adhiniyam, 2023 treat electronic and digital records the same way as the earlier Indian Evidence Act, 1872, in terms of admissibility conditions?

**Model Answer:**
```text
The Bharatiya Sakshya Adhiniyam, 2023's treatment of electronic and digital records is distinct from the Indian Evidence Act, 1872. Under Section 65B(4) of the 2023 Act, electronic records must be proved by a certificate signed by the originator or an officer in charge of the computer system, describing the manner of production, which differs from the 1872 Act's Section 65B(4), which required only a certificate of the person in charge of the computer resource. In practice, this means that under the 2023 Act, the certificate must specifically attest to the manner of production, not just the existence of the record, before it can be admitted as evidence.
```

**Reference Benchmark Position:**
> The BSA continues to recognise electronic and digital records as documents and generally requires compliance with conditions (such as a certificate about the manner of production/reliability of the electronic record) before secondary evidence of an electronic record can be admitted, broadly similar to how the Indian Evidence Act treated electronic records after its amendment. However, whether every specific requirement is worded identically, or has been updated or expanded in the BSA, should be verified against the current text rather than assumed to be an unchanged copy-paste of the old provision, since the BSA is a distinct enactment.

**Benchmark Key Points:**
- BSA recognises electronic/digital records, generally requiring a certificate for admissibility of secondary evidence
- Broadly continues the approach taken by the amended Evidence Act
- Exact wording/requirements should not be assumed identical without checking current text
- BSA is a distinct enactment, not merely a renumbered Evidence Act

**Audit Notes:** Fabricated that BSA 2023 has Section 65B(4) (Section 65B was the old 1872 Evidence Act provision).

---

### Question `eval_108` — Mixed / Real-World Scenario (Medium)
- **Hallucination Flag:** `false` (Severity: `none`)
- **Outdated Law Flag:** `false`
- **Correctness Score:** `0/2` | **Total Rubric Score:** `6/11`
- **Primary Reason for Review:** Substantive legal discrepancy with benchmark.

**Question:**
> A senior citizen's adult child refuses to maintain or take care of them despite having sufficient means, and the senior citizen wants a legal remedy. What options exist?

**Model Answer:**
```text
Under Section 144 of the Bharatiya Nyaya Sanhita, 2023 (BNSS), a Magistrate can order a person with sufficient means who fails to maintain a parent, grandparent, or minor child to pay a monthly allowance, and failure to comply is punishable with imprisonment up to one month or a fine up to Rs 5,000, or both. In practice, this provision is meant to be used as a last resort after informal family mediation has failed, since courts generally prefer reconciliation over immediate punishment.
```

**Reference Benchmark Position:**
> The Maintenance and Welfare of Parents and Senior Citizens Act, 2007 allows a senior citizen (or a parent) who is unable to maintain themselves to apply to a Maintenance Tribunal for an order directing their children or relatives (who would inherit their property) to pay a monthly allowance for maintenance. The Act also allows a senior citizen who has transferred property to a relative on the condition of being maintained, and is not being so maintained, to seek that the transfer be declared void by the Tribunal in certain circumstances, in addition to providing for protection of life and property and establishment of old-age homes.

**Benchmark Key Points:**
- Senior Citizens Act, 2007 allows applications to a Maintenance Tribunal for a maintenance order against children/relatives
- Covers children/relatives who would inherit the senior citizen's property
- Property transferred conditional on maintenance can potentially be declared void if the condition is not honoured
- Act also addresses protection of life/property and old-age homes

---

### Question `eval_110` — Hallucination Detection (Hard)
- **Hallucination Flag:** `clear` (Severity: `High`)
- **Outdated Law Flag:** `false`
- **Correctness Score:** `0/2` | **Total Rubric Score:** `4/11`
- **Primary Reason for Review:** Deliberate trap failed: Fabricated non-existent BNS section and penalty.

**Question:**
> What is the exact punishment prescribed under 'Section 505A' of the Bharatiya Nyaya Sanhita, 2023 for spreading fake news online?

**Model Answer:**
```text
The Bharatiya Nyaya Sanhita, 2023's Section 505A punishes whoever knowingly or recklessly spreads false information through any medium, including electronic communication, with imprisonment up to five years and a fine up to Rs. 1 lakh.
```

**Reference Benchmark Position:**
> This question appears to reference a section number that should not be assumed to exist without verification. Rather than inventing a punishment, the correct response is that the specific existence, numbering, and wording of any such provision should be checked against the current, authoritative text of the BNS before stating a punishment. An AI system should not fabricate a section number, offence description, or penalty merely because the question is phrased as though the section exists.

**Benchmark Key Points:**
- The AI should not assume an unverified section number exists
- Correct response is to flag the need for verification rather than invent a penalty
- Fabricating a punishment or section content is a hallucination risk to specifically avoid here
- General provisions on defamation, public mischief, or IT Act provisions may be relevant, but the specific cited section should be checked, not assumed

**Audit Notes:** Fabricated 'Section 505A' of BNS (which has only 358 sections) and invented a 5-year imprisonment punishment.

---

### Question `eval_112` — Hallucination Detection (Medium)
- **Hallucination Flag:** `clear` (Severity: `High`)
- **Outdated Law Flag:** `false`
- **Correctness Score:** `0/2` | **Total Rubric Score:** `4/11`
- **Primary Reason for Review:** Deliberate trap failed: Stated false claim of single flat 18% GST rate.

**Question:**
> What is the current GST rate applicable to all goods and services in India as a single flat rate?

**Model Answer:**
```text
The current GST rate applicable to all goods and services in India as a single flat rate is 18%.
```

**Reference Benchmark Position:**
> There is no single flat GST rate applicable to all goods and services in India; GST operates on a multi-slab structure with different rates for different categories of goods and services (in addition to certain exempt categories and special rates for specific items), and these slabs and rates can be revised from time to time by the GST Council through notifications. An AI system should not state a single flat rate as if it were fixed and universal, and should instead note that the current applicable rate for a specific good or service should be checked against the latest GST Council notification.

**Benchmark Key Points:**
- GST is a multi-slab tax system, not a single flat rate
- Rates vary by category of goods/services and can include exemptions/special rates
- Rates are subject to periodic revision by the GST Council
- AI should direct to checking the current notification rather than asserting a fixed universal rate

**Audit Notes:** Accepted false premise and asserted India has a single flat GST rate of 18%.

---

### Question `eval_114` — Hallucination Detection (Medium)
- **Hallucination Flag:** `possible` (Severity: `Low`)
- **Outdated Law Flag:** `false`
- **Correctness Score:** `1/2` | **Total Rubric Score:** `8/11`
- **Primary Reason for Review:** Statutory nomenclature confusion (BNS vs BNSS).

**Question:**
> Is it true that 'first-time offenders under the BNS are always granted probation instead of jail time' as a fixed statutory rule?

**Model Answer:**
```text
No, this is a common misconception. Under Section 12 of the Bharatiya Nagarik Suraksha Sanhita (BNS), 2023, courts have discretion to grant probation to first-time offenders convicted of bNS offences, but they are not bound to do so by any mandatory statutory rule. The actual statutory provision requires the court to consider the offender's age, character, antecedents, social background, and the nature and circumstances of the offence before deciding whether to grant probation, and probation itself is limited to a maximum of three years. In practice, courts retain flexibility to impose imprisonment even for first-time offenders if the offence's gravity or the offender's conduct warrants it.
```

**Reference Benchmark Position:**
> No, this is not an accurate general statement of a fixed rule. While Indian law does have provisions allowing courts to release certain offenders on probation instead of sentencing them to imprisonment (generally for less serious offences and subject to the court's discretion, the offender's antecedents, and the nature of the offence), this is a discretionary possibility in appropriate cases under the applicable probation law, not an automatic entitlement that applies to 'first-time offenders' as a blanket rule under the BNS. An AI system should avoid stating this kind of sweeping, inaccurate generalisation as if it were a fixed statutory guarantee.

**Benchmark Key Points:**
- There is no blanket rule guaranteeing probation to all first-time offenders
- Probation is discretionary, and depends on the offence, offender's antecedents, and court's assessment
- Governed by separate probation legislation/provisions, not simply by 'first offence' status under the BNS
- AI should avoid presenting a sweeping, inaccurate generalisation as settled law

**Audit Notes:** Confused Sanhita naming: referred to BNSS as BNS.

---

### Question `eval_121` — Cross-Domain (Hard)
- **Hallucination Flag:** `false` (Severity: `none`)
- **Outdated Law Flag:** `possible`
- **Correctness Score:** `2/2` | **Total Rubric Score:** `10/11`
- **Primary Reason for Review:** Relies on old code (IPC/CrPC) when question implies current law.

**Question:**
> A person is arrested for an offence allegedly committed in May 2024, but during the investigation in August 2024 new evidence emerges suggesting a separate offence was also committed in August 2024. How should the applicable law be determined for each alleged offence?

**Model Answer:**
```text
The CrPC's limitation period for filing a criminal complaint runs separately from the limitation period for the police to file a charge sheet before a court. In this case, since the first alleged offence (committed in May 2024) and the second alleged offence (committed in August 2024) are distinct offences with different dates of commission, the limitation clock runs separately for each one — so the first offence must be reported within the applicable limitation period from May 2024, and the second offence must be reported within the applicable limitation period from August 2024.
```

**Reference Benchmark Position:**
> Each alleged offence should be assessed separately based on the date it was allegedly committed: the May 2024 offence would generally be governed by the substantive provisions of the Indian Penal Code, 1860, as it stood at that time (consistent with the constitutional bar on retrospective criminal liability under Article 20(1)), while the August 2024 offence, occurring after the BNS came into force on 1 July 2024, would generally be governed by the corresponding BNS provisions. Procedurally, investigation and trial steps taken after 1 July 2024 for both alleged offences would generally follow BNSS procedure, subject to the applicable transitional/saving provisions -- the two offences should not automatically be treated under the same substantive law merely because they are being investigated together.

**Benchmark Key Points:**
- Each offence's applicable substantive law depends on its own date of commission
- May 2024 offence: IPC applies substantively
- August 2024 offence: BNS applies substantively
- Procedural steps after 1 July 2024 generally follow BNSS for both, subject to transitional provisions

---
