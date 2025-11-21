import json
import traceback
import sys

# Attempt to import the real FastAPI app
try:
    from api import main as api_main
    app = api_main.app
except Exception as e:
    print('Failed to import api.main.app:')
    traceback.print_exc()
    sys.exit(2)

from fastapi.testclient import TestClient


def run():
    print('Starting TestClient and triggering FastAPI startup...')
    try:
        with TestClient(app) as client:
            payload = {'transaction_text': 'Walmart Supercenter 1234 - Grocery purchase'}
            resp = client.post('/predict', json=payload, timeout=60)
            print('Status code:', resp.status_code)
            try:
                print('Response JSON:')
                print(json.dumps(resp.json(), indent=2))
            except Exception:
                print('Response text:', resp.text)
    except Exception as e:
        print('Error while calling /predict:')
        traceback.print_exc()
        sys.exit(3)


if __name__ == '__main__':
    run()
