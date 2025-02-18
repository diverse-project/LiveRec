import requests
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor

BASE_URL = 'http://localhost:5000'

def get_all_items():
    response = requests.get(f'{BASE_URL}/items')
    print(f"GET all items: {response.status_code}")
    return response.json()

def create_item(name, value):
    data = {'name': name, 'value': value}
    response = requests.post(f'{BASE_URL}/items', json=data)
    print(f"CREATE item {name}: {response.status_code}")
    return response.json() if response.status_code == 201 else None

def update_item(item_id, name, value):
    data = {'name': name, 'value': value}
    response = requests.put(f'{BASE_URL}/items/{item_id}', json=data)
    print(f"UPDATE item {item_id}: {response.status_code}")
    return response.json() if response.status_code == 200 else None

def delete_item(item_id):
    response = requests.delete(f'{BASE_URL}/items/{item_id}')
    print(f"DELETE item {item_id}: {response.status_code}")
    return response.status_code == 200

def run_simulation():
    # Initial state
    print("\n=== Initial State ===")
    items = get_all_items()
    print(f"Current items: {json.dumps(items, indent=2)}")

    # Create multiple items
    print("\n=== Creating Items ===")
    created_items = []
    for i in range(5):
        name = f"Item_{i}"
        value = random.uniform(1.0, 100.0)
        item = create_item(name, value)
        if item:
            created_items.append(item)
        time.sleep(0.5)  # Small delay between operations

    # Show current state
    print("\n=== After Creation ===")
    items = get_all_items()
    print(f"Current items: {json.dumps(items, indent=2)}")

    # Update some items
    print("\n=== Updating Items ===")
    for item in created_items[:3]:
        new_value = random.uniform(100.0, 200.0)
        update_item(item['id'], f"{item['name']}_updated", new_value)
        time.sleep(0.5)

    # Show current state
    print("\n=== After Updates ===")
    items = get_all_items()
    print(f"Current items: {json.dumps(items, indent=2)}")

    # Delete some items
    print("\n=== Deleting Items ===")
    for item in created_items[3:]:
        delete_item(item['id'])
        time.sleep(0.5)

    # Final state
    print("\n=== Final State ===")
    items = get_all_items()
    print(f"Current items: {json.dumps(items, indent=2)}")

    # Test concurrent requests
    print("\n=== Testing Concurrent Requests ===")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i in range(3):
            futures.append(executor.submit(create_item, f"Concurrent_Item_{i}", random.uniform(1.0, 100.0)))
            futures.append(executor.submit(get_all_items))
        
        for future in futures:
            future.result()

    # Show final state after concurrent operations
    print("\n=== Final State After Concurrent Operations ===")
    items = get_all_items()
    print(f"Current items: {json.dumps(items, indent=2)}")

if __name__ == '__main__':
    print("Starting API simulation...")
    try:
        run_simulation()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the Flask application.")
        print("Make sure the Flask app is running on http://localhost:5000") 