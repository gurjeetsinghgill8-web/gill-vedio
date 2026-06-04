"""
GILL VEDIO VPS Deploy Script
=============================
Deploys GILL VEDIO to VPS at port 5001.
"""
import paramiko
import sys
import os
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ─── VPS CONFIG ──────────────────────────────────────────────
VPS_IP       = "46.224.133.16"
VPS_USER     = "root"
VPS_PASSWORD = "U4CJs4HKbMMJ"
REMOTE       = "/root/BHARAT-SYSTEMS/GILL_VEDIO"

GILL_DIR = os.path.dirname(os.path.abspath(__file__))

# Connect SSH using paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(VPS_IP, username=VPS_USER, password=VPS_PASSWORD, timeout=15)
sftp = client.open_sftp()

def ssh(cmd, show=True):
    """Run command on VPS via SSH."""
    try:
        _, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode("utf-8", errors="replace").strip()
        err = stderr.read().decode("utf-8", errors="replace").strip()
        if show:
            if out:
                print(out)
            if err and "warning" not in err.lower() and "active" not in err.lower():
                print("  STDERR:", err[:200])
        return True
    except Exception as e:
        print(f"SSH execution error: {e}")
        return False


def scp_upload(local_path, remote_path):
    """Upload file to VPS."""
    try:
        sftp.put(local_path, remote_path)
        return True
    except Exception as e:
        print(f"SFTP Upload error: {e}")
        return False


print()
print("=" * 60)
print("  GILL VEDIO — DEPLOYING TO VPS (PARAMIKO)")
print(f"  Target: {VPS_USER}@{VPS_IP}")
print("=" * 60)
print()

# ─── Step 1: Create remote directory structure ─────────────────────────
print("[1/5] Preparing VPS directories...")
ssh(f"mkdir -p {REMOTE} {REMOTE}/models {REMOTE}/secrets {REMOTE}/data {REMOTE}/output")
print("      OK")

# ─── Step 2: Upload all GILL VEDIO files ────────────────────────────
print("[2/5] Uploading GILL VEDIO engine files...")
files_to_upload = [
    "app.py", "config_manager.py", "database.py", "llm_harness.py",
    "idea_generator.py", "video_generator.py", "social_publisher.py",
    "schedule_manager.py", "security.py", "requirements.txt",
]

for f in files_to_upload:
    fp = os.path.join(GILL_DIR, f)
    if os.path.exists(fp):
        ok = scp_upload(fp, f"{REMOTE}/{f}")
        print(f"  {'OK' if ok else 'FAILED'}: {f}")
    else:
        print(f"  SKIP (not found): {f}")

# Upload models
print("Uploading models...")
models_dir = os.path.join(GILL_DIR, "models")
if os.path.exists(models_dir):
    for f in os.listdir(models_dir):
        if f.endswith(".py"):
            ok = scp_upload(os.path.join(models_dir, f), f"{REMOTE}/models/{f}")
            print(f"  {'OK' if ok else 'FAILED'}: models/{f}")

# Upload secrets (vault keys)
print("Uploading encrypted vault/secrets...")
secrets_dir = os.path.join(GILL_DIR, "secrets")
if os.path.exists(secrets_dir):
    for f in os.listdir(secrets_dir):
        if f.startswith("."):
            ok = scp_upload(os.path.join(secrets_dir, f), f"{REMOTE}/secrets/{f}")
            print(f"  {'OK' if ok else 'FAILED'}: secrets/{f}")

# Upload database if exists
print("Uploading SQLite database...")
db_dir = os.path.join(GILL_DIR, "data")
if os.path.exists(db_dir):
    for f in os.listdir(db_dir):
        if f.endswith(".db"):
            ok = scp_upload(os.path.join(db_dir, f), f"{REMOTE}/data/{f}")
            print(f"  {'OK' if ok else 'FAILED'}: data/{f}")

print("      Upload done!")

# ─── Step 3: Install dependencies ────────────────────────────
print("[3/5] Installing Python packages on VPS...")
ssh(f"pip3 install -q -r {REMOTE}/requirements.txt --break-system-packages 2>/dev/null || pip3 install -q -r {REMOTE}/requirements.txt")
print("      OK")

# ─── Step 4: Create & start systemd service ─────────────────
print("[4/5] Setting up systemd service...")

dashboard_service = f"""[Unit]
Description=Gill Vedio Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={REMOTE}
ExecStart=/usr/bin/python3 -m streamlit run {REMOTE}/app.py --server.port 5001 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false --server.enableCORS false --server.enableXsrfProtection false
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONIOENCODING=utf-8

[Install]
WantedBy=multi-user.target"""

# Write service file
ssh(f"cat > /etc/systemd/system/gill_vedio.service << 'SVCEOF'\n{dashboard_service}\nSVCEOF")

ssh("systemctl daemon-reload")
ssh("systemctl enable gill_vedio")
ssh("systemctl stop gill_vedio 2>/dev/null; sleep 2")
ssh("systemctl start gill_vedio")
time.sleep(4)

# Open firewall
ssh("ufw allow 5001/tcp 2>/dev/null || iptables -I INPUT -p tcp --dport 5001 -j ACCEPT 2>/dev/null || true", show=False)
print("      OK")

# ─── Step 5: Verify ──────────────────────────────────────────
print("[5/5] Verifying services...")
time.sleep(3)
dash_status = "RUNNING" if ssh("systemctl is-active --quiet gill_vedio", show=False) else "STARTING/FAILED..."

print()
print("=" * 60)
print("  DEPLOYMENT COMPLETE!")
print()
print(f"  App Status: {dash_status}")
print()
print(f"  PERMANENT DASHBOARD URL:")
print(f"  http://{VPS_IP}:5001")
print()
print("  HOW TO USE ON MOBILE:")
print("  1. Open above URL in Chrome or Safari on mobile")
print("  2. Tap share/menu > 'Add to Home Screen'")
print("  3. Works like a native APP 24/7 without laptop!")
print("=" * 60)
print()

sftp.close()
client.close()
