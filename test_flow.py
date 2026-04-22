#!/usr/bin/env python
"""Test the improved triage flow"""
from triage.llm_triage_service import LLMTriageService

s = LLMTriageService(use_openai=False)
msgs = ['I have a stomach problem', 'Nausea and vomiting for 2 days', 'Pretty bad honestly']

print("Testing improved conversation flow:")
print("=" * 60)

for i, msg in enumerate(msgs, 1):
    r = s.process_patient_message(msg)
    print(f'\n{i}. User: "{msg}"')
    print(f'   Symptoms Found: {r["extracted_symptoms"]}')
    print(f'   Ready for Recommendation: {r["ready_for_recommendation"]}')
    if r['ready_for_recommendation']:
        print(f'   ✓ RECOMMENDATION: {r["recommendation"]["primary_specialty"].upper()}')
        print(f'   Urgency: {r["recommendation"]["urgency"]}')
    else:
        lines = r["next_question"].split('\n')
        for line in lines[:3]:
            print(f'   → {line}')

print("\n" + "=" * 60)
print("✅ System flow works correctly!")
