import streamlit as st
from pathlib import Path

# Non-Streamlit imports FIRST
from safety import check_input_safety, get_safety_message
from prompts import get_system_prompt
from llm import ask_ollama
from rag import (
    create_embedding_model,
    load_knowledge_base,
    split_documents,
    get_or_create_chroma_store,
)

# Local imports
from flow import (
    should_show_article_selector,
    build_context,
    prepare_messages_for_llm,
    search_knowledge_base,
    prepare_ticket_data,
)
from ui import render_article_selector, render_chat_history
from ui_ticket_modal import (
    render_ticket_review_modal,
    show_ticket_saved_confirmation,
)
from tickets import save_ticket

# st.set_page_config() MUST be first Streamlit command
st.set_page_config(
    page_title="AI End-User Support",
    page_icon="🛠️",
    layout="wide",
)


# Cached functions
@st.cache_resource
def init_vector_store():
    """Load or create vector store once and reuse across reruns."""
    embeddings = create_embedding_model()
    persist_dir = "app/chroma_db"

    if Path(persist_dir).exists():
        return get_or_create_chroma_store([], embeddings, persist_dir)

    docs = load_knowledge_base()
    chunks = split_documents(docs)
    return get_or_create_chroma_store(chunks, embeddings, persist_dir)


# Initialize vector store
vector_store = init_vector_store()

# Session state initialization
if "last_search_results" not in st.session_state:
    st.session_state.last_search_results = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "waiting_for_article_selection" not in st.session_state:
    st.session_state.waiting_for_article_selection = False

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "ticket_data" not in st.session_state:
    st.session_state.ticket_data = None

if "show_ticket_modal" not in st.session_state:
    st.session_state.show_ticket_modal = False

# Page header
st.title("AI End-User Support")
st.caption("Ask questions about common IT issues.")

st.warning(
    "This assistant does not perform real IT actions. "
    "Do not enter passwords, MFA codes, or sensitive data."
)

# New Chat button
if st.button("🔄 New Chat", use_container_width=True):
    st.session_state.messages = []
    st.session_state.last_search_results = []
    st.session_state.waiting_for_article_selection = False
    st.session_state.pending_question = None
    st.session_state.ticket_data = None
    st.session_state.show_ticket_modal = False
    if "selected_article_index" in st.session_state:
        del st.session_state.selected_article_index
    st.rerun()

# ============================================================================
# STEP 1: Get user input
# ============================================================================
issue_description = st.chat_input(
    placeholder="Describe your IT issue..."
)

if issue_description:
    safety_result = check_input_safety(issue_description)

    if not safety_result.is_safe:
        st.error(get_safety_message(safety_result))
        with st.expander("Safety reason"):
            st.code(safety_result.reason)
    else:
        # Safe input—search knowledge base
        st.session_state.pending_question = issue_description

        with st.spinner("Searching knowledge base..."):
            search_results = search_knowledge_base(
                issue_description,
                vector_store
            )
            st.session_state.last_search_results = search_results

        # Decide: show selector or auto-use top result?
        if should_show_article_selector(search_results):
            st.session_state.waiting_for_article_selection = True
        else:
            # Auto-use top result (index 0)
            st.session_state.selected_article_index = 0

# ============================================================================
# STEP 2: Show article selector if needed
# ============================================================================
if (
    st.session_state.waiting_for_article_selection
    and "selected_article_index" not in st.session_state
):
    result = render_article_selector(st.session_state.last_search_results)
    
    if result is not None:
        st.session_state.selected_article_index = result
        st.session_state.waiting_for_article_selection = False
        st.rerun()

# ============================================================================
# STEP 3: Generate response once article is selected
# ============================================================================
if "selected_article_index" in st.session_state:
    selected_idx = st.session_state.selected_article_index
    question = st.session_state.pending_question

    # Build context
    context = build_context(
        selected_idx,
        st.session_state.last_search_results
    )

    # Extract KB article info for ticket generation
    if selected_idx is not None and st.session_state.last_search_results:
        selected_doc, selected_score = st.session_state.last_search_results[selected_idx]
        kb_article_id = selected_doc.metadata.get("source", "UNKNOWN").split("/")[-1].split(".")[0]
        kb_article_title = selected_doc.metadata.get("title", "Unknown Article")
        kb_matched = True
    else:
        kb_article_id = ""
        kb_article_title = ""
        kb_matched = False
        selected_score = 0.0

    # Store user question in chat history
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # Prepare messages for LLM
    messages_for_llm = prepare_messages_for_llm(
        st.session_state.messages,
        question,
        context
    )

    # Call LLM
    with st.spinner("Thinking..."):
        system_prompt = get_system_prompt()
        response = ask_ollama(system_prompt, messages_for_llm)

    # Store response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # Prepare ticket data (for later use)
    st.session_state.ticket_data = prepare_ticket_data(
        user_question=question,
        llm_response=response,
        kb_article_id=kb_article_id,
        kb_article_title=kb_article_title,
        kb_similarity_score=selected_score,
        kb_matched=kb_matched,
        created_by="support_user",
        stats_file="kb_usage_stats.json",
    )

    # Clean up
    del st.session_state.selected_article_index
    st.session_state.pending_question = None
    st.rerun()

# ============================================================================
# STEP 4: Display chat history
# ============================================================================
render_chat_history(st.session_state.messages)

# ============================================================================
# STEP 5: Show "Create Ticket" button if ticket data available
# ============================================================================
if st.session_state.ticket_data:
    st.divider()
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        if st.button(
            "🎫 Create Ticket from Last Response",
            use_container_width=True,
            help="Opens review modal for the latest LLM response"
        ):
            st.session_state.show_ticket_modal = True

# ============================================================================
# STEP 6: Show ticket modal if triggered
# ============================================================================
if st.session_state.show_ticket_modal and st.session_state.ticket_data:
    modal_result = render_ticket_review_modal(st.session_state.ticket_data)
    
    if modal_result["action"] == "save":
        ticket = modal_result["ticket"]
        saved_path = save_ticket(ticket, "tickets")
        show_ticket_saved_confirmation(ticket.ticket_id, str(saved_path))
        
        # Reset ticket state
        st.session_state.show_ticket_modal = False
        st.session_state.ticket_data = None
        st.rerun()
    
    elif modal_result["action"] == "cancel":
        st.session_state.show_ticket_modal = False
        st.rerun()