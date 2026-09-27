import sqlite3
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.core.config import settings, DATA_DIR

logger = logging.getLogger("factcheck.database")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Claims Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_claims (
        id TEXT PRIMARY KEY,
        raw_input TEXT,
        claim_text TEXT NOT NULL,
        verdict TEXT NOT NULL,
        confidence REAL NOT NULL,
        summary TEXT NOT NULL,
        category TEXT,
        topic TEXT,
        supporting_evidence TEXT,
        contradicting_evidence TEXT,
        sources TEXT,
        critic_reflections TEXT,
        reflection_rounds INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)
    
    # 2. Digests Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_digests (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        topic TEXT NOT NULL,
        date_str TEXT NOT NULL,
        claim_count INTEGER NOT NULL,
        claim_ids TEXT,
        markdown_content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # 3. Trusted Sources Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trusted_sources (
        domain TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        credibility_score REAL NOT NULL,
        bias_rating TEXT NOT NULL,
        category TEXT NOT NULL,
        notes TEXT
    )
    """)
    
    # 4. Evaluation Runs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eval_runs (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        total_claims INTEGER NOT NULL,
        correct_count INTEGER NOT NULL,
        accuracy REAL NOT NULL,
        unverifiable_adherence REAL NOT NULL,
        results_json TEXT NOT NULL
    )
    """)
    
    conn.commit()
    
    # Seed trusted sources if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM trusted_sources")
    if cursor.fetchone()["cnt"] == 0:
        seed_trusted_sources(cursor)
        conn.commit()
        
    # Seed initial fact checks if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM saved_claims")
    if cursor.fetchone()["cnt"] == 0:
        seed_initial_claims(cursor)
        conn.commit()

    conn.close()
    logger.info("Database initialized successfully.")

def seed_trusted_sources(cursor: sqlite3.Cursor):
    sources_file = DATA_DIR / "trusted_sources.json"
    if sources_file.exists():
        with open(sources_file, "r", encoding="utf-8") as f:
            sources = json.load(f)
            for s in sources:
                cursor.execute("""
                INSERT OR REPLACE INTO trusted_sources (domain, name, credibility_score, bias_rating, category, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (s["domain"], s["name"], s["credibility_score"], s["bias_rating"], s["category"], s.get("notes", "")))
        logger.info(f"Seeded {len(sources)} trusted sources into database.")

def seed_initial_claims(cursor: sqlite3.Cursor):
    seed_file = DATA_DIR / "seed_fact_checks.json"
    if seed_file.exists():
        with open(seed_file, "r", encoding="utf-8") as f:
            claims = json.load(f)
            for c in claims:
                cursor.execute("""
                INSERT OR REPLACE INTO saved_claims 
                (id, raw_input, claim_text, verdict, confidence, summary, category, topic, 
                 supporting_evidence, contradicting_evidence, sources, critic_reflections, reflection_rounds, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    c["id"],
                    c.get("raw_input", c["claim_text"]),
                    c["claim_text"],
                    c["verdict"],
                    c["confidence"],
                    c["summary"],
                    c.get("category", "General"),
                    c.get("topic", "General"),
                    json.dumps(c.get("supporting_evidence", [])),
                    json.dumps(c.get("contradicting_evidence", [])),
                    json.dumps(c.get("sources", [])),
                    json.dumps([]),
                    0,
                    c.get("created_at", datetime.utcnow().isoformat() + "Z")
                ))
        logger.info(f"Seeded {len(claims)} verified claims into database.")
