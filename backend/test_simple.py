#!/usr/bin/env python3
import requests

# Test the API
response = requests.post(
    "http://localhost:8000/api/analyze",
    json={"name": "Cohere", "domain": "cohere.com"}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")