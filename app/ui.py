"""UI components for the AI support chatbot."""

import streamlit as st


def extract_title_from_doc(doc):
    """Extract title from markdown document.
    
    Looks for the first # heading in the document.
    Falls back to first 50 chars if no heading found.
    """
    content = doc.page_content
    lines = content.split("\n")
    
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    
    # Fallback
    return content[:50] + "..."


def render_article_selector(search_results):
    """Render the article selection UI.
    
    Shows "No Article" button and list of articles with select buttons.
    
    Args:
        search_results: List of (doc, score) tuples
        
    Returns:
        int or None: Selected article index, or None if no article selected
        Returns None if still waiting for selection (no button clicked)
    """
    st.divider()
    st.subheader("📚 Select Article")

    st.write("Pick an article to guide the response:")
    st.write("")

    # "No Article" option
    if st.button(
        "⊘ Answer without article",
        key="no_article",
        use_container_width=True
    ):
        return None

    st.write("")
    st.markdown("---")
    st.write("")

    # Display articles with titles only
    for i, (doc, score) in enumerate(search_results, 1):
        title = extract_title_from_doc(doc)
        
        col_title, col_btn = st.columns([3, 1])
        
        with col_title:
            st.caption(f"**{title}** (relevance: {score:.2f})")
        
        with col_btn:
            if st.button(
                "Select",
                key=f"article_{i}",
                use_container_width=True
            ):
                return i - 1

    return None  # Still waiting—no button was clicked


def render_chat_history(messages):
    """Render the conversation history.
    
    Args:
        messages: List of message dicts from session state
    """
    st.subheader("Conversation")
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])