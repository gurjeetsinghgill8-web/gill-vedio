# GILL VEDIO — Deploy to Streamlit Community Cloud (for Android use)

## Goal
Run the app on the cloud so you can use it from **Android** without keeping laptop ON.

## Important limits (read)
- Your app uses **Google Veo**. Veo still needs your `google_veo` API key.
- On free cloud tiers, long video generation can be slow or time out. Start with **ideas first**.

---

## Step A — Create a GitHub repo (required by Streamlit Cloud)
1. Sign in to **GitHub**.
2. Create a new repo (name it like `gill-vedio`).
3. Upload these files from this folder:
   - `app.py`
   - `requirements.txt`
   - `models/*`
   - `database.py`, `config_manager.py`, `security.py`
   - plus any other `.py` files in this folder
   - include folders: `models/`, `data/` (if exists), `secrets/` (if exists)

> If you don’t want to upload your secrets (API keys), that’s OK. The app stores keys in the encrypted vault via your master password.

---

## Step B — Deploy on Streamlit Community Cloud
1. Go to: https://streamlit.io/cloud
2. Click **Deploy an app**.
3. Choose **GitHub** and select your repo.
4. Streamlit should detect `app.py`.
5. If it asks, set:
   - **Main file**: `app.py`
   - **Python version**: 3.11 (recommended)
6. Click **Deploy**.

After deploy, Streamlit Cloud gives a URL like:
`https://<your-app-name>.streamlit.app`

## Step B-1 — Make sure database works on cloud
This app uses `data/gill_vedio.db` (SQLite) stored inside the project folder.
- If Streamlit Cloud restarts and data resets, we must enable a persistent storage option.
- Many free plans may reset storage.

If you see data lost after redeploy/restart, tell me and I will patch code to store DB in a cloud-persistent directory (or use a simple remote DB option).

---

## Step C — Use on Android
1. Open the URL in Chrome on Android.
2. If you want “app-like” icon:
   - Menu (⋮) → **Add to Home screen**
3. Unlock vault in **Settings** and add API keys.

---

## Step D — If Veo fails
Your `models/veo_client.py` has placeholder endpoints.
- If Veo API fails, the error will show in logs.
- Send me the exact Veo endpoint from your docs so we can patch `models/veo_client.py`.

