# LegalAI V2 + RAG (Fixed Architecture): Human Review Required

**Total Cases Flagged:** 54 / 125 (43.2%)

This document details all responses that triggered human review thresholds (wrong domain retrieval, hallucination, temporal error, or outdated law).

---

## [eval_019] Criminal Law (Medium)

**Question:**
A theft allegedly took place on 15 June 2024, but the FIR is registered and the trial happens in 2025. Which law applies to the substantive offence, and which law applies to the procedure?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
Substantive Criminal Liability: Strictly governed by the Indian Penal Code, 1860 under Article 20(1) of the Constitution. The Bharatiya Nyaya Sanhita, 2023 CANNOT be applied retrospectively to penalize acts committed prior to July 1, 2024.

**Reference Answer:**
Because the alleged offence occurred before 1 July 2024, the substantive question of whether an offence was committed, and what punishment applies, is generally governed by the Indian Penal Code, 1860 as it stood on 15 June 2024 -- consistent with the constitutional bar on retrospective criminal liability under Article 20(1). Procedural steps taken after the BNSS came into force, such as parts of investigation, inquiry and trial conducted after 1 July 2024, are generally governed by the BNSS/BSA, subject to the transitional and saving provisions in those statutes, which should be checked for the specific procedural stage involved.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.1 ('Short title, commencement and application.') | The Bharatiya Nyaya Sanhita, 2023 s.303 ('Theft.') | The Bharatiya Nyaya Sanhita, 2023 s.305 ('Theft in a dwelling house, or means of transportation or place of worship, etc.') | The Bharatiya Nyaya Sanhita, 2023 s.112 ('Petty organised crime.') | The Bharatiya Nyaya Sanhita, 2023 s.15 ('Act of Judge when acting judicially.')

**Citations:**
["Section 1 ('Short title, commencement and application.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 303 ('Theft.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 305 ('Theft in a dwelling house, or means of transportation or place of worship, etc.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 112 ('Petty organised crime.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 15 ('Act of Judge when acting judicially.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `TEMPORALLY_UNCERTAIN`, Total Score: 5/11

---

## [eval_020] Criminal Law (Hard)

**Question:**
Is it always safe to assume that a given IPC section maps one-to-one onto a single BNS section with the same content?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
NO. Assuming a one-to-one mapping between IPC sections and BNS sections is legally unsafe. The Bharatiya Nyaya Sanhita, 2023 (BNS) is a distinct substantive penal code that replaced the Indian Penal Code, 1860 (IPC) on 1 July 2024. While many concepts and offences retain continuity, the specific sections, definitions, and penalties differ significantly. For example, Section 237 BNS (Using as true such declaration knowing it to be false) corresponds roughly to Section 193 IPC (Giving false evidence or fabricating documents for giving false evidence), but the exact scope, punishment, and procedural safeguards are distinct.

**Reference Answer:**
No. While many BNS provisions closely track their IPC counterparts with renumbering, the mapping is not uniformly one-to-one: some offences have been reworded, some punishments have been changed (for example, community service was introduced as a form of punishment for certain minor offences), some provisions have been consolidated or split, and some new offences (such as certain organised crime and terrorism provisions, or specific aggravated offences) do not have a direct IPC equivalent. Any specific IPC-to-BNS mapping should be verified against the current statutory text rather than assumed.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.2 ('Definitions.') | The Bharatiya Nyaya Sanhita, 2023 s.339 ('Having possession of document described in section 337 or section 338, knowing it to be') | The Bharatiya Nyaya Sanhita, 2023 s.237 ('Using as true such declaration knowing it to be false.') | The Bharatiya Nyaya Sanhita, 2023 s.235 ('Using as true a certificate known to be false.') | The Bharatiya Nyaya Sanhita, 2023 s.204 ('Personating a public servant.')

**Citations:**
["Section 2 ('Definitions.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 339 ('Having possession of document described in section 337 or section 338, knowing it to be'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 237 ('Using as true such declaration knowing it to be false.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 235 ('Using as true a certificate known to be false.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 204 ('Personating a public servant.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_022] Criminal Law (Medium)

**Question:**
What is the difference between a cognizable and a non-cognizable offence?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
Under Section 2(22) of the Bharatiya Nagarik Suraksha Sanhita, 2023, a 'cognizable offence' is defined as an offence for which, and a 'cognizable case' as a case in which, a police officer may, in accordance with the First Schedule or under any other law for the time being in force, arrest without warrant. Conversely, a 'non-cognizable offence' is defined as an offence for which, and a 'non-cognizable case' as a case in which, a police officer has no authority to arrest without warrant.

**Reference Answer:**
In a cognizable offence, the police can register an FIR and start investigation, and can arrest the accused without a warrant and without prior permission of a magistrate. In a non-cognizable offence, the police cannot investigate or arrest without a warrant unless a magistrate authorises it; the complainant generally has to approach a magistrate directly to set the process in motion.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.400 ('Order to pay costs in non-cognizable cases.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.174 ('Information as to non-cognizable cases and investigation of such cases.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.221 ('Cognizance of offence.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.40 ('Arrest by private person and procedure on such arrest.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.2 ('Definitions.')

**Citations:**
["Section 400 ('Order to pay costs in non-cognizable cases.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 174 ('Information as to non-cognizable cases and investigation of such cases.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 221 ('Cognizance of offence.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 40 ('Arrest by private person and procedure on such arrest.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 2 ('Definitions.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_023] Criminal Law (Easy)

**Question:**
Can a person simply ignore a summons issued by a criminal court because they believe the case against them is false?

**Model Answer (Fixed V2 + RAG):**
### Legal Response:
NO. Ignoring a summons issued by a criminal court carries serious legal consequences. Under Section 207 of the Bharatiya Nagarik Suraksha Sanhita, 2023, a Magistrate has the power to issue a summons or warrant for an offence committed beyond local jurisdiction, compelling the accused to appear before the court. Failure to respond to a valid summons constitutes contempt of court under Section 193 of the Bharatiya Nyaya Sanhita, 2023, punishable with imprisonment up to six months and/or a fine. In practice, courts treat non-appearance as an aggravating factor during sentencing.

**Reference Answer:**
No. A person who has been validly summoned by a court must appear or otherwise respond through the legal process (such as through a lawyer, or by applying for exemption from personal appearance where permitted); simply ignoring a summons can lead to further coercive process, such as a bailable or non-bailable warrant, or proceedings for non-appearance. If the person believes the case is false or an abuse of process, the correct remedy is to defend the case through the court process, including remedies like a petition for quashing where genuinely available -- not to ignore the summons.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.207 ('Power to issue summons or warrant for offence committed beyond local jurisdiction.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.273 ('Compensation for accusation without reasonable cause.') | The Bharatiya Sakshya Adhiniyam, 2023 s.137 ('Witness not excused from answering on ground that answer will criminate.') | The Bharatiya Nyaya Sanhita, 2023 s.240 ('Giving false information respecting an offence committed.') | The Bharatiya Sakshya Adhiniyam, 2023 s.19 ('Proof of admissions against persons making them, and by or on their behalf.')

**Citations:**
["Section 207 ('Power to issue summons or warrant for offence committed beyond local jurisdiction.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 273 ('Compensation for accusation without reasonable cause.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 137 ('Witness not excused from answering on ground that answer will criminate.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 240 ('Giving false information respecting an offence committed.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 19 ('Proof of admissions against persons making them, and by or on their behalf.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_025] Criminal Law (Medium)

**Question:**
What is an FIR and can it be registered at any police station regardless of where the offence occurred?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
**Statutory Grounding:** The Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) governs the procedural aspects of criminal investigations, including the registration of First Information Reports (FIRs).

**Reference Answer:**
An FIR (First Information Report) is the document recorded by police on receiving information about the commission of a cognizable offence, and it sets the criminal investigation process in motion. Under the 'Zero FIR' concept, a person can lodge an FIR at any police station regardless of where the offence occurred; that police station is required to register the Zero FIR and then transfer it to the police station having territorial jurisdiction for further investigation.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.186 ('When officer in charge of police station may require another to issue search-warrant.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.208 ('Offence committed outside India.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.173 ('Information in cognizable cases.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.48 ('Obligation of person making arrest to inform about arrest, etc., to relative or friend.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.176 ('Procedure for investigation.')

**Citations:**
["Section 186 ('When officer in charge of police station may require another to issue search-warrant.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 208 ('Offence committed outside India.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 173 ('Information in cognizable cases.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 48 ('Obligation of person making arrest to inform about arrest, etc., to relative or friend.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 176 ('Procedure for investigation.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_026] Criminal Law (Medium)

**Question:**
What is anticipatory bail, and under what circumstances is it typically sought?

**Model Answer (Fixed V2 + RAG):**
### Legal Response:
Under Section 482 of the Bharatiya Nagarik Suraksha Sanhita, 2023, anticipatory bail is granted to a person apprehending arrest on an accusation of a non-bailable offence, allowing conditional release on bail in the event of actual arrest.

**Reference Answer:**
Anticipatory bail is bail sought in advance, before arrest, by a person who has reason to believe they may be arrested on an accusation of having committed a non-bailable offence. If granted, the court directs that in the event of arrest, the person shall be released on bail on specified conditions. Courts consider factors such as the nature of the accusation, the applicant's antecedents, the possibility of the applicant fleeing, and whether the accusation appears to be made to injure or humiliate the applicant.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.482 ('Direction for grant of bail to person apprehending arrest.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.478 ('In what cases bail to be taken.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.483 ('Special powers of High Court or Court of Session regarding bail.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.83 ('Procedure by Magistrate before whom such person arrested is brought.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.60 ('Discharge of person apprehended.')

**Citations:**
["Section 482 ('Direction for grant of bail to person apprehending arrest.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 478 ('In what cases bail to be taken.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 483 ('Special powers of High Court or Court of Session regarding bail.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 83 ('Procedure by Magistrate before whom such person arrested is brought.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 60 ('Discharge of person apprehended.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_027] Criminal Law (Hard)

**Question:**
What is the significance of the transitional/saving provisions in the BNSS for criminal cases that were already pending on 1 July 2024?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
Section 531(2)(a) of the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) provides that any appeal, application, trial, inquiry, or investigation pending immediately before the BNSS came into force on 1 July 2024 shall continue to be disposed of, continued, held, or made in accordance with the provisions of the Code of Criminal Procedure, 1973 (CrPC) as if the BNSS had not come into force.

**Reference Answer:**
The BNSS contains saving/transitional provisions designed to ensure that cases and proceedings already pending immediately before 1 July 2024 are not automatically disrupted by the change in procedural law. As a general principle, procedural steps already validly taken under the CrPC are generally saved, and pending proceedings continue in accordance with the CrPC unless the transitional provisions specifically direct otherwise; the exact treatment of a specific pending stage (such as an ongoing trial, an appeal, or an application) should be verified against the actual text of the relevant saving clause rather than assumed.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.5 ('Saving.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.531 ('Repeal and savings.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.298 ('Savings.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.2 ('Definitions.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.469 ('Saving.')

**Citations:**
["Section 5 ('Saving.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 531 ('Repeal and savings.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 298 ('Savings.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 2 ('Definitions.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 469 ('Saving.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_028] Criminal Law (Easy)

**Question:**
What is the general punishment structure for a simple (first) theft conviction under Indian criminal law?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
Under Section 303 of the Bharatiya Nyaya Sanhita, 2023, a first-time offender convicted of simple theft faces imprisonment of either description for up to three years, a fine, or both. In practice, this means the court can impose a sentence anywhere within that range, depending on the facts of the case and the accused's criminal record.

**Reference Answer:**
Theft is a criminal offence involving the dishonest taking of movable property out of the possession of another person without consent. Under the applicable criminal law (IPC for offences before 1 July 2024, BNS for offences on or after that date), a first conviction for simple theft is punishable with imprisonment of either description for a term that can extend up to a specified number of years, or with fine, or with both -- the exact maximum term and whether it is bailable/cognizable should be checked against the specific section in force for the date of the offence, since the punishment structure between IPC and BNS is not necessarily identical.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.303 ('Theft.') | The Bharatiya Nyaya Sanhita, 2023 s.112 ('Petty organised crime.') | The Bharatiya Nyaya Sanhita, 2023 s.307 ('Theft after preparation made for causing death, hurt or restraint in order to committing') | The Bharatiya Nyaya Sanhita, 2023 s.134 ('Assault or criminal force in attempt to commit theft of property carried by a person.') | The Bharatiya Nyaya Sanhita, 2023 s.313 ('Punishment for belonging to gang of robbers, etc.')

**Citations:**
["Section 303 ('Theft.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 112 ('Petty organised crime.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 307 ('Theft after preparation made for causing death, hurt or restraint in order to committing'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 134 ('Assault or criminal force in attempt to commit theft of property carried by a person.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 313 ('Punishment for belonging to gang of robbers, etc.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_030] Criminal Law (Hard)

**Question:**
A shopkeeper uses force against a person who is in the process of committing robbery on the shop premises. What legal principle allows this, and what are its limits?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
The shopkeeper's use of force against a person committing robbery on the shop premises is governed by Section 309 of the Bharatiya Nyaya Sanhita, 2023 (BNS). Section 309 defines robbery as theft accompanied by voluntary causing of death, hurt, wrongful restraint, or fear of instant death, hurt, or wrongful restraint. Force used by the shopkeeper to prevent the robbery falls squarely within this definition, since the force is used to prevent the theft itself.

**Reference Answer:**
This is a question of the right of private defence, which allows a person to use reasonable force to protect themselves or their property against an ongoing unlawful attack such as robbery. The right is not unlimited: the force used must be proportionate to the threat, must be used only while the danger is ongoing (not after the threat has ended), and must not exceed what is necessary to avert the danger. Whether the force used in a given case was within these limits is a question of fact, and the exact statutory provision defining private defence and its limits depends on whether the incident occurred before or after 1 July 2024 (IPC vs BNS), which should be verified against the applicable text.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.309 ('Robbery.') | The Bharatiya Nyaya Sanhita, 2023 s.311 ('Robbery, or dacoity, with attempt to cause death or grievous hurt.') | The Bharatiya Nyaya Sanhita, 2023 s.189 ('Unlawful assembly.') | The Bharatiya Nyaya Sanhita, 2023 s.134 ('Assault or criminal force in attempt to commit theft of property carried by a person.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.249 ('Opening case for prosecution.')

**Citations:**
["Section 309 ('Robbery.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 311 ('Robbery, or dacoity, with attempt to cause death or grievous hurt.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 189 ('Unlawful assembly.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 134 ('Assault or criminal force in attempt to commit theft of property carried by a person.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 249 ('Opening case for prosecution.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_031] Criminal Law (Medium)

**Question:**
What is the general rule about when a chargesheet must be filed after arrest, and what happens if it is not filed in time?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
The general rule under Section 251 of the Bharatiya Nagarik Suraksha Sanhita, 2023 is that once a case is committed to the Sessions Court, the Judge must frame a charge against the accused within 60 days from the date of the first hearing on charge. If the charge is not framed within this period, the accused can move the court for an order of discharge under Section 251(3).

**Reference Answer:**
Criminal procedure law prescribes a maximum period within which the investigation must be completed and a chargesheet (final report) filed, which varies depending on the severity of the offence (for example, offences punishable with death, life imprisonment, or a longer minimum sentence typically get a longer period than offences with a lower maximum sentence). If the chargesheet is not filed within the prescribed period and the accused has been in custody, the accused becomes entitled to apply for 'default' or 'statutory' bail, and the court is generally required to grant it if the conditions are met, regardless of the merits of the case.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.478 ('In what cases bail to be taken.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.236 ('When manner of committing offence must be stated.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.290 ('Application for plea bargaining.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.251 ('Framing of charge.')

**Citations:**
["Section 478 ('In what cases bail to be taken.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 236 ('When manner of committing offence must be stated.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 290 ('Application for plea bargaining.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 251 ('Framing of charge.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_032] Criminal Law (Medium)

**Question:**
What is a plea bargain, and is it available for all criminal offences in India?

**Model Answer (Fixed V2 + RAG):**
### Legal Response:
A plea bargain is a negotiated agreement between the accused and the prosecution, facilitated by the court, under Section 290 of the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS). It is available for offences punishable with imprisonment up to seven years, excluding offences affecting women, children, or public servants.

**Reference Answer:**
Plea bargaining allows an accused to voluntarily apply to the court for a negotiated disposition of the case, typically in exchange for a lesser sentence, without a full trial on the merits. It is not available for all offences: it is generally restricted to offences that do not carry the death penalty, life imprisonment, or a sentence exceeding a specified threshold, and it is generally not available for offences affecting the socio-economic condition of the country or offences committed against a woman or a child below a specified age -- the exact eligibility conditions should be checked against the current statutory text.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.296 ('Power of Court in plea bargaining.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.290 ('Application for plea bargaining.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.299 ('Statements of accused not to be used.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.298 ('Savings.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.252 ('Conviction on plea of guilty.')

**Citations:**
["Section 296 ('Power of Court in plea bargaining.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 290 ('Application for plea bargaining.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 299 ('Statements of accused not to be used.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 298 ('Savings.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 252 ('Conviction on plea of guilty.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_036] Criminal Law (Medium)

**Question:**
What is 'discharge' in a criminal case, and how is it different from acquittal?

**Model Answer (Fixed V2 + RAG):**
### Legal Response:
#### Explanation of 'Discharge' and 'Acquittal':
1. **Discharge**: Under Section 250 BNSS, 2023, the accused may apply for discharge within 60 days of commitment, and the Sessions Judge discharges if there is insufficient ground to proceed. This is distinct from acquittal, which follows conviction or acquittal findings under Section 278 BNSS, 2023.

**Reference Answer:**
Discharge occurs at a preliminary stage, before the trial properly begins, when the court examines the material on record and concludes there is no sufficient ground to proceed against the accused, so the accused is discharged without a full trial. Acquittal, by contrast, happens at the conclusion of a trial (after evidence has been led and arguments heard), where the court finds that the prosecution has not proved the charge beyond reasonable doubt. Discharge is a pre-trial screening mechanism, while acquittal is a post-trial finding on the merits.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.337 ('Person once convicted or acquitted not to be tried for same offence.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.278 ('Acquittal or conviction.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.334 ('Previous conviction or acquittal how proved.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.419 ('Appeal in case of acquittal.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.250 ('Discharge.')

**Citations:**
["Section 337 ('Person once convicted or acquitted not to be tried for same offence.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 278 ('Acquittal or conviction.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 334 ('Previous conviction or acquittal how proved.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 419 ('Appeal in case of acquittal.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 250 ('Discharge.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_038] Contract Law (Easy)

**Question:**
Is an oral agreement legally valid as a contract in India?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
An oral agreement is not legally valid as a contract in India. Under Section 95 of the Bharatiya Sakshya Adhiniyam, 2023, once the terms of a contract, grant, or disposition of property have been reduced to writing, oral evidence cannot contradict, vary, add to, or subtract from those written terms, except where the document is invalid or where a separate oral agreement exists that is not inconsistent with the written terms.

**Reference Answer:**
Yes. Under the Indian Contract Act, a contract does not need to be in writing or registered to be valid, unless a specific law requires a particular form (such as certain property transactions requiring a registered instrument). An oral agreement satisfying the essential elements of a contract -- offer, acceptance, consideration, capacity, and free consent -- is generally enforceable, though proving its exact terms can be harder than with a written contract.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.95 ('Exclusion of evidence of oral agreement.') | The Bharatiya Sakshya Adhiniyam, 2023 s.102 ('Who may give evidence of agreement varying terms of document.') | The Bharatiya Sakshya Adhiniyam, 2023 s.94 ('Evidence of terms of contracts, grants and other dispositions of property reduced to form of') | The Bharatiya Sakshya Adhiniyam, 2023 s.85 ('Presumption as to electronic agreements.') | The Bharatiya Sakshya Adhiniyam, 2023 s.147 ('Evidence as to matters in writing.')

**Citations:**
["Section 95 ('Exclusion of evidence of oral agreement.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 102 ('Who may give evidence of agreement varying terms of document.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 94 ('Evidence of terms of contracts, grants and other dispositions of property reduced to form of'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 85 ('Presumption as to electronic agreements.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 147 ('Evidence as to matters in writing.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_042] Contract Law (Medium)

**Question:**
What remedies are available to a party when the other party commits a breach of contract?

**Model Answer (Fixed V2 + RAG):**
### Legal Response:
Under Section 357 of the Bharatiya Nyaya Sanhita, 2023, whoever, being bound by a lawful contract to attend on or to supply the wants of any person who, by reason of youth, or of unsoundness of mind, or of a disease or bodily weakness, is helpless or incapable of providing for his own safety or of supplying his own wants, voluntarily omits so to do, shall be punished with imprisonment of either description for a term which may extend to three months, or with fine which may extend to five thousand rupees, or with both.

**Reference Answer:**
Depending on the nature of the breach and the contract, remedies can include damages (compensation for loss caused by the breach), specific performance (a court order compelling the breaching party to actually perform the contract, available in limited circumstances under the Specific Relief Act), injunction (restraining the breaching party from doing something inconsistent with the contract), and rescission (treating the contract as terminated). The appropriate remedy depends on facts such as whether damages would be an adequate remedy and the nature of the obligation breached.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.357 ('Breach of contract to attend on and supply wants of helpless person.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.359 ('Compounding of offences.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.164 ('Procedure where dispute concerning land or water is likely to cause breach of') | The Bharatiya Nyaya Sanhita, 2023 s.316 ('Criminal breach of trust.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.244 ('Where it is doubtful what offence has been committed.')

**Citations:**
["Section 357 ('Breach of contract to attend on and supply wants of helpless person.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 359 ('Compounding of offences.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 164 ('Procedure where dispute concerning land or water is likely to cause breach of'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 316 ('Criminal breach of trust.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 244 ('Where it is doubtful what offence has been committed.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_045] Contract Law (Hard)

**Question:**
A contract contains a clause completely restraining one party from carrying on any lawful profession or business after the contract ends. Is such a clause enforceable?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
Section 27 of the Indian Contract Act, 1872 prohibits a restraint on trade that is unreasonable or extends beyond the legitimate protection of the party's interest.

**Reference Answer:**
Generally, no. Section 27 of the Indian Contract Act declares that every agreement by which anyone is restrained from exercising a lawful profession, trade, or business is void to that extent, subject to the limited statutory exception for the sale of goodwill. Courts have carved out narrow judicial exceptions in some situations (such as certain reasonable restrictions operating during the subsistence of employment, as opposed to after it), but a blanket post-contractual restraint of this kind is generally not enforceable, and the specific facts and drafting would need to be checked.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.94 ('Evidence of terms of contracts, grants and other dispositions of property reduced to form of') | The Bharatiya Nyaya Sanhita, 2023 s.357 ('Breach of contract to attend on and supply wants of helpless person.') | The Bharatiya Sakshya Adhiniyam, 2023 s.95 ('Exclusion of evidence of oral agreement.') | The Bharatiya Nyaya Sanhita, 2023 s.219 ('Obstructing sale of property offered for sale by authority of public servant.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.293 ('Disposal of case.')

**Citations:**
["Section 94 ('Evidence of terms of contracts, grants and other dispositions of property reduced to form of'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 357 ('Breach of contract to attend on and supply wants of helpless person.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 95 ('Exclusion of evidence of oral agreement.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 219 ('Obstructing sale of property offered for sale by authority of public servant.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 293 ('Disposal of case.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_047] Property Law (Easy)

**Question:**
Is registration compulsory for a sale deed transferring immovable property worth more than a certain value?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
NO. Registration is not compulsory for a sale deed transferring immovable property worth more than a certain value. Under the Transfer of Property Act, 1882, a sale deed is valid without registration, though unregistered instruments are not admissible in evidence under Section 49.

**Reference Answer:**
Yes. Under the Registration Act, 1908, a document that purports to transfer or create an interest in immovable property of a value exceeding a specified threshold (currently one hundred rupees, which in practice covers nearly all real property sales) generally requires compulsory registration. An unregistered document required to be registered generally cannot be used as evidence of the transaction affecting the immovable property, though it may sometimes be relevant for a collateral purpose.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.505 ('Power to sell perishable property.') | The Bharatiya Nyaya Sanhita, 2023 s.322 ('Dishonest or fraudulent execution of deed of transfer containing false statement of') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.122 ('Certain transfers to be null and void.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.85 ('Attachment of property of person absconding.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.117 ('Seizure or attachment of property.')

**Citations:**
["Section 505 ('Power to sell perishable property.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 322 ('Dishonest or fraudulent execution of deed of transfer containing false statement of'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 122 ('Certain transfers to be null and void.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 85 ('Attachment of property of person absconding.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 117 ('Seizure or attachment of property.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_050] Property Law (Hard)

**Question:**
A person buys a property from someone who is not its true owner, without knowledge of the defect in title, and pays fair value. Can such a buyer claim any protection?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
Under Section 314 of the Bharatiya Nyaya Sanhita, 2023, dishonest misappropriation of property is punishable with imprisonment of either description for a term which shall not be less than six months but which may extend to two years, along with a fine. In your scenario, where a person buys property from someone who is not its true owner, without knowledge of the defect in title, and pays fair value, the doctrine of estoppel under Section 121 of the Bharatiya Sakshya Adhiniyam, 2023 provides limited protection: if the seller intentionally caused the buyer to believe the seller had a valid title, the seller cannot later deny that representation in court. However, this does not automatically confer ownership; the buyer retains the option to seek compensation for the defective title rather than possession.

**Reference Answer:**
This raises the doctrine of a bona fide purchaser for value without notice. In general, a transferee who purchases in good faith, for consideration, and without notice (actual or constructive) of a defect in the transferor's title may, in certain circumstances recognised under the Transfer of Property Act (such as the doctrine of ostensible ownership), be protected against the true owner's claim -- but this protection is not absolute, depends on satisfying each of the good-faith, consideration, and no-notice elements, and the true owner's remedies (if any) against the fraudulent transferor remain separate. Whether protection applies in a specific case depends heavily on the facts, including what due diligence the buyer undertook.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.314 ('Dishonest misappropriation of property.') | The Bharatiya Sakshya Adhiniyam, 2023 s.121 ('Estoppel.') | The Bharatiya Nyaya Sanhita, 2023 s.318 ('Cheating.') | The Bharatiya Sakshya Adhiniyam, 2023 s.122 ('Estoppel of tenant and of licensee of person in possession.') | The Bharatiya Sakshya Adhiniyam, 2023 s.135 ('Production of title-deeds of witness not a party.')

**Citations:**
["Section 314 ('Dishonest misappropriation of property.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 121 ('Estoppel.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 318 ('Cheating.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 122 ('Estoppel of tenant and of licensee of person in possession.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 135 ('Production of title-deeds of witness not a party.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_051] Property Law (Medium)

**Question:**
What are the essential requirements for a valid gift of immovable property under Indian law?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
Under Section 502 of the Bharatiya Nagarik Suraksha Sanhita, 2023, a court may order the restoration of possession of immovable property to a person who was dispossessed by criminal force or intimidation, provided the order is made within one month of conviction.

**Reference Answer:**
A valid gift of immovable property requires that it be made voluntarily, without consideration, by a person competent to contract, that it be accepted by or on behalf of the donee during the lifetime of the donor while the donor is still capable of giving, and -- critically -- that the transfer be effected by a registered instrument signed by or on behalf of the donor and attested by at least two witnesses. Without registration, a purported gift of immovable property is generally not valid, regardless of intention.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.502 ('Power to restore possession of immovable property.') | The Bharatiya Nyaya Sanhita, 2023 s.251 ('Offering gift or restoration of property in consideration of screening offender.') | The Bharatiya Nyaya Sanhita, 2023 s.252 ('Taking gift to help to recover stolen property, etc.') | The Bharatiya Sakshya Adhiniyam, 2023 s.122 ('Estoppel of tenant and of licensee of person in possession.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.85 ('Attachment of property of person absconding.')

**Citations:**
["Section 502 ('Power to restore possession of immovable property.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 251 ('Offering gift or restoration of property in consideration of screening offender.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 252 ('Taking gift to help to recover stolen property, etc.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 122 ('Estoppel of tenant and of licensee of person in possession.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 85 ('Attachment of property of person absconding.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_053] Property Law (Hard)

**Question:**
Landlord and tenant have a written lease that does not specify a notice period for termination. What notice period generally applies by default under Indian law, and does it depend on the type of tenancy?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
The default notice period for terminating a lease depends on the type of tenancy. For a month-to-month tenancy, the standard notice period is generally 15 days, though this can vary depending on local rent-control legislation. In practice, the notice period is calculated from the date the notice is actually delivered, not just posted.

**Reference Answer:**
In the absence of an express contract or local usage specifying otherwise, the Transfer of Property Act prescribes default notice periods that vary by the purpose of the lease: a lease of immovable property for agricultural or manufacturing purposes is terminable, in the absence of a contrary contract or usage, by six months' notice, while a lease for any other purpose (such as a residential or general commercial lease) is terminable by fifteen days' notice, expiring with the end of a month of the tenancy. State-specific Rent Control legislation, where applicable, can override or modify these default rules, so the applicable state rent law should also be checked.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.122 ('Estoppel of tenant and of licensee of person in possession.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.141 ('Imprisonment in default of security.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.119 ('Notice of forfeiture of property.') | The Bharatiya Sakshya Adhiniyam, 2023 s.112 ('Burden of proof as to relationship in the cases of partners, landlord and tenant, principal') | The Bharatiya Nyaya Sanhita, 2023 s.211 ('Omission to give notice or information to public servant by person legally bound to give')

**Citations:**
["Section 122 ('Estoppel of tenant and of licensee of person in possession.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 141 ('Imprisonment in default of security.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 119 ('Notice of forfeiture of property.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 112 ('Burden of proof as to relationship in the cases of partners, landlord and tenant, principal'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 211 ('Omission to give notice or information to public servant by person legally bound to give'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_054] Property Law (Medium)

**Question:**
Does merely paying property tax or municipal charges on a piece of land establish ownership of that land?

**Model Answer (Fixed V2 + RAG):**
No. Paying property tax or municipal charges on a piece of land does not establish ownership of that land. Ownership is established by registered sale deed, gift deed, or other transfer documents under the Transfer of Property Act, 1882, not by payment of municipal dues.

**Reference Answer:**
No. Paying property tax, municipal charges, or similar dues is not, by itself, proof of ownership -- it may be evidence of possession or of an assertion of interest, but ownership is established through valid title documents (such as a registered sale deed, gift deed, or succession) and the chain of title, not merely by who pays municipal dues. In a title dispute, tax receipts are at best corroborative evidence, not conclusive proof of ownership.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.111 ('Definitions.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.463 ('Warrant for levy of fine issued by a Court in any territory to which this Sanhita does not') | The Bharatiya Nyaya Sanhita, 2023 s.193 ('Liability of owner, occupier, etc., of land on which an unlawful assembly or riot takes') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.166 ('Dispute concerning right of use of land or water.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.164 ('Procedure where dispute concerning land or water is likely to cause breach of')

**Citations:**
["Section 111 ('Definitions.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 463 ('Warrant for levy of fine issued by a Court in any territory to which this Sanhita does not'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 193 ('Liability of owner, occupier, etc., of land on which an unlawful assembly or riot takes'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 166 ('Dispute concerning right of use of land or water.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 164 ('Procedure where dispute concerning land or water is likely to cause breach of'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_065] Cyber Law (Medium)

**Question:**
What practical steps should someone take if they discover a fake social media profile impersonating them?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
The Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) governs procedural matters in criminal investigations and trials, including the identification of unlawfully acquired property (Section 116) and the identification of arrested persons (Section 54). The Bharatiya Nyaya Sanhita, 2023 (BNS) defines substantive offences, including dishonest misappropriation of property (Section 314) and theft accompanied by preparation to cause death, hurt, or restraint (Section 307).

**Reference Answer:**
Practical steps include preserving evidence (screenshots of the fake profile, its posts, messages sent from it, and the profile URL), reporting the profile directly to the platform for takedown under its impersonation policy, and filing a complaint with the police cybercrime unit or through the National Cyber Crime Reporting Portal, especially if the impersonation is being used to cheat, harass, or defame. Legal remedies can include both criminal complaints (depending on the facts, potentially under IT Act and/or BNS provisions) and civil remedies for defamation or privacy violation.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.116 ('Identifying unlawfully acquired property.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.54 ('Identification of person arrested.') | The Bharatiya Nyaya Sanhita, 2023 s.314 ('Dishonest misappropriation of property.') | The Bharatiya Nyaya Sanhita, 2023 s.307 ('Theft after preparation made for causing death, hurt or restraint in order to committing')

**Citations:**
["Section 116 ('Identifying unlawfully acquired property.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 54 ('Identification of person arrested.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 314 ('Dishonest misappropriation of property.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 307 ('Theft after preparation made for causing death, hurt or restraint in order to committing'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_066] Cyber Law (Hard)

**Question:**
A person receives a phishing email that leads to unauthorized withdrawal of money from their bank account. What legal avenues are available, and what should they do immediately?

**Model Answer (Fixed V2 + RAG):**
### Legal Response:
This situation involves a cybercrime under the Bharatiya Nyaya Sanhita, 2023 (BNS). The offence of cheating by personation using a computer resource is punishable under Section 66D BNS, 2023, carrying imprisonment up to three years and a fine up to Rs. 1 lakh. In practice, the victim should file a complaint with the Cyber Crime Cell of the local police, preserve digital evidence, and seek a forensic report from a certified examiner.

**Reference Answer:**
Immediate practical steps include informing the bank at once to block the account/card and initiate a dispute for the fraudulent transaction (RBI's limited/zero liability framework for customers can apply if reported promptly), preserving the phishing email and transaction records, and filing a complaint with the police cybercrime unit or via the National Cyber Crime Reporting Portal. Legally, this can potentially attract offences under the IT Act (such as provisions dealing with computer-related fraud/cheating by personation) as well as relevant provisions of the BNS relating to cheating, depending on the exact facts; the applicable sections should be verified against the specific conduct rather than assumed.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.316 ('Criminal breach of trust.') | The Bharatiya Nyaya Sanhita, 2023 s.187 ('Person employed in mint causing coin to be of different weight or composition from that') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.116 ('Identifying unlawfully acquired property.') | The Bharatiya Sakshya Adhiniyam, 2023 s.39 ('Opinions of experts.') | The Bharatiya Nyaya Sanhita, 2023 s.2 ('Definitions.')

**Citations:**
["Section 316 ('Criminal breach of trust.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 187 ('Person employed in mint causing coin to be of different weight or composition from that'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 116 ('Identifying unlawfully acquired property.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 39 ('Opinions of experts.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 2 ('Definitions.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_068] Cyber Law (Easy)

**Question:**
Is sending a threatening or obscene message to someone through WhatsApp a punishable offence in India?

**Model Answer (Fixed V2 + RAG):**
Yes, sending a threatening or obscene message through WhatsApp is a punishable offence under Sections 308 (extortion), 296 (obscene acts and songs), and 351 (criminal intimidation) of the Bharatiya Nyaya Sanhita, 2023.

**Reference Answer:**
Potentially yes, depending on the exact content and intent -- such conduct can attract offences under the Information Technology Act (for example, provisions dealing with transmission of obscene material in electronic form) and/or provisions of the BNS relating to criminal intimidation, insult, or obscenity, depending on the specific message and its effect. The specific applicable section depends on the facts and should not be assumed without checking the current statutory text.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.308 ('Extortion.') | The Bharatiya Nyaya Sanhita, 2023 s.296 ('Obscene acts and songs.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.202 ('Offences committed by means of electronic communications, letters, etc.') | The Bharatiya Nyaya Sanhita, 2023 s.294 ('Sale, etc., of obscene books, etc.') | The Bharatiya Nyaya Sanhita, 2023 s.351 ('Criminal intimidation.')

**Citations:**
["Section 308 ('Extortion.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 296 ('Obscene acts and songs.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 202 ('Offences committed by means of electronic communications, letters, etc.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 294 ('Sale, etc., of obscene books, etc.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 351 ('Criminal intimidation.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_071] Evidence Law (Easy)

**Question:**
What is the difference between primary and secondary evidence of a document?

**Model Answer (Fixed V2 + RAG):**
Under Section 57 of the Bharatiya Sakshya Adhiniyam, 2023, primary evidence means the document itself produced for the inspection of the Court. Where a document is executed in several parts, each part is primary evidence of the document. Where a document is executed in counterpart, each counterpart is primary evidence as against the parties executing it. Where a number of documents are all made by one uniform process, as in the case of printing, lithography, or photography, each is primary evidence of the contents of the rest; but where they are all copies of a common original, they are not primary evidence of the contents of the original. Where an electronic or digital record is created or stored, and such storage occurs simultaneously or sequentially in multiple files, each such file is primary evidence. Where an electronic or digital record is produced from proper custody, such electronic and digital record is primary evidence unless it is disputed. Where a video recording is simultaneously stored in electronic form and transmitted or broadcast or transferred to another, each of the stored recordings is primary evidence. Where an electronic or digital record is stored in multiple storage spaces in a computer resource, each such automated storage, including temporary files, is primary evidence.

**Reference Answer:**
Primary evidence is the document itself produced for the inspection of the court -- the original. Secondary evidence includes certified copies, copies made from the original by mechanical processes, copies compared with the original, counterparts, and oral accounts of the contents given by someone who has seen the original. As a general rule, a document must be proved by primary evidence except in specified circumstances (such as the original being lost, destroyed, or in the opposing party's possession and not produced despite notice), where secondary evidence becomes admissible.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.56 ('Proof of contents of documents.') | The Bharatiya Sakshya Adhiniyam, 2023 s.60 ('Cases in which secondary evidence relating to documents may be given.') | The Bharatiya Sakshya Adhiniyam, 2023 s.58 ('Secondary evidence.') | The Bharatiya Sakshya Adhiniyam, 2023 s.59 ('Proof of documents by primary evidence.') | The Bharatiya Sakshya Adhiniyam, 2023 s.57 ('Primary evidence.')

**Citations:**
["Section 56 ('Proof of contents of documents.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 60 ('Cases in which secondary evidence relating to documents may be given.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 58 ('Secondary evidence.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 59 ('Proof of documents by primary evidence.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 57 ('Primary evidence.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_073] Evidence Law (Medium)

**Question:**
What is a 'dying declaration' and what is its evidentiary value?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
A 'dying declaration' is a statement made by a person who believes they are about to die, describing the cause of their death or the circumstances leading to it. Under Section 107 of the Bharatiya Sakshya Adhiniyam, 2023, the burden of proving the declarant's death lies on the party wishing to admit the declaration as evidence.

**Reference Answer:**
A dying declaration is a statement made by a person as to the cause of their death or the circumstances of the transaction resulting in their death, made when the person is in a position to know the facts. Such statements are treated as a recognised exception to the general rule against hearsay and can be admitted in evidence; if the court is satisfied the declaration is true and voluntary, a conviction can be based on it even without independent corroboration, though courts generally examine such statements with care given that the maker cannot be cross-examined.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.107 ('Burden of proving fact to be proved to make evidence admissible.') | The Bharatiya Nyaya Sanhita, 2023 s.237 ('Using as true such declaration knowing it to be false.') | The Bharatiya Nyaya Sanhita, 2023 s.170 ('Bribery.')

**Citations:**
["Section 107 ('Burden of proving fact to be proved to make evidence admissible.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 237 ('Using as true such declaration knowing it to be false.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 170 ('Bribery.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_074] Evidence Law (Hard)

**Question:**
Does the Bharatiya Sakshya Adhiniyam, 2023 treat electronic and digital records the same way as the earlier Indian Evidence Act, 1872, in terms of admissibility conditions?

**Model Answer (Fixed V2 + RAG):**
Statutory Citation Warning: The generated answer referenced unverified or non-existent provisions: Section 65B of BSA (non-existent provision; BSA equivalent is Section 63). In accordance with strict legal fidelity rules, this citation cannot be validated from authoritative sources.

**Reference Answer:**
The BSA continues to recognise electronic and digital records as documents and generally requires compliance with conditions (such as a certificate about the manner of production/reliability of the electronic record) before secondary evidence of an electronic record can be admitted, broadly similar to how the Indian Evidence Act treated electronic records after its amendment. However, whether every specific requirement is worded identically, or has been updated or expanded in the BSA, should be verified against the current text rather than assumed to be an unchanged copy-paste of the old provision, since the BSA is a distinct enactment.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.61 ('Electronic or digital record.') | The Bharatiya Sakshya Adhiniyam, 2023 s.63 ('Admissibility of electronic records.') | The Bharatiya Sakshya Adhiniyam, 2023 s.170 ('Repeal and savings.') | The Bharatiya Sakshya Adhiniyam, 2023 s.85 ('Presumption as to electronic agreements.') | The Bharatiya Sakshya Adhiniyam, 2023 s.63 ('Admissibility of electronic records.')

**Citations:**
["Section 61 ('Electronic or digital record.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 63 ('Admissibility of electronic records.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 170 ('Repeal and savings.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 85 ('Presumption as to electronic agreements.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 63 ('Admissibility of electronic records.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]

**Classification:** `CITATION_ERROR`

**Reason for Review:**
Classification: CITATION_ERROR; Low score (4/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 4/11

---

## [eval_075] Evidence Law (Easy)

**Question:**
What is the general rule about hearsay evidence being admissible in Indian courts?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
The general rule regarding hearsay evidence is codified in Section 20 of the Bharatiya Sakshya Adhiniyam, 2023. Oral admissions as to the contents of a document are not relevant unless the party proposing to prove them shows entitlement to give secondary evidence of the document's contents under the rules contained in the Act, or unless the genuineness of a document produced is in question.

**Reference Answer:**
As a general rule, hearsay evidence -- an out-of-court statement offered to prove the truth of the matter asserted, where the maker is not before the court to be cross-examined -- is not admissible, because it cannot be tested by cross-examination and its reliability cannot be assessed directly by the court. There are specific, defined exceptions (such as dying declarations, certain admissions, and statements made in the course of business) where hearsay-type statements are made admissible by law.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.141 ('Judge to decide as to admissibility of evidence.') | The Bharatiya Sakshya Adhiniyam, 2023 s.168 ('Judge's power to put questions or order production.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.318 ('Record in High Court.') | The Bharatiya Sakshya Adhiniyam, 2023 s.159 ('Questions tending to corroborate evidence of relevant fact, admissible.') | The Bharatiya Sakshya Adhiniyam, 2023 s.20 ('When oral admissions as to contents of documents are relevant.')

**Citations:**
["Section 141 ('Judge to decide as to admissibility of evidence.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 168 ('Judge's power to put questions or order production.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 318 ('Record in High Court.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 159 ('Questions tending to corroborate evidence of relevant fact, admissible.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 20 ('When oral admissions as to contents of documents are relevant.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_076] Evidence Law (Medium)

**Question:**
What is the difference between 'relevant' facts and 'admissible' evidence?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
Under Section 141 of the Bharatiya Sakshya Adhiniyam, 2023, a fact is 'relevant' if it makes another fact more or less probable, while 'admissible' means the court has decided it can be legally used as evidence.

**Reference Answer:**
Relevancy is a question of logical connection -- whether a fact has a bearing on a fact in issue such that the law recognises it as relevant (for example, facts forming part of the same transaction, motive, or conduct). Admissibility is a narrower, more technical concept about whether evidence of a relevant fact can actually be received by the court, which also depends on satisfying procedural and formal requirements (such as proper proof of a document, or compliance with a certificate requirement for electronic evidence). A fact can be relevant but the evidence offered to prove it may still be inadmissible if it does not meet these formal requirements.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.141 ('Judge to decide as to admissibility of evidence.') | The Bharatiya Sakshya Adhiniyam, 2023 s.159 ('Questions tending to corroborate evidence of relevant fact, admissible.') | The Bharatiya Sakshya Adhiniyam, 2023 s.27 ('Relevancy of certain evidence for proving, in subsequent proceeding, truth of facts therein') | The Bharatiya Sakshya Adhiniyam, 2023 s.7 ('Facts necessary to explain or introduce fact in issue or relevant facts.') | The Bharatiya Sakshya Adhiniyam, 2023 s.4 ('Relevancy of facts forming part of same transaction.')

**Citations:**
["Section 141 ('Judge to decide as to admissibility of evidence.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 159 ('Questions tending to corroborate evidence of relevant fact, admissible.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 27 ('Relevancy of certain evidence for proving, in subsequent proceeding, truth of facts therein'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 7 ('Facts necessary to explain or introduce fact in issue or relevant facts.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 4 ('Relevancy of facts forming part of same transaction.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_078] Family Law (Easy)

**Question:**
A married couple wants to end their marriage quickly by drafting and notarising a private separation deed between themselves, without approaching any court. Will this deed legally dissolve their Hindu marriage?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
NO. A private separation deed between spouses does not legally dissolve a Hindu marriage. Under the Hindu Marriage Act, 1955 (as continued in force by Section 531 of the BNSS), a marriage can only be dissolved through a decree of mutual consent, nullity, or restitution granted by a competent family court. A private agreement lacks the statutory recognition required to terminate a marriage.

**Reference Answer:**
No. Under Indian personal law applicable to Hindus, a marriage validly solemnised cannot be dissolved merely by a private agreement between the spouses, however it is documented; dissolution of marriage requires a decree of divorce granted by a competent court, including in cases of divorce by mutual consent, which still requires filing a joint petition and following the court process (including the statutory waiting period between motions, which a court can waive in appropriate circumstances). A privately notarised separation deed of this kind has no legal effect in dissolving the marriage, however it is documented or notarised.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.128 ('Communications during marriage.') | The Bharatiya Nyaya Sanhita, 2023 s.83 ('Marriage ceremony fraudulently gone through without lawful marriage.') | The Bharatiya Sakshya Adhiniyam, 2023 s.135 ('Production of title-deeds of witness not a party.') | The Bharatiya Sakshya Adhiniyam, 2023 s.92 ('Presumption as to documents thirty years old.') | The Bharatiya Nyaya Sanhita, 2023 s.82 ('Marrying again during lifetime of husband or wife.')

**Citations:**
["Section 128 ('Communications during marriage.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 83 ('Marriage ceremony fraudulently gone through without lawful marriage.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 135 ('Production of title-deeds of witness not a party.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 92 ('Presumption as to documents thirty years old.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 82 ('Marrying again during lifetime of husband or wife.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_080] Family Law (Medium)

**Question:**
Can a domestic violence complaint under the PWDV Act be filed only against a husband, and not against in-laws or other relatives?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
This premise is legally incorrect. Under Section 85 of the Bharatiya Nyaya Sanhita, 2023, the offence of cruelty is not limited to husbands alone — it extends to 'relative[s] of the husband' as well, including in-laws and other close family members.

**Reference Answer:**
No. The Protection of Women from Domestic Violence Act, 2005 allows a complaint to be filed against a 'respondent', which is defined broadly to include any adult male person who is or has been in a domestic relationship with the aggrieved woman, and -- importantly -- also allows relatives of the husband/male partner (including female relatives, in certain circumstances) to be made respondents along with the husband/male partner, when the woman alleges domestic violence involving them as well. It is not restricted to the husband alone.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.85 ('Husband or relative of husband of a woman subjecting her to cruelty.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.219 ('Prosecution for offences against marriage.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.221 ('Cognizance of offence.') | The Bharatiya Sakshya Adhiniyam, 2023 s.117 ('Presumption as to abetment of suicide by a married woman.') | The Bharatiya Sakshya Adhiniyam, 2023 s.126 ('Competency of husband and wife as witnesses in certain cases.')

**Citations:**
["Section 85 ('Husband or relative of husband of a woman subjecting her to cruelty.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 219 ('Prosecution for offences against marriage.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 221 ('Cognizance of offence.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 117 ('Presumption as to abetment of suicide by a married woman.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 126 ('Competency of husband and wife as witnesses in certain cases.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_081] Family Law (Hard)

**Question:**
Besides filing a criminal complaint, what kinds of orders can a Magistrate pass in favour of an aggrieved woman under the domestic violence law?

**Model Answer (Fixed V2 + RAG):**
Under Section 163 of the Bharatiya Nagarik Suraksha Sanhita, 2023, a Magistrate has the power to issue an order in urgent cases of nuisance or apprehended danger, directing a person to abstain from a certain act or take certain action regarding property in their possession or management, if the Magistrate considers such direction likely to prevent obstruction, annoyance, injury, danger to human life, health, or safety, or a disturbance of public tranquillity, riot, or affray. This power is specifically invoked in urgent situations involving domestic violence, such as restraining a respondent from entering the shared household, removing the respondent from the household, or directing the respondent to pay interim maintenance.

**Reference Answer:**
The PWDV Act is primarily a civil-remedy statute (though breach of certain orders can attract criminal liability) that allows an aggrieved woman to seek a protection order (restraining further acts of violence), a residence order (regarding the right to reside in the shared household, which may include restraining the respondent from dispossessing her), a monetary relief order (for expenses/losses, including medical expenses and loss of earnings), a custody order for children, and a compensation order for injury, including mental torture and emotional distress caused by the domestic violence.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.219 ('Prosecution for offences against marriage.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.364 ('Procedure when Magistrate cannot pass sentence sufficiently severe.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.278 ('Acquittal or conviction.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.163 ('Power to issue order in urgent cases of nuisance or apprehended danger.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.6 ('Classes of Criminal Courts.')

**Citations:**
["Section 219 ('Prosecution for offences against marriage.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 364 ('Procedure when Magistrate cannot pass sentence sufficiently severe.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 278 ('Acquittal or conviction.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 163 ('Power to issue order in urgent cases of nuisance or apprehended danger.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 6 ('Classes of Criminal Courts.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_082] Family Law (Medium)

**Question:**
Under the POCSO Act, is the consent of a minor a defence to a charge of sexual assault?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
NO. Under Section 63 of the Bharatiya Nyaya Sanhita, 2023, consent of a minor below 18 years of age is legally irrelevant — the offence of rape is established regardless of consent.

**Reference Answer:**
No. The POCSO Act treats any person below the age of 18 as a 'child', and consent is not a defence to offences under the Act because a minor is legally considered incapable of giving valid consent to sexual acts for the purposes of this law; the focus is on the age of the child rather than on whether the child appeared to agree.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.120 ('Presumption as to absence of consent in certain prosecution for rape.') | The Bharatiya Nyaya Sanhita, 2023 s.44 ('Right of private defence against deadly assault when there is risk of harm to innocent') | The Bharatiya Nyaya Sanhita, 2023 s.63 ('Rape.') | The Bharatiya Sakshya Adhiniyam, 2023 s.48 ('Evidence of character or previous sexual experience not relevant in certain cases.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.245 ('When offence proved included in offence charged.')

**Citations:**
["Section 120 ('Presumption as to absence of consent in certain prosecution for rape.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 44 ('Right of private defence against deadly assault when there is risk of harm to innocent'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 63 ('Rape.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 48 ('Evidence of character or previous sexual experience not relevant in certain cases.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 245 ('When offence proved included in offence charged.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_083] Family Law (Medium)

**Question:**
Does the POCSO Act apply only to offences committed by strangers, or can it apply to family members as well?

**Model Answer (Fixed V2 + RAG):**
The POCSO Act, 2012 applies to all children below 18 years of age, regardless of whether the perpetrator is a stranger or a family member. In practice, the Act specifically includes provisions for reporting and investigating offences committed by family members, recognizing that a significant proportion of child sexual abuse occurs within the home.

**Reference Answer:**
The POCSO Act applies regardless of the accused's relationship to the child, and in fact contains specific 'aggravated' categories of offences where the offender is a person in a position of trust or authority over the child, which can include family members, relatives, or persons in a domestic relationship with the child, and such aggravated categories generally attract more severe punishment than the same offence committed by a stranger.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.1 ('Short title, commencement and application.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.289 ('Application of Chapter.') | The Bharatiya Nyaya Sanhita, 2023 s.111 ('Organised crime.') | The Bharatiya Sakshya Adhiniyam, 2023 s.99 ('Evidence as to application of language which can apply to one only of several persons.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.33 ('Public to give information of certain offences.')

**Citations:**
["Section 1 ('Short title, commencement and application.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 289 ('Application of Chapter.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 111 ('Organised crime.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 99 ('Evidence as to application of language which can apply to one only of several persons.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 33 ('Public to give information of certain offences.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_084] Family Law (Hard)

**Question:**
A wife seeks maintenance from her husband. Under what different laws could such a claim be made, and does the choice of law matter?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
Under Section 144 of the Bharatiya Nagarik Suraksha Sanhita, 2023, a Magistrate of the First Class can order a person with sufficient means to make a monthly allowance for the maintenance of their wife, children, or parents who are unable to maintain themselves. This remedy is available regardless of whether the couple is married under Hindu, Muslim, Christian, or secular civil law.

**Reference Answer:**
A wife may be able to seek maintenance under more than one law depending on the facts and her personal law -- for example, under Section 125 of the erstwhile CrPC (now the corresponding provision under the BNSS) as a general, religion-neutral remedy available to any wife (and certain other dependents) unable to maintain herself, under the Hindu Marriage Act (if the parties are Hindus and maintenance is sought as an ancillary relief in matrimonial proceedings), under the Hindu Adoptions and Maintenance Act (for Hindus, independent of matrimonial proceedings), or under the PWDV Act (as monetary relief, if domestic violence is alleged). These remedies are not mutually exclusive but the specific conditions, forum, and quantum considerations differ, and courts generally account for amounts already awarded under one law when assessing a claim under another to avoid double recovery.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.144 ('Order for maintenance of wives, children and parents.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.146 ('Alteration in allowance.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.144 ('Order for maintenance of wives, children and parents.') | The Bharatiya Nyaya Sanhita, 2023 s.67 ('Sexual intercourse by husband upon his wife during separation.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.219 ('Prosecution for offences against marriage.')

**Citations:**
["Section 144 ('Order for maintenance of wives, children and parents.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 146 ('Alteration in allowance.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 144 ('Order for maintenance of wives, children and parents.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 67 ('Sexual intercourse by husband upon his wife during separation.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 219 ('Prosecution for offences against marriage.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_085] Company Law (Easy)

**Question:**
Does incorporation of a company give it a legal identity separate from its shareholders and directors?

**Model Answer (Fixed V2 + RAG):**
Yes, incorporation gives a company a distinct legal personality separate from its shareholders and directors. Under Section 65 of the Bharatiya Nagarik Suraksha Sanhita, 2023, a summons served on a company is treated as served on the company itself, not on individual shareholders or directors. This principle is further reinforced by Section 342, which allows a company to appoint a representative for court proceedings, treating that representative as the company's voice in court rather than requiring the personal appearance of shareholders or directors.

**Reference Answer:**
Yes. Upon incorporation under the Companies Act, a company becomes a separate legal person distinct from its shareholders and directors, capable of owning property, entering contracts, suing and being sued in its own name. This is the doctrine of a corporate 'separate legal personality', which generally shields shareholders and directors from personal liability for the company's debts beyond their investment, subject to exceptions such as piercing the corporate veil in cases of fraud or improper conduct.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.65 ('Service of summons on corporate bodies, firms, and societies.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.342 ('Procedure when corporation or registered society is an accused.') | The Bharatiya Nyaya Sanhita, 2023 s.72 ('Disclosure of identity of victim of certain offences, etc.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.20 ('Directorate of Prosecution.')

**Citations:**
["Section 65 ('Service of summons on corporate bodies, firms, and societies.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 342 ('Procedure when corporation or registered society is an accused.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 72 ('Disclosure of identity of victim of certain offences, etc.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 20 ('Directorate of Prosecution.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_086] Company Law (Medium)

**Question:**
Do company directors have absolute immunity from personal liability for the company's defaults?

**Model Answer (Fixed V2 + RAG):**
### Legal Response:
Company directors and officers are not immune from personal liability for the company's defaults. Under Section 316 of the Bharatiya Nyaya Sanhita, 2023, a person entrusted with property who dishonestly misappropriates or converts it to personal use commits criminal breach of trust, punishable with imprisonment up to five years, a fine, or both. Directors and officers who misuse company funds or assets for personal gain fall squarely within this definition.

**Reference Answer:**
No. While directors generally are not personally liable for the company's debts merely by virtue of being directors, director immunity is not absolute -- directors can face personal liability in specific circumstances, such as for statutory defaults where the law imposes personal liability on 'officers in default' (for example, certain tax, labour, or regulatory defaults), for fraud, for acting beyond their authority, for certain cheque-dishonour liability where they were in charge of and responsible for the company's business, and in cases where courts pierce the corporate veil.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.65 ('Service of summons on corporate bodies, firms, and societies.') | The Bharatiya Nyaya Sanhita, 2023 s.316 ('Criminal breach of trust.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.342 ('Procedure when corporation or registered society is an accused.') | The Bharatiya Nyaya Sanhita, 2023 s.8 ('Amount of fine, liability in default of payment of fine, etc.') | The Bharatiya Nyaya Sanhita, 2023 s.193 ('Liability of owner, occupier, etc., of land on which an unlawful assembly or riot takes')

**Citations:**
["Section 65 ('Service of summons on corporate bodies, firms, and societies.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 316 ('Criminal breach of trust.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 342 ('Procedure when corporation or registered society is an accused.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 8 ('Amount of fine, liability in default of payment of fine, etc.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 193 ('Liability of owner, occupier, etc., of land on which an unlawful assembly or riot takes'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_088] Company Law (Hard)

**Question:**
A cheque issued by a company towards repayment of a loan is dishonoured due to insufficient funds. Who can be prosecuted -- only the company, or also its directors?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
The Bharatiya Nyaya Sanhita, 2023 (BNS) does not contain a specific offence of cheque dishonour for insufficiency of funds. Dishonour of cheques for insufficient funds is governed by Section 138 of the Negotiable Instruments Act, 1881 (NI Act), which prescribes imprisonment up to two years and/or a fine up to twice the cheque amount.

**Reference Answer:**
Under Section 138 of the Negotiable Instruments Act, 1881, dishonour of a cheque for insufficiency of funds (subject to the statutory notice and payment conditions) is an offence, and where the drawer is a company, Section 141 extends liability to every person who, at the time the offence was committed, was in charge of and responsible to the company for the conduct of its business, in addition to the company itself. Directors who were not in charge of or responsible for the day-to-day conduct of the business at the relevant time may not automatically be liable merely because they hold the position of director; liability depends on the specific role and involvement, which is a question of fact.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.316 ('Criminal breach of trust.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.120 ('Forfeiture of property in certain cases.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.342 ('Procedure when corporation or registered society is an accused.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.65 ('Service of summons on corporate bodies, firms, and societies.')

**Citations:**
["Section 316 ('Criminal breach of trust.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 120 ('Forfeiture of property in certain cases.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 342 ('Procedure when corporation or registered society is an accused.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 65 ('Service of summons on corporate bodies, firms, and societies.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_090] Company Law (Hard)

**Question:**
If a company fails to file its annual financial statements or annual return for several consecutive years, what consequences can follow?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
Section 342 of the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) governs the procedure when a corporation or registered society is an accused in an inquiry or trial. Under sub-section (2), a corporation may appoint a representative for the inquiry or trial without requiring the seal of the corporation. Sub-section (3) allows the representative to be treated as the accused for procedural purposes, while sub-section (4) provides that where a representative does not appear, the requirement to examine the accused does not apply. Sub-section (5) presumes the validity of a written statement signed by the managing director or authorised person appointing a representative, rebuttable only by contrary proof. Sub-section (6) empowers the court to determine whether a person appearing as a representative is genuinely authorised.

**Reference Answer:**
Consequences can include monetary penalties on the company and its officers in default for the delayed/non-filing, and, in more serious or prolonged cases of non-compliance, action by the Registrar of Companies to strike the company's name off the register (treating it as a defunct company) under the relevant provisions, along with potential disqualification of the directors from being reappointed as directors of that company or being appointed as directors of other companies for a specified period, if the non-filing continues for the statutorily specified duration. The exact penalty amounts and disqualification period should be checked against the current provisions and any applicable government relief schemes in force at the relevant time.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.342 ('Procedure when corporation or registered society is an accused.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.323 ('Return of commission.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.25 ('Sentence in cases of conviction of several offences at one trial.') | The Bharatiya Nyaya Sanhita, 2023 s.177 ('Failure to keep election accounts.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.244 ('Where it is doubtful what offence has been committed.')

**Citations:**
["Section 342 ('Procedure when corporation or registered society is an accused.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 323 ('Return of commission.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 25 ('Sentence in cases of conviction of several offences at one trial.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 177 ('Failure to keep election accounts.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 244 ('Where it is doubtful what offence has been committed.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_096] Labour Law (Easy)

**Question:**
Can an employer terminate a permanent workman's employment without following any procedure, simply by paying one month's salary in lieu of notice?

**Model Answer (Fixed V2 + RAG):**
This premise is legally incorrect. Under Section 144 of the Bharatiya Nagarik Suraksha Sanhita, 2023, a Magistrate may order a person with sufficient means to make a monthly allowance for the maintenance of a wife, child, parent, or father or mother who is unable to maintain themselves. This remedy is distinct from and independent of the Industrial Disputes Act, 1947, which governs retrenchment compensation and notice periods for workmen.

**Reference Answer:**
Not generally, if the workman is covered under industrial/labour welfare legislation applicable to 'workmen' -- termination of a workman (retrenchment) for reasons other than as a punishment for misconduct generally requires compliance with conditions such as notice or pay in lieu of notice, retrenchment compensation, and (for industrial establishments above a specified size) prior permission or notice to the appropriate government, in addition to the 'last come, first go' principle where applicable. Whether a specific employee qualifies as a 'workman' under the applicable law, and which conditions apply, depends on the nature of their role and the size/type of the establishment.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.144 ('Order for maintenance of wives, children and parents.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.160 ('Procedure on order being made absolute and consequences of disobedience.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.183 ('Recording of confessions and statements.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.145 ('Procedure.') | The Bharatiya Nyaya Sanhita, 2023 s.316 ('Criminal breach of trust.')

**Citations:**
["Section 144 ('Order for maintenance of wives, children and parents.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 160 ('Procedure on order being made absolute and consequences of disobedience.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 183 ('Recording of confessions and statements.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 145 ('Procedure.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 316 ('Criminal breach of trust.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `WRONG_DOMAIN_RETRIEVAL`

**Reason for Review:**
Classification: WRONG_DOMAIN_RETRIEVAL; Low score (3/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 3/11

---

## [eval_097] Labour Law (Medium)

**Question:**
Is an employee entitled to gratuity only after completing a minimum period of continuous service?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
The premise that an employee is entitled to gratuity only after completing a minimum period of continuous service is legally valid. Gratuity entitlement under the Payment of Gratuity Act, 1972 requires continuous service of five years or more, and the Act applies to all establishments employing 10 or more persons.

**Reference Answer:**
Generally, yes -- under the Payment of Gratuity Act, gratuity is ordinarily payable to an employee who has rendered continuous service of a minimum specified period (currently five years) on termination of employment due to superannuation, retirement, resignation, death, or disablement, with the minimum-service condition generally waived in cases of death or disablement. The exact minimum period and any special relaxations should be checked against the current statutory text and applicable notifications.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.293 ('Continuance of nuisance after injunction to discontinue.') | The Bharatiya Nyaya Sanhita, 2023 s.8 ('Amount of fine, liability in default of payment of fine, etc.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.67 ('Procedure when service cannot be effected as before provided.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.396 ('Victim compensation scheme.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.144 ('Order for maintenance of wives, children and parents.')

**Citations:**
["Section 293 ('Continuance of nuisance after injunction to discontinue.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 8 ('Amount of fine, liability in default of payment of fine, etc.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 67 ('Procedure when service cannot be effected as before provided.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 396 ('Victim compensation scheme.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 144 ('Order for maintenance of wives, children and parents.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_101] Arbitration/Civil Procedure (Medium)

**Question:**
On what limited grounds can an arbitral award be challenged/set aside by a court in India?

**Model Answer (Fixed V2 + RAG):**
### Legal Response:
An arbitral award can be challenged/set aside by a court on limited statutory grounds under Section 34 of the Arbitration and Conciliation Act, 1996.

**Reference Answer:**
An arbitral award can be set aside only on limited, specified grounds -- such as incapacity of a party, invalidity of the arbitration agreement, lack of proper notice of appointment of the arbitrator or of the arbitral proceedings, the award dealing with a dispute not falling within the terms of submission to arbitration, improper composition of the tribunal or procedure, the subject matter not being capable of settlement by arbitration, or the award being in conflict with the public policy of India (which itself is narrowly construed by courts, generally limited to matters like fraud, corruption, contravention of fundamental policy of Indian law, or conflict with basic notions of justice/morality). Courts generally cannot re-examine the merits of the dispute as if hearing an appeal.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.99 ('Application to High Court to set aside declaration of forfeiture.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.516 ('Exclusion of time in certain cases.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.399 ('Compensation to persons groundlessly arrested.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.519 ('Extension of period of limitation in certain cases.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.273 ('Compensation for accusation without reasonable cause.')

**Citations:**
["Section 99 ('Application to High Court to set aside declaration of forfeiture.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 516 ('Exclusion of time in certain cases.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 399 ('Compensation to persons groundlessly arrested.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 519 ('Extension of period of limitation in certain cases.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 273 ('Compensation for accusation without reasonable cause.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_102] Arbitration/Civil Procedure (Medium)

**Question:**
What is the general limitation period for filing a suit for recovery of money based on a written contract?

**Model Answer (Fixed V2 + RAG):**
### Legal Answer:
The general limitation period for filing a suit for recovery of money based on a written contract is three years from the date the cause of action arose, under Section 3(3) of the Limitation Act, 1963.

**Reference Answer:**
The general limitation period for filing a suit for recovery of money due on a written contract is three years from the date the right to sue accrues (typically the date of default or breach), under the general Limitation Act provisions applicable to contracts, unless a different, specific limitation period is prescribed for that particular type of claim. If the suit is filed after this period, it is generally barred, subject to specific provisions on extension of limitation (such as acknowledgment of debt or, in limited situations, condonation of delay where permitted).

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.514 ('Bar to taking cognizance after lapse of period of limitation.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.519 ('Extension of period of limitation in certain cases.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.515 ('Commencement of period of limitation.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.513 ('Definitions.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.516 ('Exclusion of time in certain cases.')

**Citations:**
["Section 514 ('Bar to taking cognizance after lapse of period of limitation.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 519 ('Extension of period of limitation in certain cases.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 515 ('Commencement of period of limitation.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 513 ('Definitions.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 516 ('Exclusion of time in certain cases.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_105] Mixed / Real-World Scenario (Medium)

**Question:**
A person paid a builder for a flat, and possession is now several months overdue beyond the date promised in the agreement for sale. What does the law generally allow such a buyer to do?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
This query concerns a buyer's rights under Section 18 of the Real Estate (Regulation and Development) Act, 2016 (RERA). RERA is a specialized enactment governing real estate transactions, distinct from general criminal or civil law.

**Reference Answer:**
Under Section 18(1) of the Real Estate (Regulation and Development) Act, 2016, if a promoter fails to complete or is unable to give possession of an apartment in accordance with the terms of the agreement for sale, the allottee has the option to either withdraw from the project and claim a refund of the amount paid along with interest, or to continue with the project, in which case the promoter must pay interest for every month of delay until possession is handed over. The exact interest rate is fixed by the rules of the relevant State's Real Estate Regulatory Authority, not by a fixed figure in the Act itself, so the applicable state rules should be checked for the precise rate.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.499 ('Payment to innocent purchaser of money found on accused.') | The Bharatiya Nyaya Sanhita, 2023 s.219 ('Obstructing sale of property offered for sale by authority of public servant.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.88 ('Release, sale and restoration of attached property.') | The Bharatiya Nyaya Sanhita, 2023 s.220 ('Illegal purchase or bid for property offered for sale by authority of public servant.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.504 ('Procedure where no claimant appears within six months.')

**Citations:**
["Section 499 ('Payment to innocent purchaser of money found on accused.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 219 ('Obstructing sale of property offered for sale by authority of public servant.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 88 ('Release, sale and restoration of attached property.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 220 ('Illegal purchase or bid for property offered for sale by authority of public servant.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 504 ('Procedure where no claimant appears within six months.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_107] Mixed / Real-World Scenario (Medium)

**Question:**
A retail app collects a user's continuous background location without showing any privacy notice or taking consent. What legal issue does this raise?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
This raises a substantive criminal liability issue under the Bharatiya Nyaya Sanhita, 2023 (BNS). Under Section 303 BNS, 'Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft.' Since the user's continuous background location data is a form of personal information, collecting it without consent constitutes dishonest movement of that property, raising a prima facie theft offence.

**Reference Answer:**
This raises a notice-and-consent compliance issue under the Digital Personal Data Protection Act, 2023: a data fiduciary is generally required to give the data principal a clear, itemised notice describing what personal data (such as location) is being collected and for what purpose, and to obtain free, specific, informed, and unambiguous consent before or at the time of collection. Collecting continuous background location silently, without such notice and consent, would not meet this standard and could expose the company to enforcement action and financial penalties under the Act.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.35 ('When police may arrest without warrant.') | The Bharatiya Nyaya Sanhita, 2023 s.303 ('Theft.') | The Bharatiya Nyaya Sanhita, 2023 s.77 ('Voyeurism.') | The Bharatiya Sakshya Adhiniyam, 2023 s.132 ('Professional communications.') | The Bharatiya Nyaya Sanhita, 2023 s.211 ('Omission to give notice or information to public servant by person legally bound to give')

**Citations:**
["Section 35 ('When police may arrest without warrant.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 303 ('Theft.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 77 ('Voyeurism.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 132 ('Professional communications.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 211 ('Omission to give notice or information to public servant by person legally bound to give'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_108] Mixed / Real-World Scenario (Medium)

**Question:**
A senior citizen's adult child refuses to maintain or take care of them despite having sufficient means, and the senior citizen wants a legal remedy. What options exist?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
Under Section 144 of the Bharatiya Nagarik Suraksha Sanhita, 2023, a Magistrate of the First Class can order a person with sufficient means to make a monthly allowance for the maintenance of their wife, children, or parents who are unable to maintain themselves. In practice, this means the senior citizen can file an application before the local Magistrate seeking a monthly maintenance allowance from the adult child, supported by evidence of the child's means and the senior citizen's inability to maintain themselves.

**Reference Answer:**
The Maintenance and Welfare of Parents and Senior Citizens Act, 2007 allows a senior citizen (or a parent) who is unable to maintain themselves to apply to a Maintenance Tribunal for an order directing their children or relatives (who would inherit their property) to pay a monthly allowance for maintenance. The Act also allows a senior citizen who has transferred property to a relative on the condition of being maintained, and is not being so maintained, to seek that the transfer be declared void by the Tribunal in certain circumstances, in addition to providing for protection of life and property and establishment of old-age homes.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.144 ('Order for maintenance of wives, children and parents.') | The Bharatiya Nyaya Sanhita, 2023 s.93 ('Exposure and abandonment of child under twelve years of age, by parent or person having') | The Bharatiya Nyaya Sanhita, 2023 s.137 ('Kidnapping.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.208 ('Offence committed outside India.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.144 ('Order for maintenance of wives, children and parents.')

**Citations:**
["Section 144 ('Order for maintenance of wives, children and parents.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 93 ('Exposure and abandonment of child under twelve years of age, by parent or person having'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 137 ('Kidnapping.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 208 ('Offence committed outside India.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 144 ('Order for maintenance of wives, children and parents.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_109] Mixed / Real-World Scenario (Hard)

**Question:**
An RTI application is filed with a public authority, but no response is received within the statutory time limit. What can the applicant do?

**Model Answer (Fixed V2 + RAG):**
### Legal Response:
Under Section 514 of the Bharatiya Nagarik Suraksha Sanhita, 2023, no court shall take cognizance of an offence of the category specified in sub-section (2) after the expiry of the prescribed period of limitation. For offences punishable with imprisonment up to one year, the limitation period is one year from the date of filing the complaint or recording information.

**Reference Answer:**
Under the Right to Information Act, 2005, a Public Information Officer is generally required to respond to a request within thirty days of receipt (or forty-eight hours for information concerning life or liberty, and a somewhat longer period if the request has to be transferred or if it involves a third party). If no response is received within the prescribed time, the request is deemed to have been refused, and the applicant can file a first appeal to the departmental appellate authority within the specified period, and, if still unsatisfied, a second appeal to the State or Central Information Commission, as applicable; the Information Commission also has the power to impose a penalty on the Public Information Officer for unreasonable delay or unjustified refusal.

**Retrieved Sources:**
The Bharatiya Nagarik Suraksha Sanhita, 2023 s.516 ('Exclusion of time in certain cases.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.290 ('Application for plea bargaining.') | The Bharatiya Nyaya Sanhita, 2023 s.209 ('Non-appearance in response to a proclamation under section 84 of Bharatiya Nagarik') | The Bharatiya Nyaya Sanhita, 2023 s.1 ('Short title, commencement and application.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.514 ('Bar to taking cognizance after lapse of period of limitation.')

**Citations:**
["Section 516 ('Exclusion of time in certain cases.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 290 ('Application for plea bargaining.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 209 ('Non-appearance in response to a proclamation under section 84 of Bharatiya Nagarik'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 1 ('Short title, commencement and application.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 514 ('Bar to taking cognizance after lapse of period of limitation.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_114] Hallucination Detection (Medium)

**Question:**
Is it true that 'first-time offenders under the BNS are always granted probation instead of jail time' as a fixed statutory rule?

**Model Answer (Fixed V2 + RAG):**
This statement is legally false. Under Section 4 of the Bharatiya Nyaya Sanhita, 2023, the punishment for offences is imprisonment, fine, or community service, with no blanket statutory rule granting probation to first-time offenders.

**Reference Answer:**
No, this is not an accurate general statement of a fixed rule. While Indian law does have provisions allowing courts to release certain offenders on probation instead of sentencing them to imprisonment (generally for less serious offences and subject to the court's discretion, the offender's antecedents, and the nature of the offence), this is a discretionary possibility in appropriate cases under the applicable probation law, not an automatic entitlement that applies to 'first-time offenders' as a blanket rule under the BNS. An AI system should avoid stating this kind of sweeping, inaccurate generalisation as if it were a fixed statutory guarantee.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.11 ('Solitary confinement.') | The Bharatiya Nyaya Sanhita, 2023 s.4 ('Punishments.') | The Bharatiya Nyaya Sanhita, 2023 s.64 ('Punishment for rape.') | The Bharatiya Nyaya Sanhita, 2023 s.71 ('Punishment for repeat offenders.') | The Bharatiya Nyaya Sanhita, 2023 s.303 ('Theft.')

**Citations:**
["Section 11 ('Solitary confinement.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 4 ('Punishments.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 64 ('Punishment for rape.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 71 ('Punishment for repeat offenders.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 303 ('Theft.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_115] Cross-Domain (Hard)

**Question:**
A consumer buys a defective product online, the seller refuses a refund, and the consumer also suspects the seller's website used a fake payment gateway to steal card details. Which laws could potentially be relevant, and would the consumer need to choose only one?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
The Bharatiya Nyaya Sanhita, 2023 (BNS) Section 318 defines 'cheating' as inducing a person to deliver property or consent to retain property through deceit, causing damage or harm. This covers fraudulent inducement to buy a defective product.

**Reference Answer:**
This fact pattern potentially engages more than one area of law simultaneously: the defective product and refusal to refund could be pursued as a consumer complaint under the Consumer Protection Act, 2019 (including its specific e-commerce provisions), while the suspected fake payment gateway and card-detail theft could separately raise issues under the Information Technology Act, 2000 (relevant provisions dealing with computer-related fraud/cheating) and potentially the BNS provisions on cheating, along with a complaint to the bank regarding unauthorized transactions. These are not mutually exclusive; a consumer can pursue a consumer complaint for the product/refund issue and a separate cybercrime complaint for the alleged card-detail theft, since they arise from different aspects of the same overall episode.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.318 ('Cheating.') | The Bharatiya Sakshya Adhiniyam, 2023 s.136 ('Production of documents or electronic records which another person, having possession,') | The Bharatiya Sakshya Adhiniyam, 2023 s.168 ('Judge's power to put questions or order production.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.499 ('Payment to innocent purchaser of money found on accused.')

**Citations:**
["Section 318 ('Cheating.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 136 ('Production of documents or electronic records which another person, having possession,'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 168 ('Judge's power to put questions or order production.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 499 ('Payment to innocent purchaser of money found on accused.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_117] Cross-Domain (Hard)

**Question:**
A landlord wants to evict a tenant who has stopped paying rent, and separately believes the tenant sent a threatening message over WhatsApp. Should these two issues be combined into a single case?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
The landlord's two issues — unpaid rent and a threatening message — involve distinct legal frameworks and remedies. Unpaid rent is governed by the Rent Control Act or relevant tenancy legislation, while the threatening message falls under the Bharatiya Nyaya Sanhita, 2023's provisions on extortion. Combining them into a single case risks diluting the evidentiary focus needed for each.

**Reference Answer:**
No, generally these are two distinct legal matters that would ordinarily be pursued through separate proceedings: the non-payment-of-rent/eviction issue would typically be addressed through civil proceedings under the Transfer of Property Act (default notice/termination of lease) and/or applicable state Rent Control legislation, while the threatening WhatsApp message could separately raise a criminal complaint (potentially under BNS provisions on criminal intimidation, and/or the IT Act, depending on the exact content), filed with the police. The two matters arise from different facts and different legal frameworks (civil landlord-tenant law versus criminal law) and are not typically combined into a single case.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.122 ('Estoppel of tenant and of licensee of person in possession.') | The Bharatiya Nyaya Sanhita, 2023 s.308 ('Extortion.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.243 ('Trial for more than one offence.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.85 ('Attachment of property of person absconding.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.164 ('Procedure where dispute concerning land or water is likely to cause breach of')

**Citations:**
["Section 122 ('Estoppel of tenant and of licensee of person in possession.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 308 ('Extortion.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 243 ('Trial for more than one offence.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 85 ('Attachment of property of person absconding.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 164 ('Procedure where dispute concerning land or water is likely to cause breach of'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_119] Cross-Domain (Hard)

**Question:**
An employee is dismissed from a private company after being falsely accused of theft of office property, and the company also files a police complaint. Does an acquittal in the criminal case automatically mean the dismissal from employment was illegal?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
#### Statutory Grounding:
The premise that an acquittal in the criminal case automatically invalidates the dismissal from employment is legally incorrect. Under Section 306 of the Bharatiya Nyaya Sanhita, 2023, theft by a clerk or servant of property in possession of the master is a distinct offence from the general definition of theft, attracting a higher punishment of up to seven years.

**Reference Answer:**
Not automatically. A criminal acquittal and the legality of a disciplinary dismissal are governed by different standards and different proceedings: a criminal court requires proof of guilt beyond reasonable doubt, while a domestic/departmental disciplinary inquiry into misconduct generally applies a lower standard (such as preponderance of probability) and is examined by labour/industrial forums (if the employee qualifies as a 'workman') primarily for whether principles of natural justice were followed and whether the finding was perverse, not by re-trying the criminal case. So an acquittal in the criminal case does not automatically invalidate a properly conducted disciplinary dismissal, though the facts and any specific findings in the criminal case could still be relevant evidence in a labour dispute.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.316 ('Criminal breach of trust.') | The Bharatiya Nyaya Sanhita, 2023 s.217 ('False information, with intent to cause public servant to use his lawful power to injury of') | The Bharatiya Nyaya Sanhita, 2023 s.344 ('Falsification of accounts.') | The Bharatiya Nyaya Sanhita, 2023 s.306 ('Theft by clerk or servant of property in possession of master.') | The Bharatiya Nyaya Sanhita, 2023 s.2 ('Definitions.')

**Citations:**
["Section 316 ('Criminal breach of trust.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 217 ('False information, with intent to cause public servant to use his lawful power to injury of'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 344 ('Falsification of accounts.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 306 ('Theft by clerk or servant of property in possession of master.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 2 ('Definitions.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_120] Cross-Domain (Medium)

**Question:**
A start-up wants to protect both its brand name and its proprietary software algorithm. What different intellectual property protections, if any, would typically apply to each?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
The brand name and the proprietary software algorithm require distinct intellectual property protections. The brand name is protected under trademark law, while the proprietary software algorithm is protected under copyright law.

**Reference Answer:**
The brand name would typically be protected through trademark registration under the Trade Marks Act, 1999, which protects distinctive marks used to identify goods/services in trade. The proprietary software algorithm, on the other hand, is generally not eligible for patent protection as such because computer programmes 'per se' and algorithms are excluded from patentability under the Patents Act, though the underlying source code itself is automatically protected by copyright as a literary work under the Copyright Act; in some cases, a broader software-related invention with a genuine technical effect tied to specific hardware might be separately assessed for patent eligibility, but that is a narrower, fact-specific question.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.2 ('Definitions.') | The Bharatiya Nyaya Sanhita, 2023 s.225 ('Threat of injury to induce person to refrain from applying for protection to public') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.42 ('Protection of members of Armed Forces from arrest.')

**Citations:**
["Section 2 ('Definitions.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 225 ('Threat of injury to induce person to refrain from applying for protection to public'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 42 ('Protection of members of Armed Forces from arrest.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_123] Cross-Domain (Hard)

**Question:**
A dispute arises out of a commercial contract that contains both an arbitration clause and a consumer-facing warranty claim by an individual buyer. Would the consumer be forced into arbitration for their warranty complaint?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
The Arbitration and Conciliation Act, 1996 governs commercial arbitration agreements, while consumer disputes are governed by the Consumer Protection Act, 2019. The Supreme Court has held that a consumer's right to file a complaint under the Consumer Protection Act cannot be ousted by an arbitration clause in a contract.

**Reference Answer:**
Not necessarily. Even where a contract contains an arbitration clause, Indian courts have generally held that a consumer is not compelled to pursue their statutory consumer-protection remedies through arbitration merely because of such a clause, on the reasoning that Consumer Protection Act remedies are in addition to other remedies and consumer disputes involve a public-interest dimension beyond a purely private commercial dispute; the exact outcome can still depend on the specific facts, the nature of the transaction (commercial vs individual/consumer use), and current precedent, so a case-specific check is advisable, particularly if the buyer's use of the goods could be characterised as commercial rather than personal.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.95 ('Exclusion of evidence of oral agreement.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.164 ('Procedure where dispute concerning land or water is likely to cause breach of') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.166 ('Dispute concerning right of use of land or water.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.87 ('Claims and objections to attachment.') | The Bharatiya Sakshya Adhiniyam, 2023 s.94 ('Evidence of terms of contracts, grants and other dispositions of property reduced to form of')

**Citations:**
["Section 95 ('Exclusion of evidence of oral agreement.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 164 ('Procedure where dispute concerning land or water is likely to cause breach of'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 166 ('Dispute concerning right of use of land or water.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 87 ('Claims and objections to attachment.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 94 ('Evidence of terms of contracts, grants and other dispositions of property reduced to form of'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_124] Mixed / Real-World Scenario (Medium)

**Question:**
A person was in a car accident and wants to know whether they can be held criminally liable. Can this be answered definitively without more facts?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
The Bharatiya Nyaya Sanhita, 2023 (BNS) governs substantive criminal liability, while the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) governs criminal procedure. The Bharatiya Sakshya Adhiniyam, 2023 (BSA) governs admissibility of evidence. Without knowing the exact date of the accident, it is impossible to determine whether the substantive offence is governed by the BNS or the IPC.

**Reference Answer:**
No, not definitively on the facts given. Criminal liability in a motor accident depends heavily on specifics such as whether there was rash or negligent driving, whether death or grievous hurt resulted, whether the driver was under the influence of alcohol/drugs, whether there was a hit-and-run element, and the driver's state of mind -- these facts determine which offence (if any) is made out and its severity. Without these details, only a general statement of the relevant legal framework (covering rash/negligent driving, causing death by negligence, and related motor vehicle law provisions) can be given, not a definitive conclusion about liability in this specific case.

**Retrieved Sources:**
The Bharatiya Sakshya Adhiniyam, 2023 s.99 ('Evidence as to application of language which can apply to one only of several persons.') | The Bharatiya Sakshya Adhiniyam, 2023 s.157 ('Question by party to his own witness.') | The Bharatiya Nyaya Sanhita, 2023 s.18 ('Accident in doing a lawful act.') | The Bharatiya Sakshya Adhiniyam, 2023 s.3 ('Evidence may be given of facts in issue and relevant facts.') | The Bharatiya Sakshya Adhiniyam, 2023 s.119 ('Court may presume existence of certain facts.')

**Citations:**
["Section 99 ('Evidence as to application of language which can apply to one only of several persons.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 157 ('Question by party to his own witness.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 18 ('Accident in doing a lawful act.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 3 ('Evidence may be given of facts in issue and relevant facts.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 119 ('Court may presume existence of certain facts.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

## [eval_125] Mixed / Real-World Scenario (Medium)

**Question:**
Someone wants to know if their upcoming business contract is 'legally safe.' Can this be assessed without seeing the contract?

**Model Answer (Fixed V2 + RAG):**
### Legal Analysis:
#### Statutory Grounding:
- **Contractual Terms and Oral Agreements:** Under Section 94 of the Bharatiya Sakshya Adhiniyam, 2023, once a contract, grant, or disposition of property is reduced to writing, oral evidence of its terms is excluded, except for proving matters that invalidate the document or entitle someone to a decree or order.

**Reference Answer:**
No, not meaningfully. Whether a contract is 'legally safe' depends on the actual terms used, the specific obligations, the identity and capacity of the parties, applicable sector-specific regulations, and how risk (such as indemnity, liability caps, termination, and dispute-resolution clauses) is allocated -- none of which can be assessed without reviewing the contract itself. General principles of contract law (offer, acceptance, consideration, free consent, lawful object) can be explained, but a genuine risk assessment requires reviewing the specific document, ideally with a lawyer who can also account for the particular industry and transaction context.

**Retrieved Sources:**
The Bharatiya Nyaya Sanhita, 2023 s.357 ('Breach of contract to attend on and supply wants of helpless person.') | The Bharatiya Sakshya Adhiniyam, 2023 s.94 ('Evidence of terms of contracts, grants and other dispositions of property reduced to form of') | The Bharatiya Sakshya Adhiniyam, 2023 s.95 ('Exclusion of evidence of oral agreement.') | The Bharatiya Nagarik Suraksha Sanhita, 2023 s.359 ('Compounding of offences.') | The Bharatiya Sakshya Adhiniyam, 2023 s.147 ('Evidence as to matters in writing.')

**Citations:**
["Section 357 ('Breach of contract to attend on and supply wants of helpless person.'), The Bharatiya Nyaya Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496548>", "Section 94 ('Evidence of terms of contracts, grants and other dispositions of property reduced to form of'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 95 ('Exclusion of evidence of oral agreement.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>", "Section 359 ('Compounding of offences.'), The Bharatiya Nagarik Suraksha Sanhita, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496550>", "Section 147 ('Evidence as to matters in writing.'), The Bharatiya Sakshya Adhiniyam, 2023, w.e.f. 2024-07-01, Version: 1.0-ORIGINAL-ENACTMENT, Authority: Legislative Department, Ministry of Law and Justice, Government of India, Official Repository: <https://indiacode.gov.in/handle/123456789/496549>"]

**Classification:** `INCORRECT`

**Reason for Review:**
Low score (5/11)

**Diagnosis:** Evidence Status: `ANSWERABLE`, Total Score: 5/11

---

