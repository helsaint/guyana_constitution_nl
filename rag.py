import duckdb
import streamlit as st
import hashlib

from config import (
    client,
    db_url,
    OPENAI_MODEL,
    EMBEDDING_MODEL,
    TOP_K_CHUNKS,
)

@st.cache_resource
def get_db_connection():
    conn = duckdb.connect(
        db_url,
        read_only=False
    )
    cursor = conn.cursor()
    return cursor

# If question doesn't exist add it
def _update_answer_table(question_embeddings: list,
                         answer: str,
                         results: list,
                         best_score: float):
    results_list = []
    for r in results:
        results_list.append({'i': r[0], 't': r[1], 'f': r[2]})

    str_embedding = str(question_embeddings)
    primary_key = hashlib.sha256(str_embedding.encode()).hexdigest()
    cursor =  get_db_connection()
    cursor.execute("""
                  INSERT INTO answers (
                   embeddings_hash, 
                   question_embeddings, 
                   answer, 
                   hit_count, 
                   best_score, 
                   results
                   ) VALUES (?, ?, ?, ?, ?, ?::STRUCT(i INTEGER, t VARCHAR, f FLOAT)[])
                  """, [primary_key, question_embeddings,
                        answer, 1, best_score, results_list])


# If question exists update counter
def _update_answer_counter(question_embeddings: list):
    str_embedding = str(question_embeddings)
    primary_key = hashlib.sha256(str_embedding.encode()).hexdigest()
    cursor =  get_db_connection()
    cursor.execute("""
                   UPDATE answers 
                   SET hit_count = hit_count + 1,
                   updated_on = NOW()
                   WHERE embeddings_hash = ?
                   """, [primary_key])

# Checks the database to see if an answer to this question was already created
def _check_for_answer(question_embeddings: list, 
                      cursor: duckdb.DuckDBPyConnection):
    old_answer = cursor.execute("""
                             SELECT
                             embeddings_hash,
                             question_embeddings,
                             answer,
                             hit_count,
                             best_score,
                             results,
                             array_cosine_similarity(question_embeddings, ?::FLOAT[1536]) AS score
                             FROM answers
                             ORDER BY score DESC
                             LIMIT 1
                             """, [question_embeddings]).fetchall()
    
    
    # Only happens first time
    if not(old_answer):
        return []
    elif old_answer[0][6] > 0.95:
        return [old_answer[0][2], old_answer[0][4], old_answer[0][5]] 
    else:
        return []

def embed(text: str) -> list[float]:
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding

def retrieve_chunks(question: str):
    question_embeddings = embed(question)
    local_cursor = get_db_connection()

    results = _check_for_answer(question_embeddings, local_cursor)
    if results:
        return (results, question_embeddings, True)
    else:
        results = local_cursor.execute("""
                                       SELECT
                                       id,
                                       text,
                                       array_cosine_similarity(embeddings, ?::FLOAT[1536]) AS score
                                       FROM sections
                                       ORDER BY score DESC
                                       LIMIT 5
                                       """, [question_embeddings]).fetchall()

    return (results, question_embeddings, False)

def build_context(results: list):
    
    context = "\n\n".join(
        [
            f"Source {i+1}:\n{row[1]}"
            for i, row in enumerate(results)
            ]
            )
    
    return context

system_prompt = """
You are answering questions about the constitution of Guyana.

Use ONLY the supplied context.

If the answer cannot be found in the context,
say that the information is not available.

Do not invent facts.
Do not use outside knowledge.

When possible, cite the source numbers.
"""

def generate_answer(question:str, context: str):
    user_prompt = f"""
    Question:
    {question}
    Context:
    {context}
    """

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
            ]
            )
    answer = response.choices[0].message.content
    return answer

def answer_question(question: str):
    results_res_exist = retrieve_chunks(question)
    results = results_res_exist[0]
    question_embeddings = results_res_exist[1]
    res_exist = results_res_exist[2]
    
    if not(res_exist):
        best_score = results[0][2]
        if best_score < 0.45:
            return {
                "answer": "I couldn't find relevant information in the document",
                "sources": [],
                "score": best_score
            }
    
        context = build_context(results)
        answer = generate_answer(question, context)
        _update_answer_table(question_embeddings=question_embeddings, 
                             answer=answer, results=results,
                             best_score=best_score)
        
    else:
        _update_answer_counter(question_embeddings=question_embeddings)
        answer = results[0]
        best_score = results[1]
        sources = results[2]
        return {"answer": answer, "sources": sources, "score": best_score}
        
    return {"answer": answer, "sources": results, "score": best_score}

