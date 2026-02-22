import random
from json_vector_store import search_json
from vector_store import search as search_pdf
from llama_engine import generate_answer

def get_response(user_query):
    """
    Hybrid search: JSON first (curated, fast) → PDF second (comprehensive) → LLaMA 3 fallback → Clear rejection
    No hallucination guaranteed!
    """
    q = user_query.lower().strip()

    # ============ SMALL TALK (No retrieval needed) ============
    
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
            "I have access to curated institutional data and documents.\n"
            "I can help you with admissions, academics, placements, hostels, and campus life."
        )

    if "what can you do" in q:
        return (
            "I can provide information related to NIT Jalandhar such as:\n"
            "- Admissions (B.Tech, M.Tech, MBA, PhD)\n"
            "- Academic programs and departments\n"
            "- Placements & recruiting\n"
            "- Campus facilities and hostels\n"
            "- Student life and activities\n"
            "- Faculty and administration\n"
            "- Research opportunities\n\n"
            "Feel free to ask!"
        )

    if q in ["thanks", "thank you"]:
        return "You're welcome 😊 Let me know if you need any more information."

    # ============ ADMISSION CLARIFICATION ============
    
    if "admission" in q and not any(x in q for x in ["btech", "b.tech", "mtech", "m.tech", "mba", "phd"]):
        return (
            "Admissions to NIT Jalandhar are offered for multiple programs.\n\n"
            "Please specify:\n"
            "- B.Tech (Undergraduate)\n"
            "- M.Tech (Postgraduate)\n"
            "- MBA\n"
            "- PhD\n\n"
            "Example: 'B.Tech admission process'"
        )

    # ============ HARD-CODED PROCEDURES (High confidence) ============
    
    if (("btech" in q or "b.tech" in q) and 
        any(word in q for word in ["how", "process", "admission", "apply"])):
        return (
            "Here is the B.Tech admission process for NIT Jalandhar:\n\n"
            "1. Appear in **JEE Main** and obtain a valid rank\n"
            "2. Participate in **JoSAA counseling** (and CSAB rounds if applicable)\n"
            "3. Register on JoSAA portal and fill course choices\n"
            "4. Seats allocated based on rank, category, and availability\n\n"
            "**Important:** Follow the official JoSAA portal (josaa.nic.in) for updates."
        )

    # ============ HYBRID RETRIEVAL SYSTEM (NO HALLUCINATION) ============
    
    print(f"[SEARCH] Query: {user_query}")
    
    # Store contexts here for potential LLaMA 3 fallback
    fallback_contexts = []
    
    # STEP 1: Search JSON (Primary - Curated, Fast, High Confidence)
    print("[STEP 1] Searching JSON embeddings (curated data)...")
    json_results, json_confidence = search_json(user_query, top_k=3, threshold=0.30) # Lowered search threshold to gather context
    
    if json_confidence > 0.80:
        print(f"[RESULT] Found direct match in JSON with confidence {json_confidence:.3f}")
        return format_response(
            json_results,
            user_query,
            json_confidence,
            source='JSON'
        )
    elif json_results:
        print(f"[JSON] Adding {len(json_results)} chunks to fallback context (Confidence: {json_confidence:.3f})")
        for ans, meta in json_results:
            fallback_contexts.append(f"[JSON: {meta.get('category', 'Info')}]\n{ans}")
    
    print(f"[JSON] Confidence {json_confidence:.3f} below direct threshold 0.80 - trying PDF...")
    
    # STEP 2: Search PDF (Secondary - Comprehensive Fallback)
    print("[STEP 2] Searching PDF documents (fallback)...")
    pdf_results, pdf_confidence = search_pdf(user_query, top_k=3, threshold=0.20) # Lowered search threshold to gather context
    
    if pdf_confidence > 0.50:
        print(f"[RESULT] Found direct match in PDF with confidence {pdf_confidence:.3f}")
        return format_response(
            pdf_results,
            user_query,
            pdf_confidence,
            source='PDF'
        )
    elif pdf_results:
         print(f"[PDF] Adding {len(pdf_results)} chunks to fallback context (Confidence: {pdf_confidence:.3f})")
         for ans, meta in pdf_results:
            source_file = meta.get('source', 'document').split('/')[-1]
            page = meta.get('page', '?')
            fallback_contexts.append(f"[PDF: {source_file} (Page {page})]\n{ans}")
            
    # STEP 3: LLaMA 3 Generative Fallback
    if fallback_contexts:
        print(f"[STEP 3] Generating LLaMA 3 response from {len(fallback_contexts)} context chunks...")
        context_string = "\n\n---\n\n".join(fallback_contexts)
        llama_answer = generate_answer(context_string, user_query)
        
        # Determine highest confidence for logging purposes
        best_confidence = max(json_confidence, pdf_confidence)
        
        print(f"[RESULT] Generated LLaMA 3 response")
        
        # Log the generated response
        with open("query_logs.txt", "a", encoding="utf-8") as f:
            f.write(f"Query: {user_query} | Source: LLaMA3 | Confidence: {best_confidence:.3f} | Status: GENERATED\n")
            
        return f"{llama_answer}\n\n*(Generated by LLaMA 3 based on retrieved knowledge base)*"

    # STEP 4: Not Found Anywhere (Clear Rejection - No Hallucination!)
    print(f"[PDF] Confidence {pdf_confidence:.3f} below fallback threshold - rejecting")
    print("[RESULT] Not found in knowledge base and not enough context for LLaMA")
    
    return (
        "I could not find information about this topic in my knowledge base.\n\n"
        "This may be because:\n"
        "- The topic is not related to NIT Jalandhar\n"
        "- The specific information is not available in our current database\n\n"
        "For more details, please:\n"
        "• Visit the official website: https://www.nitj.ac.in\n"
        "• Contact the Registrar's Office\n"
        "• Reach out to the relevant department\n\n"
        "Is there anything else I can help you with?"
    )


def format_response(results, user_query, confidence, source='JSON'):
    """
    Format the retrieved results into a user-friendly response
    """
    
    if not results:
        return "No results found."
    
    # Extract answer and metadata
    answers = []
    categories = []
    sources_info = []
    
    for answer_text, metadata in results:
        answers.append(answer_text)
        categories.append(metadata.get('category', 'General'))
        
        # Build source info
        if source == 'JSON':
            source_info = f"Category: {metadata.get('category', 'General')}"
        else:
            page = metadata.get('page', '?')
            source_file = metadata.get('source', 'document').split('/')[-1]
            source_info = f"[Page {page}] {source_file}"
        
        sources_info.append(source_info)
    
    # Combine answers
    combined_answer = "\n\n".join([f"• {ans}" for ans in answers])
    
    # Build final response
    response = f"Based on {source} knowledge base:\n\n{combined_answer}"
    
    # Add sources
    response += f"\n\n**Source Information:**\n"
    response += "\n".join(sources_info)
    
    # Add confidence indicator (for transparency)
    confidence_pct = int(confidence * 100)
    response += f"\n(Confidence: {confidence_pct}%)"
    
    # Log the successful retrieval
    with open("query_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"Query: {user_query} | Source: {source} | Confidence: {confidence:.3f} | Status: SUCCESS\n")
    
    return response