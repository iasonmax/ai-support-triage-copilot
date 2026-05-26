# test_flow_tickets.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flow import prepare_ticket_data
import tempfile

print("Testing ticket generation from flow:\n")

# Test 1: Normal case with KB match
print("Test 1: Normal case with KB match")
with tempfile.TemporaryDirectory() as tmpdir:
    stats_file = Path(tmpdir) / "stats.json"
    
    ticket_data = prepare_ticket_data(
        user_question="How do I connect to the VPN?",
        llm_response="To connect to the VPN, open the VPN client and...",
        kb_article_id="VPN-001",
        kb_article_title="VPN Connection Guide",
        kb_similarity_score=0.85,
        kb_matched=True,
        stats_file=str(stats_file),
    )
    
    print(f"  Ticket ID: {ticket_data['ticket_id']}")
    print(f"  Priority: {ticket_data['auto_suggested']['priority']}")
    print(f"  Category: {ticket_data['auto_suggested']['category']}")
    print(f"  Queue: {ticket_data['auto_suggested']['queue']}")
    print(f"  Auto-escalated: {ticket_data['auto_suggested']['auto_escalated']}")
    print("  ✅ PASS\n")

# Test 2: Escalation case (user says "didn't work")
print("Test 2: Escalation case (user says didn't work)")
with tempfile.TemporaryDirectory() as tmpdir:
    stats_file = Path(tmpdir) / "stats.json"
    
    ticket_data = prepare_ticket_data(
        user_question="I tried the VPN steps but it still doesn't work!",
        llm_response="Let me help. Try clearing your cache...",
        kb_article_id="VPN-001",
        kb_article_title="VPN Connection Guide",
        kb_similarity_score=0.85,
        kb_matched=True,
        stats_file=str(stats_file),
    )
    
    print(f"  Priority: {ticket_data['auto_suggested']['priority']}")
    print(f"  Auto-escalated: {ticket_data['auto_suggested']['auto_escalated']}")
    print(f"  Escalation reasons: {ticket_data['auto_suggested']['escalation_reasons']}")
    print(f"  Confidence: {ticket_data['auto_suggested']['escalation_confidence']:.2f}")
    assert ticket_data['auto_suggested']['auto_escalated'] == True
    print("  ✅ PASS\n")

# Test 3: No KB match case
print("Test 3: No KB match case")
with tempfile.TemporaryDirectory() as tmpdir:
    stats_file = Path(tmpdir) / "stats.json"
    
    ticket_data = prepare_ticket_data(
        user_question="My printer is making weird noises",
        llm_response="I don't have information about this...",
        kb_article_id="",
        kb_article_title="",
        kb_similarity_score=0.0,
        kb_matched=False,
        stats_file=str(stats_file),
    )
    
    print(f"  Priority: {ticket_data['auto_suggested']['priority']}")
    print(f"  Auto-escalated: {ticket_data['auto_suggested']['auto_escalated']}")
    print(f"  Category: {ticket_data['auto_suggested']['category']}")
    assert ticket_data['auto_suggested']['auto_escalated'] == True
    print("  ✅ PASS\n")

# Test 4: Business impact escalation
print("Test 4: Business impact escalation")
with tempfile.TemporaryDirectory() as tmpdir:
    stats_file = Path(tmpdir) / "stats.json"
    
    ticket_data = prepare_ticket_data(
        user_question="All users can't work - entire team is down!",
        llm_response="This is critical. Let me check...",
        kb_article_id="NET-001",
        kb_article_title="Network Outage",
        kb_similarity_score=0.75,
        kb_matched=True,
        stats_file=str(stats_file),
    )
    
    print(f"  Priority: {ticket_data['auto_suggested']['priority']}")
    print(f"  Escalation reasons: {ticket_data['auto_suggested']['escalation_reasons']}")
    # Business impact alone = High, not Critical
    # (Critical requires 2+ escalation categories)
    assert ticket_data['auto_suggested']['priority'] == "High"
    print("  ✅ PASS\n")

# Test 5: Critical priority (multiple escalation signals)
print("Test 5: Critical priority (multiple escalation signals)")
with tempfile.TemporaryDirectory() as tmpdir:
    stats_file = Path(tmpdir) / "stats.json"
    
    ticket_data = prepare_ticket_data(
        user_question="Tried multiple times, still broken, whole team down!",
        llm_response="This is urgent...",
        kb_article_id="NET-001",
        kb_article_title="Network Outage",
        kb_similarity_score=0.75,
        kb_matched=True,
        stats_file=str(stats_file),
    )
    
    print(f"  Priority: {ticket_data['auto_suggested']['priority']}")
    print(f"  Escalation reasons: {ticket_data['auto_suggested']['escalation_reasons']}")
    print(f"  Confidence: {ticket_data['auto_suggested']['escalation_confidence']:.2f}")
    # Multiple reasons = higher confidence = Critical
    assert ticket_data['auto_suggested']['priority'] == "Critical"
    print("  ✅ PASS\n")

print("All flow ticket tests passed! ✅")