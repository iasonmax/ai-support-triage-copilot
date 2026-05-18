import streamlit as st
from safety import check_input_safety, get_safety_message

st.set_page_config(
    page_title="AI Support Triage Co-Pilot",
    page_icon="🛠️",
    layout="wide",
)


st.title("AI Support Triage Co-Pilot")
st.caption(
    "Local proof-of-concept assistant for safe IT support triage using a "
    "local markdown knowledge base."
)

st.warning(
    "Demo safety notice: This assistant does not perform real IT actions. "
    "Do not enter passwords, MFA codes, recovery codes, or sensitive personal "
    "data. / Μην εισάγετε κωδικούς πρόσβασης, κωδικούς MFA, recovery codes ή "
    "ευαίσθητα προσωπικά δεδομένα."
)

col1, col2 = st.columns(2)

with col1:
    mode = st.radio(
        "Choose mode / Επιλέξτε λειτουργία",
        options=["End User", "Support Analyst"],
        horizontal=True,
    )

with col2:
    language = st.radio(
        "Response language / Γλώσσα απάντησης",
        options=["English", "Greek"],
        horizontal=True,
    )

issue_description = st.text_area(
    "Describe the IT issue / Περιγράψτε το πρόβλημα IT",
    placeholder=(
        "Example: I cannot connect to VPN. It says authentication failed.\n"
        "Παράδειγμα: Δεν μπορώ να συνδεθώ στο VPN. Εμφανίζει σφάλμα "
        "authentication failed."
    ),
    height=180,
)

submitted = st.button("Generate triage response / Δημιουργία απάντησης")

if submitted:
    safety_result = check_input_safety(issue_description)

    if not safety_result.is_safe:
        st.error(get_safety_message(safety_result, language))

        with st.expander("Safety reason / Αιτία ελέγχου ασφαλείας"):
            st.code(safety_result.reason)

    else:
        st.subheader("Triage Response / Απάντηση Διαλογής")

        if language == "Greek":
            st.write(
                "Εδώ θα εμφανιστεί η απάντηση διαλογής που θα δημιουργηθεί "
                "από το AI."
            )
        else:
            st.write("This is where the AI-generated triage response will appear.")

        st.subheader("Draft Ticket / Πρόχειρο Ticket")
        st.json(
            {
                "summary": "Draft summary will appear here",
                "category": "To be suggested",
                "subcategory": "To be suggested",
                "priority": "To be suggested",
                "assignment_group": "To be suggested",
                "language": language,
                "mode": mode,
            }
        )

        st.subheader("Sources / Πηγές")
        st.info("Retrieved knowledge base articles will appear here.")