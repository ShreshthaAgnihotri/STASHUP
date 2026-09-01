-- ============================================================
-- FINMIND AI DATABASE
-- M1 + M2 + M3 + M4 SUPPORT
-- ============================================================


-- ============================================================
-- DATABASE 1 : VECTOR DATABASE
-- ============================================================

CREATE DATABASE IF NOT EXISTS finmind_vector_db;

USE finmind_vector_db;


-- ============================================================
-- DOCUMENT EMBEDDINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS document_embeddings (

    embedding_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    document_id BIGINT NOT NULL,

    chunk_id BIGINT NOT NULL,

    chunk_text TEXT NOT NULL,

    embedding_model VARCHAR(100) NOT NULL,

    embedding_dimension INT NOT NULL,

    embedding_data LONGTEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unique_chunk (
        document_id,
        chunk_id
    )
);


-- ============================================================
-- VECTOR DATABASE METADATA
-- ============================================================

CREATE TABLE IF NOT EXISTS vector_database_metadata (

    id INT AUTO_INCREMENT PRIMARY KEY,

    database_name VARCHAR(100) NOT NULL,

    embedding_model VARCHAR(100) NOT NULL,

    dimension INT NOT NULL,

    distance_metric VARCHAR(50)
        DEFAULT 'cosine',

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_document_id
ON document_embeddings(document_id);


CREATE INDEX idx_chunk_id
ON document_embeddings(chunk_id);


-- ============================================================
-- VECTOR CONFIGURATION
-- ============================================================

INSERT INTO vector_database_metadata
(
    database_name,
    embedding_model,
    dimension,
    distance_metric
)
SELECT
    'FINMIND Vector Database',
    'all-MiniLM-L6-v2',
    384,
    'cosine'
WHERE NOT EXISTS (

    SELECT 1

    FROM vector_database_metadata

    WHERE database_name =
        'FINMIND Vector Database'

);


-- ============================================================
-- DATABASE 2 : RAG
-- ============================================================

CREATE DATABASE IF NOT EXISTS finmind_rag;

USE finmind_rag;


-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (

    user_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(150),

    risk_profile VARCHAR(50)
        DEFAULT 'MODERATE',

    investment_horizon VARCHAR(50)
        DEFAULT 'MEDIUM',

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- USER BEHAVIOR
-- ============================================================

CREATE TABLE IF NOT EXISTS user_behavior (

    behavior_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    action_type VARCHAR(100),

    symbol VARCHAR(30),

    action_details TEXT,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE

);


CREATE INDEX idx_behavior_user
ON user_behavior(user_id);


-- ============================================================
-- RAG QUERIES
-- ============================================================

CREATE TABLE IF NOT EXISTS rag_queries (

    query_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT,

    query_text TEXT NOT NULL,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL

);


CREATE INDEX idx_rag_user
ON rag_queries(user_id);


-- ============================================================
-- RETRIEVED DOCUMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS rag_retrievals (

    retrieval_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    query_id BIGINT NOT NULL,

    document_id BIGINT NOT NULL,

    chunk_id BIGINT NOT NULL,

    retrieved_text TEXT NOT NULL,

    similarity_score DECIMAL(10,8),

    ranking INT,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (query_id)
        REFERENCES rag_queries(query_id)
        ON DELETE CASCADE

);


CREATE INDEX idx_rag_query
ON rag_retrievals(query_id);


CREATE INDEX idx_rag_document
ON rag_retrievals(document_id);


CREATE INDEX idx_rag_similarity
ON rag_retrievals(similarity_score);


-- ============================================================
-- RAG CONTEXT
-- ============================================================

CREATE TABLE IF NOT EXISTS rag_context (

    context_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    query_id BIGINT NOT NULL,

    context_text LONGTEXT NOT NULL,

    source_count INT
        DEFAULT 0,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (query_id)
        REFERENCES rag_queries(query_id)
        ON DELETE CASCADE

);


-- ============================================================
-- RAG RESPONSES
-- ============================================================

CREATE TABLE IF NOT EXISTS rag_responses (

    response_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    query_id BIGINT NOT NULL,

    response_text LONGTEXT NOT NULL,

    model_name VARCHAR(100),

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (query_id)
        REFERENCES rag_queries(query_id)
        ON DELETE CASCADE

);


-- ============================================================
-- M4 AGENT SESSIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS agent_sessions (

    session_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT,

    symbol VARCHAR(30),

    user_risk_profile VARCHAR(50),

    overall_signal VARCHAR(50),

    confidence DECIMAL(5,2),

    status VARCHAR(30),

    total_latency DECIMAL(10,4),

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL

);


CREATE INDEX idx_session_user
ON agent_sessions(user_id);


CREATE INDEX idx_session_symbol
ON agent_sessions(symbol);


-- ============================================================
-- M4 AGENT OUTPUTS
-- ============================================================

CREATE TABLE IF NOT EXISTS agent_outputs (

    agent_output_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    session_id BIGINT NOT NULL,

    agent_name VARCHAR(100) NOT NULL,

    signal VARCHAR(50),

    confidence DECIMAL(5,2),

    risk_level VARCHAR(30),

    risk_score DECIMAL(5,2),

    reasoning TEXT,

    latency DECIMAL(10,4),

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id)
        REFERENCES agent_sessions(session_id)
        ON DELETE CASCADE

);


CREATE INDEX idx_agent_session
ON agent_outputs(session_id);


CREATE INDEX idx_agent_name
ON agent_outputs(agent_name);


-- ============================================================
-- REASONING TRACE
-- ============================================================

CREATE TABLE IF NOT EXISTS reasoning_trace (

    trace_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    session_id BIGINT NOT NULL,

    step_number INT NOT NULL,

    agent_name VARCHAR(100),

    finding VARCHAR(100),

    reasoning TEXT,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id)
        REFERENCES agent_sessions(session_id)
        ON DELETE CASCADE

);


CREATE INDEX idx_trace_session
ON reasoning_trace(session_id);


-- ============================================================
-- SOURCES / CITATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS agent_sources (

    source_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    session_id BIGINT NOT NULL,

    agent_name VARCHAR(100),

    document_id BIGINT,

    chunk_id BIGINT,

    similarity_score DECIMAL(10,8),

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id)
        REFERENCES agent_sessions(session_id)
        ON DELETE CASCADE

);


CREATE INDEX idx_source_session
ON agent_sources(session_id);


-- ============================================================
-- PERFORMANCE METRICS
-- ============================================================

CREATE TABLE IF NOT EXISTS performance_metrics (

    metric_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    session_id BIGINT NOT NULL,

    signal_accuracy DECIMAL(5,2),

    response_latency DECIMAL(10,4),

    portfolio_risk_score DECIMAL(5,2),

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id)
        REFERENCES agent_sessions(session_id)
        ON DELETE CASCADE

);


CREATE INDEX idx_metrics_session
ON performance_metrics(session_id);


-- ============================================================
-- PORTFOLIO
-- ============================================================

CREATE TABLE IF NOT EXISTS portfolios (

    portfolio_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    symbol VARCHAR(30) NOT NULL,

    quantity DECIMAL(15,4)
        DEFAULT 0,

    average_price DECIMAL(15,2)
        DEFAULT 0,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE

);


CREATE INDEX idx_portfolio_user
ON portfolios(user_id);


CREATE INDEX idx_portfolio_symbol
ON portfolios(symbol);


-- ============================================================
-- WATCHLIST
-- ============================================================

CREATE TABLE IF NOT EXISTS watchlist (

    watchlist_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,

    symbol VARCHAR(30) NOT NULL,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unique_watchlist (
        user_id,
        symbol
    ),

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE

);


-- ============================================================
-- DECISION LOG
-- ============================================================

CREATE TABLE IF NOT EXISTS decision_logs (

    decision_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    session_id BIGINT NOT NULL,

    user_id BIGINT,

    symbol VARCHAR(30),

    decision VARCHAR(100),

    reason TEXT,

    created_at TIMESTAMP
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (session_id)
        REFERENCES agent_sessions(session_id)
        ON DELETE CASCADE,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL

);


-- ============================================================
-- SAMPLE USER
-- ============================================================

INSERT INTO users
(
    name,
    risk_profile,
    investment_horizon
)

SELECT
    'Demo Investor',
    'MODERATE',
    'MEDIUM'

WHERE NOT EXISTS (

    SELECT 1

    FROM users

    WHERE name = 'Demo Investor'

);


-- ============================================================
-- DONE
-- ============================================================

SELECT
    'FINMIND DATABASE READY' AS status;