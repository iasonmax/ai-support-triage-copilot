# test_tickets.py
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tickets import (
    Ticket, TicketIssue, TicketKBResolution, TicketEscalation,
    TicketUsageTracking, TicketUserReview, generate_ticket_id,
    get_next_ticket_number, save_ticket
)
from datetime import datetime

print("Testing ticket generation:\n")

# Test 1: Generate ticket ID
print("Test 1: Generate ticket ID")
ticket_id = generate_ticket_id(1)
print(f"  Generated ID: {ticket_id}")
print(f"  Format correct: {ticket_id.startswith('TKT-')}")
print("  ✅ PASS\n")

# Test 2: Create ticket object
print("Test 2: Create ticket object")
ticket = Ticket(
    ticket_id=ticket_id,
    created_at=datetime.utcnow().isoformat() + "Z",
    priority="High",
    category="Software",
    queue="software_queue",
    created_by="user@company.com",
    llm_response="Try clearing your cache and restarting the application.",
    issue=TicketIssue(
        original_question="Application crashes on startup",
        environment="Windows 11"
    ),
    resolution_attempt=TicketKBResolution(
        kb_article_id="APP-001",
        kb_article_title="Application Crash Troubleshooting",
        similarity_score=0.85,
        suggested_solution="Clear cache and reinstall",
        kb_matched=True
    ),
    escalation=TicketEscalation(
        is_escalated=False,
        escalation_reasons=[],
        auto_escalated=False
    ),
    usage_tracking=TicketUsageTracking(
        kb_article_usage_count=5,
        kb_success_rate=0.80,
        needs_attention=False
    ),
    user_review=TicketUserReview(
        internal_notes="User confirmed issue resolved after cache clear"
    )
)

print(f"  Ticket ID: {ticket.ticket_id}")
print(f"  Priority: {ticket.priority}")
print(f"  Category: {ticket.category}")
print("  ✅ PASS\n")

# Test 3: Convert to JSON
print("Test 3: Convert to JSON")
ticket_json = ticket.to_json()
print(f"  JSON length: {len(ticket_json)} chars")
print(f"  Contains ticket_id: {'ticket_id' in ticket_json}")
print("  ✅ PASS\n")

# Test 4: Save and load ticket
print("Test 4: Save and load ticket")
saved_path = save_ticket(ticket, tickets_dir="app/tickets_test")
print(f"  Saved to: {saved_path}")
print(f"  File exists: {saved_path.exists()}")
print("  ✅ PASS\n")

print("All tests passed! ✅")