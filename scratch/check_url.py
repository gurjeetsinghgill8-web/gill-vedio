import requests

urls = [
    "https://gill-vedio.streamlit.app",
    "https://gillvedio.streamlit.app",
]

for url in urls:
    try:
        r = requests.head(url, timeout=5)
        print(f"{url} -> status {r.status_code}")
    except Exception as e:
        print(f"{url} -> error: {e}")
