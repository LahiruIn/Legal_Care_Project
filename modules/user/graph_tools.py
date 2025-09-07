from langchain_core.tools import tool
from .vector import retriever  


@tool
def search_laws(question: str) -> str:
    """
    🔎 Tool: Search Sri Lankan Legal Documents

    Given a legal question, retrieve the most relevant law text chunks
    from the embedded PDF documents using hybrid semantic + keyword search.

    Args:
        question (str): The user's legal query.

    Returns:
        str: Plain-text string of relevant legal content extracted from documents.
             Returns a friendly error message if retrieval fails.
    """
    try:
        # Retrieve documents using your configured retriever
        docs = retriever.invoke(question)

        if not docs:
            return "⚠️ No relevant legal documents were found for your query."

        # Combine all retrieved document content into one string
        return "\n\n".join([doc.page_content for doc in docs])

    except Exception as e:
        return f"⚠️ Error retrieving legal documents: {str(e)}"
