"""Business logic for the AI support chatbot.

Handles article selection, context building, and LLM interaction.
Returns data for main.py to update session state.
"""

from rag import retrieve_relevant_context
from escalation import detect_escalation_keywords
from usage_tracker import UsageTracker
from tickets import (
    Ticket, TicketIssue, TicketKBResolution, TicketEscalation,
    TicketUsageTracking, TicketUserReview, generate_ticket_id,
    get_next_ticket_number
)
from datetime import datetime


RELEVANCE_THRESHOLD = 0.7


def should_show_article_selector(search_results):
    """Decide if we should show article selector or auto-use top result.
    
    Args:
        search_results: List of (doc, score) tuples from RAG retrieval
        
    Returns:
        bool: True if should show selector, False to auto-use top result
    """
    if not search_results:
        return False
    
    top_score = search_results[0][1]
    return top_score < RELEVANCE_THRESHOLD


def build_context(selected_idx, search_results):
    """Build context string for the LLM based on article selection.
    
    Args:
        selected_idx: Index of selected article, or None if no article
        search_results: List of (doc, score) tuples
        
    Returns:
        str: Formatted context for the LLM
    """
    if selected_idx is None:
        return "(No knowledge base article selected)"
    
    if not search_results or selected_idx >= len(search_results):
        return "(Article not found)"
    
    selected_doc, selected_score = search_results[selected_idx]
    return (
        f"**Selected Article (relevance: {selected_score:.2f}):**\n\n"
        f"{selected_doc.page_content}"
    )


def build_llm_message(question, context):
    """Build the final user message for the LLM.
    
    Args:
        question: User's original question
        context: Context string from build_context()
        
    Returns:
        dict: Message dict with role and content
    """
    return {
        "role": "user",
        "content": (
            f"### User Question:\n{question}\n\n"
            f"### Context from Knowledge Base:\n{context}"
        ),
    }


def prepare_messages_for_llm(messages, question, context):
    """Prepare the full message history for the LLM.
    
    Replaces the last user message with the enhanced version
    that includes context.
    
    Args:
        messages: List of message dicts from session state
        question: User's original question
        context: Context string from build_context()
        
    Returns:
        list: Message history ready for LLM
    """
    messages_for_llm = messages.copy()
    messages_for_llm[-1] = build_llm_message(question, context)
    return messages_for_llm


def search_knowledge_base(query, vector_store, k=3):
    """Search the knowledge base for relevant articles.
    
    Args:
        query: User's question
        vector_store: Chroma vector store
        k: Number of results to return
        
    Returns:
        list: Search results as (doc, score) tuples
    """
    return retrieve_relevant_context(
        query=query,
        vector_store=vector_store,
        k=k
    )


def prepare_ticket_data(
    user_question: str,
    llm_response: str,
    kb_article_id: str,
    kb_article_title: str,
    kb_similarity_score: float,
    kb_matched: bool,
    created_by: str = "support_user",
    stats_file: str = "kb_usage_stats.json",
) -> dict:
    """
    Prepare ticket data after LLM response.
    
    Detects escalation, gets usage stats, auto-suggests priority/category.
    Does NOT save to disk—returns data for review modal.
    
    Args:
        user_question: Original user question
        llm_response: The response from LLM
        kb_article_id: ID of KB article used (e.g., "VPN-001")
        kb_article_title: Title of KB article
        kb_similarity_score: Relevance score (0.0-1.0)
        kb_matched: Was a KB article matched?
        created_by: User email/name
        stats_file: Path to usage stats file
        
    Returns:
        dict with ticket data ready for review:
        {
            "ticket_id": "TKT-20260526-001",
            "auto_suggested": {...},  # LLM suggestions
            "ticket_object": Ticket,   # Full ticket object
        }
    """
    
    # Initialize tracker
    tracker = UsageTracker(stats_file)
    
    # Detect escalation
    escalation_check = detect_escalation_keywords(user_question)
    
    # Get usage stats for this article
    if kb_matched and kb_article_id:
        tracker.record_suggestion(kb_article_id)
        usage_stats = tracker.get_stats(kb_article_id)
    else:
        usage_stats = {
            "total_times_suggested": 0,
            "times_marked_helpful": 0,
            "times_failed": 0,
            "times_partially_helped": 0,
            "success_rate": 0.0,
        }
    
    # Auto-suggest priority based on escalation + KB match
    priority = _suggest_priority(
        escalation_check=escalation_check,
        kb_matched=kb_matched,
        similarity_score=kb_similarity_score,
        usage_stats=usage_stats,
    )
    
    # Auto-suggest category from KB article ID prefix
    category = _suggest_category(kb_article_id)
    
    # Auto-suggest queue based on category
    queue = _suggest_queue(category)
    
    # Determine if auto-escalate
    auto_escalate = _should_auto_escalate(
        escalation_check=escalation_check,
        kb_matched=kb_matched,
    )
    
    # Generate ticket ID
    ticket_number = get_next_ticket_number("tickets")
    ticket_id = generate_ticket_id(ticket_number)
    
    # Build ticket object
    ticket = Ticket(
        ticket_id=ticket_id,
        created_at=datetime.utcnow().isoformat() + "Z",
        priority=priority,
        category=category,
        queue=queue,
        created_by=created_by,
        llm_response=llm_response,
        status="open",
        issue=TicketIssue(
            original_question=user_question,
            environment=None,  # Could extract from user context later
        ),
        resolution_attempt=TicketKBResolution(
            kb_article_id=kb_article_id or "NONE",
            kb_article_title=kb_article_title or "No article matched",
            similarity_score=kb_similarity_score,
            suggested_solution=llm_response[:500],  # First 500 chars
            kb_matched=kb_matched,
        ),
        escalation=TicketEscalation(
            is_escalated=auto_escalate,
            escalation_reasons=escalation_check["reasons"],
            auto_escalated=auto_escalate,
        ),
        usage_tracking=TicketUsageTracking(
            kb_article_usage_count=usage_stats["total_times_suggested"],
            kb_success_rate=usage_stats["success_rate"],
            needs_attention=usage_stats["success_rate"] < 0.5,
        ),
        user_review=TicketUserReview(),
    )
    
    return {
        "ticket_id": ticket_id,
        "auto_suggested": {
            "priority": priority,
            "category": category,
            "queue": queue,
            "auto_escalated": auto_escalate,
            "escalation_reasons": escalation_check["reasons"],
            "escalation_confidence": escalation_check["confidence"],
        },
        "ticket_object": ticket,
    }


def _suggest_priority(
    escalation_check: dict,
    kb_matched: bool,
    similarity_score: float,
    usage_stats: dict,
) -> str:
    """Suggest priority based on escalation signals."""
    
    # Critical: user triggered escalation keywords with high confidence
    if escalation_check["escalation_triggered"]:
        if escalation_check["confidence"] > 0.66:
            return "Critical"
        elif escalation_check["confidence"] > 0.33:
            return "High"
    
    # High: no KB match
    if not kb_matched:
        return "High"
    
    # High: KB article has low success rate
    if (usage_stats["success_rate"] < 0.5 and
        usage_stats["total_times_suggested"] >= 3):
        return "High"
    
    # Medium: moderate confidence but matched
    if similarity_score >= 0.7:
        return "Medium"
    
    # Low: weak match
    return "Low"


def _suggest_category(kb_article_id: str) -> str:
    """Suggest category from KB article ID prefix."""
    if not kb_article_id or kb_article_id == "NONE":
        return "Other"
    
    prefix = kb_article_id.split("-")[0].upper()
    
    category_map = {
        "VPN": "Network",
        "NET": "Network",
        "HW": "Hardware",
        "APP": "Software",
        "SW": "Software",
        "ACC": "Access",
        "AUTH": "Access",
        "DB": "Software",
    }
    
    return category_map.get(prefix, "Other")


def _suggest_queue(category: str) -> str:
    """Suggest queue based on category."""
    queue_map = {
        "Network": "network_queue",
        "Hardware": "hardware_queue",
        "Software": "software_queue",
        "Access": "access_queue",
        "Other": "general_queue",
    }
    
    return queue_map.get(category, "general_queue")


def _should_auto_escalate(
    escalation_check: dict,
    kb_matched: bool,
) -> bool:
    """Determine if ticket should auto-escalate."""
    
    # Escalate if user triggered keywords
    if escalation_check["escalation_triggered"]:
        return True
    
    # Escalate if no KB match (unhandled issue)
    if not kb_matched:
        return True
    
    return False