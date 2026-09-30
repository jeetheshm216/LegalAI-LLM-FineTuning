import sys
sys.path.insert(0, '/home/sece2026-student07/legalai-finetuning')
from src.api.server import generate_case_management_response, LEGALAI_ASSISTANT_IDENTITY

print("--- TEST 1: Identity ---")
print("Identity String:", LEGALAI_ASSISTANT_IDENTITY)

print("\n--- TEST 2: Case Priority with Martinez ('case-01') ---")
res_cm = generate_case_management_response("what is the priority of this case", active_case_id="case-01")
print(res_cm)
assert "Priority Areas" in res_cm
assert "Immediate Procedural Issue" in res_cm
assert "Key Evidentiary Focus" in res_cm
assert "Upcoming Hearing / Deadline" in res_cm
assert "Items Requiring Verification" in res_cm
assert "9/10" not in res_cm, "Arbitrary numerical ranking found!"

print("\n--- TEST 3: Bare focus outside case ---")
res_bare = generate_case_management_response("what should i focus on", active_case_id=None)
print("Response:", res_bare)
assert res_bare == "Which case or task would you like me to focus on?"

print("\n--- TEST 4: Portfolio priority search outside case ---")
res_port = generate_case_management_response("which case has the highest priority", active_case_id=None)
print("Portfolio response snippet:\n", res_port[:160])
assert "Case Portfolio & Workload Overview" in res_port

print("\nSERVER CASE MANAGEMENT & IDENTITY VERIFICATION PASSED 100%!")
