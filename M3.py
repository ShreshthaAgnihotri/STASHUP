import os
import re
import math
import mysql.connector

from sentence_transformers import SentenceTransformer


# =====================================================
# CONFIG
# =====================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD"
}


# =====================================================
# EMBEDDING MODEL
# =====================================================

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db():

    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database="finmind_vector_db"
    )


# =====================================================
# TEXT CHUNKING
# =====================================================

def chunk_text(text, chunk_size=500):

    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(
            words[i:i + chunk_size]
        )

        chunks.append(chunk)

    return chunks


# =====================================================
# CREATE EMBEDDING
# =====================================================

def create_embedding(text):

    vector = model.encode(text)

    return vector.tolist()


# =====================================================
# COSINE SIMILARITY
# =====================================================

def cosine_similarity(a, b):

    dot = sum(
        x * y
        for x, y in zip(a, b)
    )

    norm_a = math.sqrt(
        sum(x * x for x in a)
    )

    norm_b = math.sqrt(
        sum(x * x for x in b)
    )

    if norm_a == 0 or norm_b == 0:
        return 0

    return dot / (norm_a * norm_b)


# =====================================================
# STORE DOCUMENT
# =====================================================

def store_document(
    document_id,
    text
):

    chunks = chunk_text(text)

    db = get_db()

    cursor = db.cursor()

    for index, chunk in enumerate(chunks):

        embedding = create_embedding(chunk)

        embedding_string = ",".join(
            str(x)
            for x in embedding
        )

        query = """
        INSERT INTO document_embeddings
        (
            document_id,
            chunk_id,
            chunk_text,
            embedding_model,
            embedding_dimension,
            embedding_data
        )
        VALUES (%s, %s, %s, %s, %s, %s)

        ON DUPLICATE KEY UPDATE
        chunk_text = VALUES(chunk_text),
        embedding_data = VALUES(embedding_data)
        """

        cursor.execute(
            query,
            (
                document_id,
                index,
                chunk,
                MODEL_NAME,
                len(embedding),
                embedding_string
            )
        )

    db.commit()

    cursor.close()
    db.close()


# =====================================================
# LOAD EMBEDDING
# =====================================================

def parse_embedding(data):

    return [
        float(x)
        for x in data.split(",")
    ]


# =====================================================
# RETRIEVE RELEVANT DOCUMENTS
# =====================================================

def retrieve_documents(
    query_text,
    top_k=5
):

    query_embedding = create_embedding(
        query_text
    )

    db = get_db()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            document_id,
            chunk_id,
            chunk_text,
            embedding_data
        FROM document_embeddings
    """)

    rows = cursor.fetchall()

    results = []

    for row in rows:

        document_embedding = parse_embedding(
            row["embedding_data"]
        )

        similarity = cosine_similarity(
            query_embedding,
            document_embedding
        )

        results.append({

            "document_id":
                row["document_id"],

            "chunk_id":
                row["chunk_id"],

            "text":
                row["chunk_text"],

            "similarity":
                similarity
        })


    results.sort(
        key=lambda x: x["similarity"],
        reverse=True
    )

    cursor.close()
    db.close()

    return results[:top_k]


# =====================================================
# BUILD RAG CONTEXT
# =====================================================

def build_context(
    query_text
):

    documents = retrieve_documents(
        query_text
    )

    if not documents:

        return {
            "context": "",
            "sources": []
        }


    context_parts = []

    sources = []


    for result in documents:

        context_parts.append(
            result["text"]
        )

        sources.append({

            "document_id":
                result["document_id"],

            "chunk_id":
                result["chunk_id"],

            "similarity":
                round(
                    result["similarity"],
                    4
                )

        })


    context = "\n\n".join(
        context_parts
    )


    return {

        "context": context,

        "sources": sources

    }


# =====================================================
# RAG ANSWER
# =====================================================

def generate_rag_response(
    question
):

    rag_data = build_context(
        question
    )

    context = rag_data["context"]

    sources = rag_data["sources"]


    if not context:

        return {

            "answer":
                "No relevant filing or document was found.",

            "sources": [],

            "grounded": False

        }


    # -------------------------------------------------
    # DEMO RESPONSE
    # -------------------------------------------------

    answer = (
        "Relevant financial information was found "
        "from the available document corpus. "
        "The retrieved evidence should be reviewed "
        "before making an investment decision."
    )


    return {

        "answer": answer,

        "context": context,

        "sources": sources,

        "grounded": True

    }