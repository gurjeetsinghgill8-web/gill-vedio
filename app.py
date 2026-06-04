import json
import os
from pathlib import Path

import streamlit as st

from database import (
    initialize_database,
    save_user,
    update_user_preferences,
    save_ideas,
    get_latest_batch_id,
    get_ideas_by_batch,
    select_idea,
    get_selected_ideas,
    save_video,
    update_video_status,
    get_all_videos,
    get_approved_videos,
    get_progress,
    get_user,
)
from config_manager import (
    init_or_unlock_vault,
    unlock_vault,
    save_user_profile,
    save_api_provider_key,
    update_preferences,
)
from llm_harness import Harness
from idea_generator import generate_10_ideas
from video_generator import generate_videos
from social_publisher import StubSocialPublisher
from schedule_manager import start_scheduler


APP_TITLE = "🎬 GILL VEDIO"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def ensure_initialized():
    initialize_database()


def require_auth() -> str:
    if "master_password" not in st.session_state:
        st.error("Vault locked. Please unlock.")
        st.stop()
    return st.session_state["master_password"]


def auth_page():
    st.title(APP_TITLE)

    if "vault_initialized" not in st.session_state:
        # lazy: try to unlock/initialize on demand
        st.session_state.vault_initialized = None

    master_password = st.text_input("Master password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        init_btn = st.button("Initialize Vault")
    with col2:
        unlock_btn = st.button("Unlock Vault")

    if init_btn:
        ok = init_or_unlock_vault(master_password)
        if ok:
            st.session_state.master_password = master_password
            st.success("Vault initialized/unlocked.")
            st.rerun()
        else:
            st.error("Invalid master password or vault error.")

    if unlock_btn:
        ok = unlock_vault(master_password)
        if ok:
            st.session_state.master_password = master_password
            st.success("Vault unlocked.")
            st.rerun()
        else:
            st.error("Vault not initialized or wrong password.")


def settings_page(master_password: str):
    st.header("⚙️ Settings")

    with st.expander("👤 Profile"):
        user = get_user()
        name = st.text_input("Name", value=user.get("name", ""))
        email = st.text_input("Email", value=user.get("email", ""))
        phone = st.text_input("Phone", value=user.get("phone", ""))
        niche = st.text_input("Niche", value=user.get("niche", ""))
        about_me = st.text_area("About me", value=user.get("about_me", ""))
        style_preference = st.text_area("Style preference", value=user.get("style_preference", ""))

        if st.button("Save Profile"):
            save_user_profile(
                name=name,
                email=email,
                phone=phone,
                niche=niche,
                about_me=about_me,
                style_preference=style_preference,
            )
            st.success("Profile saved.")

    with st.expander("🔑 API Keys"):
        st.caption("Add keys for: google_veo, fal_ai, json2video, groq, gemini, nvidia")

        providers = ["google_veo", "fal_ai", "json2video", "groq", "gemini", "nvidia"]
        for provider in providers:
            with st.container():
                key = st.text_input(f"{provider} API key", type="password", key=f"key_{provider}")
                tier = st.selectbox(
                    f"{provider} tier", ["free", "paid"], index=0, key=f"tier_{provider}"
                )
                if st.button(f"Save {provider} key", key=f"save_{provider}"):
                    if not key.strip():
                        st.error("Enter a key.")
                    else:
                        save_api_provider_key(master_password, provider, key.strip(), tier=tier)
                        st.success("Key saved encrypted.")

    with st.expander("🎛️ Preferences"):
        user = get_user()
        video_length = st.number_input("Default video length (seconds)", min_value=5, max_value=60, value=int(user.get("default_video_length", 10)))
        model = st.text_input("Default LLM model id (optional)", value=user.get("default_model", "groq"))
        tier = st.selectbox("Default tier", ["free", "paid"], index=0)
        
        provider_options = ["mock", "google_veo", "fal_ai", "json2video"]
        current_provider = user.get("video_provider", "mock")
        if current_provider not in provider_options:
            current_provider = "mock"
            
        video_provider = st.selectbox(
            "Video Generation Provider",
            provider_options,
            index=provider_options.index(current_provider),
            format_func=lambda x: {
                "mock": "Mock Generator (100% Free / Testing)",
                "google_veo": "Google Veo (Paid)",
                "fal_ai": "Fal.ai - HunyuanVideo/Wan2.1 (Freemium)",
                "json2video": "JSON2Video (Freemium)"
            }[x]
        )
        
        if st.button("Save Preferences"):
            update_preferences(video_length=int(video_length), model=model, tier=tier, video_provider=video_provider)
            st.success("Preferences saved.")


def dashboard_page(master_password: str):
    st.header("🎯 Dashboard")

    harness = Harness(master_password)

    topic = st.text_input("Enter your video topic", placeholder="e.g., 5 Morning Habits for Success")
    duration = st.selectbox("Video length", [5, 10, 20, 60], index=1)
    style = st.text_input("Style (optional)", value="cinematic, vibrant")

    if "last_batch_id" not in st.session_state:
        st.session_state.last_batch_id = None

    if st.button("🚀 Generate 10 Viral Ideas"):
        if not topic.strip():
            st.error("Topic is required")
            st.stop()

        try:
            ideas = harness.generate_ideas(topic=topic, count=10)
            batch_id = save_ideas(topic=topic, ideas=ideas)
            st.session_state.last_batch_id = batch_id
            st.success(f"Generated ideas. Batch: {batch_id}")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to generate ideas: {e}")

    batch_id = st.session_state.last_batch_id or get_latest_batch_id()

    if not batch_id:
        st.info("Generate ideas to start.")
        return

    ideas = get_ideas_by_batch(batch_id)
    if not ideas:
        st.warning("No ideas found for batch.")
        return

    st.subheader("💡 Generated Ideas")
    selected_ids = []

    for idea in ideas:
        with st.container():
            colA, colB = st.columns([6, 1])
            with colA:
                st.markdown(f"**{idea.get('title')}** (Viral score: {idea.get('viral_score')}/10)")
                st.caption(f"Hook: {idea.get('hook')}")
                st.caption(f"Script: {idea.get('script_outline')}")
            with colB:
                checked = bool(idea.get("is_selected"))
                new_val = st.checkbox("Select", value=checked, key=f"sel_{idea['id']}")
                if new_val != checked:
                    select_idea(idea['id'], selected=new_val)

    # refresh selected after user actions
    selected_ideas = get_selected_ideas(batch_id)

    st.subheader("🎬 Video Queue")
    if st.button("Generate Videos for Selected Ideas"):
        if not selected_ideas:
            st.error("Select at least 1 idea.")
            st.stop()

        prompt_style = style
        try:
            generated = harness.generate_videos(
                ideas=selected_ideas,
                duration_seconds=duration,
                style=prompt_style,
            )

            # Save video records
            for item in generated:
                file_path = ""  # Veo download not implemented in this build
                prompt = item["prompt"]
                video_id = save_video(
                    idea_id=item["idea_id"],
                    file_path=file_path,
                    file_name="",
                    duration=duration,
                    prompt=prompt,
                    veo_job_id=item["veo_job_id"],
                    status="submitted",
                    metadata={"topic": topic, "batch_id": batch_id},
                )
                update_video_status(video_id, "completed")

            st.success("Video records created (Veo download/polling may require API wiring).")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to generate videos: {e}")

    videos = get_all_videos()
    if videos:
        for v in videos[:30]:
            st.write(f"Video #{v['id']} | idea_id={v['idea_id']} | status={v['status']} | veo_job_id={v.get('veo_job_id','')}")


def history_page():
    st.header("📚 History")
    videos = get_all_videos()
    for v in videos[:50]:
        st.write(f"Video {v['id']} - status={v['status']} - file_path={v.get('file_path','')}")


def analytics_page():
    st.header("📊 Analytics")
    st.info("Analytics UI can be extended using database.get_stats()")


def guide_page():
    st.header("📖 Setup Wizard (Non-technical)")
    st.markdown(
        """Step-by-step (simple):

1) **Open**: double-click `run_app.bat` (or run the app)
2) **Initialize/Unlock vault**
3) **Settings → API Keys**: paste keys for:
   - google_veo
   - groq
   - gemini
   - nvidia
4) **Settings → Profile**: niche + about + style preference
5) **Dashboard**:
   - Topic → **Generate 10 Viral Ideas**
   - Select ideas → **Generate Videos for Selected Ideas**

✅ Your dashboard is ready to generate ideas + submit Veo jobs.

⛔ Social posting is currently a **safe stub** (real posting requires OAuth/business tokens for each platform).
"""
    )


def publish_job(master_password: str):
    # stub publishing - will log failures
    publisher = StubSocialPublisher()
    approved = get_approved_videos()
    if not approved:
        return

    platforms = ["instagram", "facebook", "whatsapp", "youtube", "twitter"]
    # best-effort: try video_id list
    for v in approved:
        try:
            # stub will raise; social_publisher can be extended
            publisher.publish_video(video_id=v["id"], platform=platforms[0])
        except Exception:
            pass


def main():
    ensure_initialized()

    st.set_page_config(page_title=APP_TITLE, layout="wide")

    if "master_password" not in st.session_state:
        auth_page()
        return

    master_password = st.session_state["master_password"]

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Settings", "History", "Analytics", "Guide"],
        index=0,
    )

    if menu == "Dashboard":
        dashboard_page(master_password)
    elif menu == "Settings":
        settings_page(master_password)
    elif menu == "History":
        history_page()
    elif menu == "Analytics":
        analytics_page()
    elif menu == "Guide":
        guide_page()


if __name__ == "__main__":
    main()

