import sys
sys.path.insert(0, '/home/sece2026-student07/legalai-finetuning')
from src.api.query_router import UniversalQueryRouter

r = UniversalQueryRouter()
prompt = """**1. Type of Document:**
Civil Petition / Petition relating to a property dispute

**2. Purpose:**
The petition is being prepared to request the court to protect the petitioner's rights over a property and to seek appropriate relief against the respondent, who is allegedly interfering with the petitioner's lawful possession of the property.

**3. Parties Involved:**

* **Petitioner:** Mr. Arun Kumar, aged 42, residing at Coimbatore, Tamil Nadu
* **Respondent:** Mr. Ravi Kumar, aged 45, residing at Coimbatore, Tamil Nadu
* **Court:** Appropriate jurisdictional Civil Court

**4. Specific Details / Clauses:**

* Description and location of the disputed property
* Petitioner's basis for claiming ownership or lawful possession
* Details of the respondent's alleged interference
* Relevant dates and events
* Details of supporting documents, such as sale deed, patta, tax receipts, or other records
* Request for the court to restrain the respondent from interfering with the petitioner's possession
* Request for any other relief that the court considers appropriate
* Verification that the facts stated in the petition are true to the petitioner's knowledge and belief"""

print("FUZZY MATCH:", r.fuzzy_match_case(prompt))
dec = r.classify(prompt)
print("DECISION INTENT:", dec.intent)
print("SUB INTENT:", dec.sub_intent)
print("USER GOAL:", dec.user_goal)
print("OUTPUT PLAN:", dec.output_plan)
print("CASE_ID:", dec.case_id)
print("REASON:", dec.reason)
