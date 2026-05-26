# tickets.py
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, List
import json
from pathlib import Path


@dataclass
class TicketIssue:
    """The original user issue"""
    original_question: str
    environment: Optional[str] = None


@dataclass
class TicketKBResolution:
    """KB article and resolution attempted"""
    kb_article_id: str
    kb_article_title: str
    similarity_score: float
    suggested_solution: str
    kb_matched: bool = True


@dataclass
class TicketEscalation:
    """Escalation flags"""
    is_escalated: bool
    escalation_reasons: List[str] = field(default_factory=list)
    auto_escalated: bool = False


@dataclass
class TicketUsageTracking:
    """Usage stats for the KB article"""
    kb_article_usage_count: int = 0
    kb_success_rate: float = 0.0
    needs_attention: bool = False


@dataclass
class TicketUserReview:
    """User/support person review of ticket"""
    priority_override: Optional[str] = None
    category_override: Optional[str] = None
    internal_notes: str = ""
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None


@dataclass
class Ticket:
    """Complete ticket structure"""
    ticket_id: str
    created_at: str
    priority: str  # Critical, High, Medium, Low
    category: str  # Network, Hardware, Software, Access, Other
    queue: str     # Which queue to route to
    issue: TicketIssue
    resolution_attempt: TicketKBResolution
    escalation: TicketEscalation
    usage_tracking: TicketUsageTracking
    user_review: TicketUserReview
    llm_response: str = ""
    created_by: Optional[str] = None
    status: str = "open"
    
    def to_dict(self) -> dict:
        """Convert ticket to dictionary (for JSON)"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert ticket to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


def generate_ticket_id(ticket_number: int) -> str:
    """
    Generate ticket ID in format: TKT-YYYYMMDD-NNN
    
    Args:
        ticket_number: Sequential number (1, 2, 3, etc.)
        
    Returns:
        str: Ticket ID like "TKT-20260525-001"
    """
    date_str = datetime.utcnow().strftime("%Y%m%d")
    return f"TKT-{date_str}-{ticket_number:03d}"


def get_next_ticket_number(tickets_dir: str = "tickets") -> int:
    """
    Get the next ticket number by checking existing files.
    
    Args:
        tickets_dir: Path to tickets directory
        
    Returns:
        int: Next ticket number to use
    """
    tickets_path = Path(tickets_dir)
    
    if not tickets_path.exists():
        return 1
    
    # Get all ticket files for today
    today = datetime.utcnow().strftime("%Y%m%d")
    today_tickets = list(tickets_path.glob(f"TKT-{today}-*.json"))
    
    if not today_tickets:
        return 1
    
    # Extract numbers and get the max
    numbers = []
    for file in today_tickets:
        try:
            # Extract number from TKT-YYYYMMDD-NNN.json
            num_str = file.stem.split("-")[-1]
            numbers.append(int(num_str))
        except (IndexError, ValueError):
            continue
    
    return max(numbers) + 1 if numbers else 1


def save_ticket(ticket: Ticket, tickets_dir: str = "tickets") -> Path:
    """
    Save ticket to JSON file.
    
    Args:
        ticket: Ticket object to save
        tickets_dir: Directory to save to
        
    Returns:
        Path: Path where ticket was saved
    """
    tickets_path = Path(tickets_dir)
    tickets_path.mkdir(exist_ok=True)
    
    file_path = tickets_path / f"{ticket.ticket_id}.json"
    
    with open(file_path, "w") as f:
        f.write(ticket.to_json())
    
    return file_path


def load_ticket(ticket_id: str, tickets_dir: str = "tickets") -> dict:
    """
    Load ticket from JSON file.
    
    Args:
        ticket_id: Ticket ID to load (e.g., "TKT-20260525-001")
        tickets_dir: Directory to load from
        
    Returns:
        dict: Parsed ticket data
    """
    file_path = Path(tickets_dir) / f"{ticket_id}.json"
    
    if not file_path.exists():
        raise FileNotFoundError(f"Ticket {ticket_id} not found")
    
    with open(file_path, "r") as f:
        return json.load(f)