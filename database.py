"""
GILL VEDIO - Database Module
SQLite-based storage for users, ideas, videos, publish logs, and chat history.
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "gill_vedio.db"


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection():
    """Get a database connection."""
    _ensure_data_dir()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def initialize_database():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            niche TEXT,
            about_me TEXT,
            style_preference TEXT,
            avatar_path TEXT,
            default_video_length INTEGER DEFAULT 10,
            default_model TEXT DEFAULT 'groq',
            default_tier TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            title TEXT NOT NULL,
            hook TEXT,
            script_outline TEXT,
            viral_score INTEGER DEFAULT 5,
            hashtags TEXT,
            is_selected INTEGER DEFAULT 0,
            batch_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER REFERENCES ideas(id),
            file_path TEXT,
            file_name TEXT,
            duration_seconds INTEGER,
            prompt_used TEXT,
            veo_job_id TEXT,
            status TEXT DEFAULT 'pending',
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS publish_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER REFERENCES videos(id),
            platform TEXT NOT NULL,
            status TEXT DEFAULT 'scheduled',
            scheduled_at TIMESTAMP,
            published_at TIMESTAMP,
            post_url TEXT,
            caption TEXT,
            hashtags TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            context_type TEXT DEFAULT 'general',
            model_used TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER REFERENCES videos(id),
            platforms TEXT,
            interval_hours REAL DEFAULT 3.0,
            is_active INTEGER DEFAULT 1,
            next_run TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()
    logger.info("Database initialized successfully.")


# ============ USER OPERATIONS ============

def save_user(name: str, email: str = "", phone: str = "", niche: str = "",
              about_me: str = "", style_preference: str = "", avatar_path: str = "") -> int:
    """Save or update user profile. Returns user ID."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT id FROM users LIMIT 1")
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE users SET name=?, email=?, phone=?, niche=?, about_me=?,
            style_preference=?, avatar_path=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (name, email, phone, niche, about_me, style_preference, avatar_path, existing['id']))
        user_id = existing['id']
    else:
        cursor.execute("""
            INSERT INTO users (name, email, phone, niche, about_me, style_preference, avatar_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, niche, about_me, style_preference, avatar_path))
        user_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return user_id


def get_user() -> dict:
    """Get the current user profile."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {}


def update_user_preferences(video_length: int = None, model: str = None, tier: str = None):
    """Update user preferences."""
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if video_length is not None:
        updates.append("default_video_length=?")
        params.append(video_length)
    if model is not None:
        updates.append("default_model=?")
        params.append(model)
    if tier is not None:
        updates.append("default_tier=?")
        params.append(tier)
    if updates:
        updates.append("updated_at=CURRENT_TIMESTAMP")
        cursor.execute(f"UPDATE users SET {', '.join(updates)}", params)
        conn.commit()
    conn.close()


# ============ IDEAS OPERATIONS ============

def save_ideas(topic: str, ideas: list, batch_id: str = None):
    """
    Save a batch of generated ideas.
    ideas: list of dicts with keys: title, hook, script_outline, viral_score, hashtags
    """
    conn = get_connection()
    cursor = conn.cursor()
    if not batch_id:
        batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    for idea in ideas:
        cursor.execute("""
            INSERT INTO ideas (topic, title, hook, script_outline, viral_score, hashtags, batch_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            topic,
            idea.get("title", ""),
            idea.get("hook", ""),
            idea.get("script_outline", ""),
            idea.get("viral_score", 5),
            json.dumps(idea.get("hashtags", [])),
            batch_id
        ))

    conn.commit()
    conn.close()
    return batch_id


def get_ideas_by_batch(batch_id: str) -> list:
    """Get all ideas for a batch."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ideas WHERE batch_id=? ORDER BY viral_score DESC", (batch_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_latest_batch_id() -> str:
    """Get the most recent batch ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT batch_id FROM ideas ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row['batch_id'] if row else None


def select_idea(idea_id: int, selected: bool = True):
    """Mark an idea as selected for video generation."""
    conn = get_connection()
    conn.execute("UPDATE ideas SET is_selected=? WHERE id=?", (1 if selected else 0, idea_id))
    conn.commit()
    conn.close()


def get_selected_ideas(batch_id: str) -> list:
    """Get all selected ideas from a batch."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ideas WHERE batch_id=? AND is_selected=1", (batch_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# ============ VIDEO OPERATIONS ============

def save_video(idea_id: int, file_path: str = "", file_name: str = "",
               duration: int = 10, prompt: str = "", veo_job_id: str = "",
               status: str = "pending", metadata: dict = None) -> int:
    """Save a video record. Returns video ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO videos (idea_id, file_path, file_name, duration_seconds, prompt_used, veo_job_id, status, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (idea_id, file_path, file_name, duration, prompt, veo_job_id, status, json.dumps(metadata or {})))
    video_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return video_id


def update_video_status(video_id: int, status: str, file_path: str = None, veo_job_id: str = None):
    """Update video status (pending/generating/completed/approved/published)."""
    conn = get_connection()
    updates = ["status=?", "updated_at=CURRENT_TIMESTAMP"]
    params = [status]
    if file_path:
        updates.append("file_path=?")
        params.append(file_path)
    if veo_job_id:
        updates.append("veo_job_id=?")
        params.append(veo_job_id)
    params.append(video_id)
    conn.execute(f"UPDATE videos SET {', '.join(updates)} WHERE id=?", params)
    conn.commit()
    conn.close()


def get_video(video_id: int) -> dict:
    """Get a single video record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos WHERE id=?", (video_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}


def get_all_videos(status: str = None) -> list:
    """Get all videos, optionally filtered by status."""
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM videos WHERE status=? ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM videos ORDER BY created_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_approved_videos() -> list:
    """Get all approved videos ready for publishing."""
    return get_all_videos(status="approved")


# ============ PUBLISH LOG OPERATIONS ============

def save_publish_log(video_id: int, platform: str, status: str = "scheduled",
                     scheduled_at: str = None, caption: str = "", hashtags: str = "") -> int:
    """Create a publish log entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO publish_log (video_id, platform, status, scheduled_at, caption, hashtags)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (video_id, platform, status, scheduled_at, caption, hashtags))
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def update_publish_log(log_id: int, status: str, published_at: str = None,
                       post_url: str = None, error_message: str = None):
    """Update publish log status."""
    conn = get_connection()
    updates = ["status=?"]
    params = [status]
    if published_at:
        updates.append("published_at=?")
        params.append(published_at)
    if post_url:
        updates.append("post_url=?")
        params.append(post_url)
    if error_message:
        updates.append("error_message=?")
        params.append(error_message)
    params.append(log_id)
    conn.execute(f"UPDATE publish_log SET {', '.join(updates)} WHERE id=?", params)
    conn.commit()
    conn.close()


def get_publish_logs(video_id: int = None) -> list:
    """Get publish logs, optionally for a specific video."""
    conn = get_connection()
    cursor = conn.cursor()
    if video_id:
        cursor.execute("SELECT * FROM publish_log WHERE video_id=? ORDER BY created_at DESC", (video_id,))
    else:
        cursor.execute("SELECT * FROM publish_log ORDER BY created_at DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# ============ CHAT HISTORY ============

def save_message(role: str, content: str, context_type: str = "general", model_used: str = ""):
    """Save a chat message."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO chat_history (role, content, context_type, model_used)
        VALUES (?, ?, ?, ?)
    """, (role, content, context_type, model_used))
    conn.commit()
    conn.close()


def get_chat_history(context_type: str = None, limit: int = 50) -> list:
    """Get chat history."""
    conn = get_connection()
    cursor = conn.cursor()
    if context_type:
        cursor.execute("SELECT * FROM chat_history WHERE context_type=? ORDER BY created_at DESC LIMIT ?",
                       (context_type, limit))
    else:
        cursor.execute("SELECT * FROM chat_history ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# ============ USER PROGRESS ============

def save_progress(step: str, status: str = "pending", data: dict = None):
    """Save user progress for a step."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user_progress WHERE step=?", (step,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
            UPDATE user_progress SET status=?, data=?, updated_at=CURRENT_TIMESTAMP WHERE step=?
        """, (status, json.dumps(data or {}), step))
    else:
        cursor.execute("""
            INSERT INTO user_progress (step, status, data) VALUES (?, ?, ?)
        """, (step, status, json.dumps(data or {})))
    conn.commit()
    conn.close()


def get_progress(step: str) -> dict:
    """Get progress for a specific step."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_progress WHERE step=?", (step,))
    row = cursor.fetchone()
    conn.close()
    if row:
        result = dict(row)
        if result.get('data'):
            result['data'] = json.loads(result['data'])
        return result
    return {}


def get_all_progress() -> dict:
    """Get all progress entries."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_progress ORDER BY created_at")
    rows = cursor.fetchall()
    conn.close()
    result = {}
    for row in rows:
        d = dict(row)
        if d.get('data'):
            d['data'] = json.loads(d['data'])
        result[d['step']] = d
    return result


# ============ STATS ============

def get_stats() -> dict:
    """Get overall statistics."""
    conn = get_connection()
    cursor = conn.cursor()
    stats = {}

    cursor.execute("SELECT COUNT(*) as count FROM ideas")
    stats['total_ideas'] = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM videos")
    stats['total_videos'] = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM videos WHERE status='published'")
    stats['published_videos'] = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM publish_log WHERE status='published'")
    stats['total_posts'] = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(DISTINCT platform) as count FROM publish_log WHERE status='published'")
    stats['active_platforms'] = cursor.fetchone()['count']

    conn.close()
    return stats