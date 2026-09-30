from src.api.llm_fallback import query_llm_with_fallback, call_vllm, call_gemini

print("--- 1. Testing Primary NVIDIA GPU vLLM (port 8009) ---")
vllm_res = call_vllm([{"role": "user", "content": "Hello vLLM"}], max_tokens=15)
if vllm_res:
    print(f"[NVIDIA GPU Online]: {vllm_res}")
else:
    print("[NVIDIA GPU Offline / Not Responding]")

print("\n--- 2. Testing Fallback Gemini API Key ---")
gemini_res = call_gemini([{"role": "user", "content": "Hello Gemini"}], max_tokens=15)
if gemini_res:
    print(f"[Gemini Fallback Online]: {gemini_res}")
else:
    print("[Gemini Fallback Failed]")

print("\n--- 3. Testing Full Orchestrated Function ---")
final_res = query_llm_with_fallback([{"role": "user", "content": "Confirm you are active in 5 words."}], max_tokens=15)
print(f"[Orchestrated Result]: {final_res}")
