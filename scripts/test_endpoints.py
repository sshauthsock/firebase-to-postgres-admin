#!/usr/bin/env python
import requests
import json

try:
    response = requests.get('http://127.0.0.1:8000/openapi.json')
    if response.status_code == 200:
        data = response.json()
        paths = data.get('paths', {})
        
        print("=" * 50)
        print("Registered API Endpoints:")
        print("=" * 50)
        
        for path in sorted(paths.keys()):
            for method in paths[path].keys():
                print(f"{method.upper():6} {path}")
        
        print("=" * 50)
        
        post_endpoints = []
        for path in paths.keys():
            if 'post' in paths[path]:
                post_endpoints.append(path)
        
        if post_endpoints:
            print(f"\n✓ Found {len(post_endpoints)} POST endpoint(s):")
            for endpoint in post_endpoints:
                print(f"  - POST {endpoint}")
        else:
            print("\n✗ No POST endpoints found!")
            print("  Please restart the server.")
    else:
        print(f"Server response error: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to server.")
    print("  Please check if the server is running.")
except Exception as e:
    print(f"Error: {e}")

