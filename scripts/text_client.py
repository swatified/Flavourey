import sys
import json
import requests


def main():
    if len(sys.argv) < 3:
        print('Usage: python scripts/text_client.py <session_id> <message>')
        return
    sid = sys.argv[1]
    msg = sys.argv[2]
    url = 'http://127.0.0.1:8000/api/ask'
    payload = {'session_id': sid, 'message': msg}
    r = requests.post(url, json=payload)
    try:
        print('Status:', r.status_code)
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print('Response text:', r.text)


if __name__ == '__main__':
    main()
