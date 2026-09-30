import urllib.request
import json

URL = "http://127.0.0.1:8008/api/v1/ai/chat"

def query(text, history=None):
    payload = {"content": text}
    if history:
        payload["history"] = history
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))

print("=== TEST A: GREETING ===")
res_a = query("hi")
print("TYPE:", res_a.get("query_type"))
print("CONTENT:", res_a.get("content"))
assert res_a.get("query_type") == "CONVERSATIONAL"

print("\n=== TEST B: GENERAL CONTEXT ===")
res_b1 = query("write a python code")
print("B1 TYPE:", res_b1.get("query_type"))
print("B1 CONTENT:", res_b1.get("content"))
assert res_b1.get("query_type") == "OUT_OF_SCOPE"

history_b = [
    {"role": "user", "content": "write a python code"},
    {"role": "assistant", "content": res_b1.get("content"), "query_type": "OUT_OF_SCOPE"}
]
res_b2 = query("for odd or even", history=history_b)
print("B2 TYPE:", res_b2.get("query_type"))
print("B2 CONTENT:\n", res_b2.get("content"))
assert res_b2.get("query_type") == "OUT_OF_SCOPE"
assert "input" in res_b2.get("content") or "% 2" in res_b2.get("content") or "even" in res_b2.get("content").lower()

print("\n=== TEST C: CONTEXT SWITCH TO LEGAL ===")
history_c = history_b + [
    {"role": "user", "content": "for odd or even"},
    {"role": "assistant", "content": res_b2.get("content"), "query_type": "OUT_OF_SCOPE"}
]
res_c = query("what is BNS section 103?", history=history_c)
print("C TYPE:", res_c.get("query_type"))
print("C SOURCES:", len(res_c.get("sources", [])))
print("C CONTENT PREVIEW:", res_c.get("content")[:120])
assert res_c.get("query_type") == "LEGAL_QUERY"
assert len(res_c.get("sources", [])) > 0

print("\n=== TEST D: CASE QUERY ===")
res_d = query("what happened in my case?")
print("D TYPE:", res_d.get("query_type"))
assert res_d.get("query_type") == "CASE_QUERY"

print("\n=== TEST E: OUT OF SCOPE ===")
res_e = query("recommend me a movie")
print("E TYPE:", res_e.get("query_type"))
print("E CONTENT:\n", res_e.get("content"))
assert res_e.get("query_type") == "OUT_OF_SCOPE"
assert "outside my main area" in res_e.get("content") or "mainly designed" in res_e.get("content")

print("\n=== TEST F: MIXED QUERY ===")
res_f = query("hey, what is BNS section 103?")
print("F TYPE:", res_f.get("query_type"))
print("F CONTENT PREVIEW:", res_f.get("content")[:120])
assert res_f.get("query_type") == "LEGAL_QUERY"
assert res_f.get("content").startswith("Absolutely! 👋")

print("\n=== TEST G: ABUSIVE LANGUAGE ===")
res_g = query("you are stupid")
print("G TYPE:", res_g.get("query_type"))
print("G CONTENT:", res_g.get("content"))
assert "I’m here to help" in res_g.get("content") or "here to help" in res_g.get("content")

print("\nALL BACKEND CONVERSATION UX TESTS PASSED SUCCESSFULLY!")
