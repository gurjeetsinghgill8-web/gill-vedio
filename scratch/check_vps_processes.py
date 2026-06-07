import paramiko
import sys

ip = "46.224.133.16"
password = "U4CJs4HKbMMJ"
user = "root"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect(ip, username=user, password=password, timeout=10)
    print("SSH Connected successfully.")
    
    print("\n--- Running Python Processes ---")
    _, stdout, stderr = client.exec_command("ps aux | grep python")
    output = stdout.read().decode("utf-8", errors="replace")
    sys.stdout.buffer.write(output.encode(sys.stdout.encoding or 'utf-8', errors='replace'))
    
    client.close()
except Exception as e:
    print(f"Error: {e}")
