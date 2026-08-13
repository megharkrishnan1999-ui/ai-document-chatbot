from ollama import chat


def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are an AI assistant that answers questions based only on the provided document context.

Document context:
{context}

Question:
{question}

Instructions:
- Answer using only the information provided in the document context.
- If the answer is not present in the context, say that the information is not available in the document.
- Do not make up information.
- Give a clear and concise answer.
"""

    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.message.content