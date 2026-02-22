from chat_engine import get_response

test_questions = [
    "How to get admission in NIT Jalandhar?",
    "Tell me about hostel facilities",
    "What is placement percentage?",
    "Library details",
    "Fee structure for BTech"
]

for q in test_questions:
    print("Question:", q)
    print("Response:", get_response(q))
    print("-" * 50)
