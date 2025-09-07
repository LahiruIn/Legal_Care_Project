from typing import TypedDict, List, Tuple
import os
from dotenv import load_dotenv

import google.generativeai as genai
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from .graph_tools import retriever

# Load API Key 
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("🚨 Missing GOOGLE_API_KEY in .env file")

#Initialize Gemini 1.5 Pro 
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")

#  Define State Schema 
class LegalState(TypedDict):
    question: str
    chat_history: str
    retrieved_docs: str
    response: str

# Prompt Template 
template = """
You are a highly specialized **Legal AI Assistant** trained exclusively in **Sri Lankan law**. You MUST provide legally accurate answers ONLY using:

✅ The Constitution of Sri Lanka (1978)  
✅ Official Acts and Ordinances of Sri Lanka  
✅ Verified content from loaded PDF documents (statutes, ordinances, legal commentary)  
✅ Case law from the Supreme Court or Court of Appeal of Sri Lanka  
❌ DO NOT use laws from foreign jurisdictions or uncited assumptions.

───────────────────────────────────────────  
📘 **Extracted Legal Content (from uploaded PDFs):**  
{legal_text}

💬 **Chat Memory / User Context:**  
{chat_history}

⚖️ **User’s Current Legal Question:**  
{question}
───────────────────────────────────────────

📌 **RESPONSE GUIDELINES:**

1. Provide a legally correct answer based ONLY on Sri Lankan statutes, ordinances, or case law.  
2. Cite specific sections or articles (e.g., *Section 7 of the Land Development Ordinance*).  
3. If the user cited a **non-existent** or **wrong law**, politely correct them and refer to the accurate Sri Lankan law.  
4. Use clear and formal legal English appropriate for Sri Lankan legal writing.  
5. DO NOT include disclaimers unless specifically asked.  
6. NEVER fabricate legal acts, ordinance numbers, or citations.

───────────────────────────────────────────

🎯 **RESPONSE FORMAT:**

📌 **Legal Answer (Cited & Precise):**
- Clear legal explanation with accurate citations (section, act, case law).
- Use bullet points or structure if needed for readability.

🔢 **Recommendation (Optional):**
- If relevant, advise the user on the next legal step (e.g., consult a notary, file a case, register a deed).
- Mention procedures, forms, or departments involved in real terms (e.g., DMT, Land Registry).

⚠️ You must ignore laws or citations that do not exist in the Sri Lankan legal system.
"""

# LangGraph Prompt & Chain 
prompt = ChatPromptTemplate.from_template(template)

def run_retriever(state: LegalState) -> LegalState:
    retrieved = retriever.invoke(state["question"])
    return {
        **state,
        "retrieved_docs": retrieved
    }

def get_legal_answer(state: LegalState) -> LegalState:
    final_prompt = prompt.format_messages(
        legal_text=state["retrieved_docs"],
        question=state["question"],
        chat_history=state["chat_history"]
    )[0].content
    response = model.generate_content(final_prompt)
    return {
        **state,
        "response": response.text
    }

# LangGraph Setup 
graph = StateGraph(LegalState)
graph.add_node("retrieve", RunnableLambda(run_retriever))
graph.add_node("answer", RunnableLambda(get_legal_answer))
graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "answer")
graph.add_edge("answer", END)

legal_chain_graph = graph.compile()

# Final Public Function
def get_answer(question: str, chat_history: List[dict]) -> Tuple[str, str]:
    chat_memory = "\n".join([
        f"{'User' if msg['role'] == 'user' else 'Legal AI'}: {msg['content']}"
        for msg in chat_history
    ])
    initial_state: LegalState = {
        "question": question,
        "chat_history": chat_memory,
        "retrieved_docs": "",
        "response": ""
    }
    result = legal_chain_graph.invoke(initial_state)
    return result["response"], result["retrieved_docs"]
