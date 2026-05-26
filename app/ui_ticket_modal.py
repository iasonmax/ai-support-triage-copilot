# ui_ticket_modal.py
"""Ticket review modal UI component."""

import streamlit as st
from tickets import Ticket


def render_ticket_review_modal(ticket_data: dict) -> dict:
    """
    Render ticket review modal in a dialog.
    
    User can review auto-suggested values and edit before saving.
    
    Args:
        ticket_data: Dict from flow.prepare_ticket_data() containing:
            - ticket_id: Generated ticket ID
            - auto_suggested: Dict with priority, category, queue, etc.
            - ticket_object: Full Ticket object
            
    Returns:
        dict: {
            "action": "save" or "cancel",
            "ticket": Ticket (with user edits applied) or None,
            "user_review": {
                "priority_override": str or None,
                "category_override": str or None,
                "internal_notes": str,
            }
        }
    """
    
    ticket_obj = ticket_data["ticket_object"]
    auto_suggested = ticket_data["auto_suggested"]
    
    # Use Streamlit dialog for modal
    @st.dialog("Review & Create Ticket")
    def ticket_modal():
        st.markdown("### Ticket Preview")
        
        # Section 1: Issue summary
        st.markdown("#### 📋 Issue")
        st.info(f"**Question:** {ticket_obj.issue.original_question}")
        
        # Section 2: KB article used
        st.markdown("#### 📚 Knowledge Base")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Article ID", ticket_obj.resolution_attempt.kb_article_id)
        with col2:
            st.metric(
                "Relevance",
                f"{ticket_obj.resolution_attempt.similarity_score:.2f}"
            )
        with col3:
            kb_matched_text = "✅ Matched" if ticket_obj.resolution_attempt.kb_matched else "❌ No Match"
            st.metric("Status", kb_matched_text)
        
        st.caption(f"**{ticket_obj.resolution_attempt.kb_article_title}**")
        
        # Section 3: LLM response
        st.markdown("#### 💬 Suggested Response")
        st.write(ticket_obj.llm_response)
        
        st.divider()
        
        # Section 4: Editable fields
        st.markdown("#### ✏️ Ticket Details (Review & Edit)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            priority_options = ["Low", "Medium", "High", "Critical"]
            priority_idx = priority_options.index(auto_suggested["priority"])
            priority = st.selectbox(
                "Priority",
                priority_options,
                index=priority_idx,
                help="Auto-suggested based on escalation signals"
            )
        
        with col2:
            category_options = [
                "Network", "Hardware", "Software", "Access", "Other"
            ]
            category_idx = category_options.index(auto_suggested["category"])
            category = st.selectbox(
                "Category",
                category_options,
                index=category_idx,
                help="Auto-suggested from KB article ID"
            )
        
        with col3:
            queue_options = [
                "network_queue",
                "hardware_queue",
                "software_queue",
                "access_queue",
                "general_queue"
            ]
            queue_idx = queue_options.index(auto_suggested["queue"])
            queue = st.selectbox(
                "Queue",
                queue_options,
                index=queue_idx,
                help="Which team queue to route to"
            )
        
        # Section 5: Escalation info
        st.markdown("#### ⚠️ Escalation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            escalation_status = "🚨 Yes" if auto_suggested["auto_escalated"] else "✅ No"
            st.metric("Auto-Escalated", escalation_status)
        
        with col2:
            if auto_suggested["escalation_reasons"]:
                reasons_text = ", ".join(auto_suggested["escalation_reasons"])
                st.caption(f"**Reasons:** {reasons_text}")
            else:
                st.caption("**Reasons:** None")
        
        # Section 6: Internal notes
        st.markdown("#### 📝 Internal Notes")
        internal_notes = st.text_area(
            "Add notes for the support team (optional)",
            value="",
            height=100,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("💾 Save Ticket", use_container_width=True, type="primary"):
                # Update ticket with user edits
                ticket_obj.priority = priority
                ticket_obj.category = category
                ticket_obj.queue = queue
                ticket_obj.user_review.priority_override = (
                    priority if priority != auto_suggested["priority"] else None
                )
                ticket_obj.user_review.category_override = (
                    category if category != auto_suggested["category"] else None
                )
                ticket_obj.user_review.internal_notes = internal_notes
                ticket_obj.user_review.reviewed_by = "support_user"
                
                from datetime import datetime
                ticket_obj.user_review.reviewed_at = (
                    datetime.utcnow().isoformat() + "Z"
                )
                
                # Store in session state and close dialog
                st.session_state.ticket_review_action = "save"
                st.session_state.reviewed_ticket = ticket_obj
                st.rerun()
        
        with col2:
            if st.button("✕ Cancel", use_container_width=True):
                st.session_state.ticket_review_action = "cancel"
                st.rerun()
        
        with col3:
            st.caption("Ticket ID: " + ticket_obj.ticket_id)
    
    # Show the modal
    ticket_modal()
    
    # Check session state for result
    if "ticket_review_action" in st.session_state:
        action = st.session_state.ticket_review_action
        
        if action == "save":
            result = {
                "action": "save",
                "ticket": st.session_state.reviewed_ticket,
            }
        else:
            result = {
                "action": "cancel",
                "ticket": None,
            }
        
        # Clean up session state
        del st.session_state.ticket_review_action
        if "reviewed_ticket" in st.session_state:
            del st.session_state.reviewed_ticket
        
        return result
    
    # Modal still open
    return {"action": "pending", "ticket": None}


def show_ticket_saved_confirmation(ticket_id: str, file_path: str):
    """Show success message after ticket is saved.
    
    Args:
        ticket_id: ID of saved ticket
        file_path: Path where ticket was saved
    """
    st.success(
        f"✅ Ticket created: **{ticket_id}**\n\n"
        f"Saved to: `{file_path}`"
    )


def show_ticket_creation_button() -> bool:
    """Show 'Create Ticket' button in chat sidebar.
    
    Returns:
        bool: True if button clicked
    """
    with st.sidebar:
        st.divider()
        if st.button(
            "🎫 Create Ticket from Last Response",
            use_container_width=True,
            help="Opens review modal for the latest LLM response"
        ):
            return True
    
    return False