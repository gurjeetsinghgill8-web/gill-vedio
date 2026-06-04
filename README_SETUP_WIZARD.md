# GILL VEDIO — Quick Setup Wizard (non-technical)

## 0) Start the dashboard (double-click)
- Run: **run_app.bat** (double click)
- A browser tab will open with the dashboard.

## 1) Unlock / initialize vault
- Open **Settings**
- If vault not created: open **Dashboard first** and click **Initialize Vault**
- Enter a **Master Password** (remember it)

## 2) Add API keys (required)
Go to **Settings → API Keys** and add these keys:
1. **google_veo** — used to generate videos
2. **groq** — used for generating 10 viral ideas
3. **gemini** — fallback for ideas/prompts
4. **nvidia** — fallback for quick tasks

Paste each key in the field and click **Save ... key**.

## 3) Add your profile (helps personalization)
In **Settings → Profile** fill:
- Name
- Niche (topic area)
- About me
- Style preference
Click **Save Profile**.

## 4) Create videos
1. Go to **Dashboard**
2. Type your topic (example: “5 Morning Habits for Success”)
3. Click **Generate 10 Viral Ideas**
4. Select 2-10 ideas using the checkboxes
5. Click **Generate Videos for Selected Ideas**

What you will see:
- Video jobs will be stored in the database
- The UI will show job ids

## 5) Social media posting
Right now publishing is **safe stubbed** (no real posting) because each platform requires OAuth/business verification.

Supported platforms (placeholder):
- instagram
- facebook
- whatsapp
- youtube
- twitter

To make posting real, you must wire OAuth for each platform and then replace the stub publishers.

---
## Troubleshooting
### Streamlit doesn’t open
- Install Python 3.11+
- Ensure you can run `python --version`
- Double-click `run_app.bat` again.

### Veo fails
- Your Veo endpoint/schema in `models/veo_client.py` may need to be updated to your exact API.
- Send me the Veo API endpoint text you use (from your docs page), and I’ll patch it.

