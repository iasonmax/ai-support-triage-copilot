import re
from dataclasses import dataclass


@dataclass
class SafetyResult:
    is_safe: bool
    reason: str
    user_message_en: str
    user_message_el: str


UNSAFE_PATTERNS: list[tuple[str, str]] = [
    (
        "password_or_secret",
        r"\b(password|passcode|passwd|secret|api\s*key|token|private\s*key)\b"
        r"|κωδικ(ός|ο)|κωδικοί|συνθηματικ(ό|ο)|μυστικ(ό|ο)|διακριτικ(ό|ο)",
    ),
    (
        "mfa_or_recovery_code",
        r"\b(mfa|2fa|otp|one[-\s]?time\s?password|verification\s?code|"
        r"recovery\s?code|backup\s?code)\b"
        r"|κωδικ(ός|ο)\s*(mfa|2fa|otp|επαλήθευσης|ανάκτησης)"
        r"|κωδικοί\s*(ανάκτησης|backup)",
    ),
    (
        "bypass_security",
        r"\b(bypass|disable|turn\s*off|circumvent|evade|workaround)\b"
        r".{0,40}\b(mfa|2fa|security|antivirus|edr|firewall|policy|"
        r"conditional\s*access)\b"
        r"|παράκαμψ(η|ω)|απενεργοποι(ώ|ηση).{0,40}"
        r"(mfa|2fa|ασφάλεια|antivirus|firewall|πολιτικ(ή|η))",
    ),
    (
        "credential_theft_or_phishing",
        r"\b(phish|phishing|steal|capture|harvest|dump)\b"
        r".{0,40}\b(password|credential|token|cookie|session)\b"
        r"|υποκλοπ(ή|η)|κλέψ(ω|ε).{0,40}"
        r"(κωδικ|διαπιστευτήρια|token|cookie|session)",
    ),
    (
        "sensitive_personal_data",
        r"\b(ssn|social\s*security|passport|national\s*id|credit\s*card|"
        r"card\s*number|iban|bank\s*account|medical\s*record)\b"
        r"|αριθμ(ός|ο)\s*(ταυτότητας|διαβατηρίου)"
        r"|πιστωτικ(ή|η)\s*κάρτα|iban|τραπεζικ(ός|ο)\s*λογαριασμ(ός|ο)"
        r"|ιατρικ(ός|ο)\s*φάκελος",
    ),
    (
        "claim_real_action",
        r"\b(reset|unlock|delete|disable|enable|create|remove|change)\b"
        r".{0,40}\b(my|the|this|that)?\s*(account|password|user|device|mailbox)\b"
        r"|κάνε\s*(reset|unlock)|ξεκλείδωσε|διέγραψε|απενεργοποίησε"
        r"|ενεργοποίησε.{0,40}(λογαριασμ|χρήστη|συσκευ)",
    ),
]


SAFE_RESPONSE_EN = (
    "I can help with safe IT support triage, but I cannot request, process, "
    "or provide instructions involving passwords, MFA codes, recovery codes, "
    "sensitive personal data, bypassing security controls, or real account "
    "actions. Please remove sensitive details and describe the issue at a "
    "high level. If this is urgent, contact your IT support team through the "
    "approved support channel."
)

SAFE_RESPONSE_EL = (
    "Μπορώ να βοηθήσω με ασφαλή διαλογή αιτημάτων IT, αλλά δεν μπορώ να "
    "ζητήσω, να επεξεργαστώ ή να δώσω οδηγίες που αφορούν κωδικούς "
    "πρόσβασης, κωδικούς MFA, recovery codes, ευαίσθητα προσωπικά δεδομένα, "
    "παράκαμψη ελέγχων ασφαλείας ή πραγματικές ενέργειες σε λογαριασμούς. "
    "Παρακαλώ αφαιρέστε ευαίσθητες πληροφορίες και περιγράψτε το πρόβλημα "
    "σε γενικό επίπεδο. Αν είναι επείγον, επικοινωνήστε με την ομάδα IT "
    "μέσω του εγκεκριμένου καναλιού υποστήριξης."
)


def check_input_safety(text: str) -> SafetyResult:
    """Check user input for unsafe support-triage content.

    This is intentionally conservative for a public proof-of-concept.
    It does not replace enterprise DLP, IAM, or security tooling.
    """

    normalized_text = text.strip().lower()

    if not normalized_text:
        return SafetyResult(
            is_safe=False,
            reason="empty_input",
            user_message_en="Please describe the issue before generating triage.",
            user_message_el="Παρακαλώ περιγράψτε το πρόβλημα πριν τη διαλογή.",
        )

    for reason, pattern in UNSAFE_PATTERNS:
        if re.search(pattern, normalized_text, flags=re.IGNORECASE | re.DOTALL):
            return SafetyResult(
                is_safe=False,
                reason=reason,
                user_message_en=SAFE_RESPONSE_EN,
                user_message_el=SAFE_RESPONSE_EL,
            )

    return SafetyResult(
        is_safe=True,
        reason="safe",
        user_message_en="Input passed the basic safety check.",
        user_message_el="Το κείμενο πέρασε τον βασικό έλεγχο ασφαλείας.",
    )


def get_safety_message(result: SafetyResult, language: str) -> str:
    """Return the safety message in the selected response language."""

    if language == "Greek":
        return result.user_message_el

    return result.user_message_en