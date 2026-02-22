from flask import Flask, render_template, request, jsonify
from chat_engine import get_response
from json_vector_store import initialize_json_store, get_json_stats
from data_loader import load_documents
from vector_store import initialize_vector_store

app = Flask(__name__)

# ============ INITIALIZATION (ONE-TIME AT STARTUP) ============

print("\n" + "="*70)
print("🚀 INITIALIZING HYBRID RAG SYSTEM (JSON + PDF)")
print("="*70)

try:
    # Initialize JSON Store (Primary)
    print("\n[1/2] Initializing JSON Embeddings Store...")
    initialize_json_store(rebuild=False)
    json_stats = get_json_stats()
    print(f"✅ JSON Store Ready: {json_stats['total_qa_pairs']} Q&A pairs loaded")
    print(f"   Categories: {list(json_stats['categories'].keys())}")
    
except Exception as e:
    print(f"❌ Error initializing JSON store: {e}")
    print("⚠️ JSON search will not be available")

try:
    # Initialize PDF Store (Fallback)
    print("\n[2/2] Initializing PDF Documents Store...")
    documents = load_documents()
    
    if documents:
        print(f"📚 Loaded {len(documents)} document chunks from knowledge_base/")
        initialize_vector_store(documents, rebuild=False)
        print("✅ PDF Store Ready")
    else:
        print("⚠️ No PDF documents found in knowledge_base/")
        
except Exception as e:
    print(f"❌ Error initializing PDF store: {e}")
    print("⚠️ PDF search will not be available as fallback")

print("\n" + "="*70)
print("✅ HYBRID RAG SYSTEM INITIALIZED")
print("="*70)
print("Search Order: JSON (High Confidence) → PDF (Fallback) → Clear Rejection")
print("="*70 + "\n")

# ============ ROUTES ============

@app.route("/")
def home():
    """Serve the main chat interface"""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Chat endpoint - hybrid JSON + PDF search
    
    Returns JSON with response
    """
    try:
        user_msg = request.json.get("message")
        
        if not user_msg:
            return jsonify({"reply": "Please enter a message."})
        
        # Get response from hybrid chat engine
        reply = get_response(user_msg)
        
        return jsonify({"reply": reply})
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"reply": f"An error occurred: {str(e)}"})


@app.route("/stats", methods=["GET"])
def stats():
    """
    Get system statistics (optional - for monitoring)
    """
    try:
        json_stats = get_json_stats()
        return jsonify({
            "json_store": json_stats,
            "status": "operational"
        })
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    print("Starting Flask app...")
    print("Open browser: http://127.0.0.1:5000")
    app.run(debug=True)