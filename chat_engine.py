import random
from vector_store import search

RESPONSE_STYLES = [
    "Here is the admission process for NIT Jalandhar:\n\n{context}\n\nFor official updates, please visit the institute website.",
    "Based on NIT Jalandhar admission guidelines:\n\n{context}\n\nYou may also refer to the JoSAA portal for counseling details."
]

def get_response(user_query):
    q = user_query.lower().strip()

    # ---------- SMALL TALK / HUMAN GUARD ----------
    if q in ["hi", "hello", "hey", "hii"]:
        return "Hello 👋 How can I help you with information about NIT Jalandhar?"

    if "how are you" in q:
        return (
            "I'm doing well, thank you for asking 😊\n"
            "How can I assist you with information about NIT Jalandhar today?"
        )

    if "who are you" in q:
        return (
            "I am the NITJ Virtual Assistant 🤖.\n"
            "I can help you with admissions, academics, placements, hostels, and campus life."
        )

    if "what can you do" in q:
        return (
            "I can provide information related to NIT Jalandhar such as:\n"
            "- Admissions\n"
            "- Academic programs\n"
            "- Placements\n"
            "- Hostels and campus life\n\n"
            "Feel free to ask!"
        )

    if q in ["thanks", "thank you"]:
        return "You're welcome 😊 Let me know if you need any more information."

    # ---------- CLARIFICATION FOR AMBIGUOUS ADMISSION ----------
    if "admission" in q and not any(x in q for x in ["btech", "b.tech", "mtech", "mba", "phd"]):
        return (
            "Admissions to NIT Jalandhar are offered for multiple programs.\n\n"
            "Please specify the program you are interested in:\n"
            "- B.Tech (Undergraduate)\n"
            "- M.Tech (Postgraduate)\n"
            "- MBA\n"
            "- PhD\n\n"
            "For example:\n"
            "“How to get admission into NIT Jalandhar for B.Tech?”"
        )

    # ---------- HARD B.TECH PROCEDURAL ROUTE ----------
    if (
        ("btech" in q or "b.tech" in q)
        and any(word in q for word in ["how", "process", "admission", "apply"])
    ):
        return (
            "Here is the B.Tech admission process for NIT Jalandhar:\n\n"
            "- Appear in **JEE Main** and obtain a valid rank.\n"
            "- Participate in **JoSAA counseling** (and CSAB rounds if applicable).\n"
            "- Register on the JoSAA portal and fill in choices.\n"
            "- Seats are allotted based on rank, category, and availability.\n\n"
            "For official updates, please refer to the JoSAA portal and NIT Jalandhar website."
        )

    # ---------- INFORMATION RETRIEVAL ----------
    
    results, confidence = search(user_query, top_k=2)

    # Confidence threshold
    if confidence < 0.45:
        return (
            "I am not confident about this answer.\n"
            "Please try rephrasing your question or visit the official NIT Jalandhar website."
        )

    # Extract contexts
    contexts = [item[0] for item in results]

    combined_context = "\n".join([f"- {ctx}" for ctx in contexts])

    # Log query
    with open("query_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"{user_query} | Confidence: {confidence}\n")

    from llama_engine import generate_answer

    answer = generate_answer(combined_context, user_query)

    return answer
