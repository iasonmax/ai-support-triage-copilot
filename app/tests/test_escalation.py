# test_escalation.py
import sys
from pathlib import Path

# Add parent directory to path so we can import from app/
sys.path.insert(0, str(Path(__file__).parent.parent))

from escalation import detect_escalation_keywords

test_cases = [
    ("Didn't work at all", True, ["failed"]),
    ("Tried twice but still broken", True, ["multiple_attempts", "failed"]),
    ("Whole team can't work now", True, ["business_impact"]),
    ("This is critical, urgent!", True, ["failed"]),
    ("Thanks for the help", False, []),
    ("Error 500 appeared", True, ["failed"]),
    ("Even after restart, still frozen", True, ["multiple_attempts", "failed"]),
]

print("Testing escalation detection:\n")
for text, should_escalate, expected_reasons in test_cases:
    result = detect_escalation_keywords(text)
    
    print(f"Text: {text}")
    print(f"  Escalated: {result['escalation_triggered']} (expected: {should_escalate})")
    print(f"  Reasons: {result['reasons']} (expected: {expected_reasons})")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Matched: {result['matched_keywords']}")
    
    if result['escalation_triggered'] == should_escalate:
        print("  ✅ PASS")
    else:
        print("  ❌ FAIL")
    print()