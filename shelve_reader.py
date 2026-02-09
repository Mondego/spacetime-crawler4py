import shelve
import os

file_path = 'frontier.shelve'

try:
    # Open the shelve file in read mode ('r' flag) or default 'c' (create if not exists)
    with shelve.open(file_path, 'r') as db:
        print(f"Keys available in the shelve: {list(db.keys())}")

        # Retrieve a specific value by its key
        if 'some_key' in db:
            value = db['some_key']
            print(f"Value for 'some_key': {value}")
        else:
            print("Key 'some_key' not found in the shelve.")

        # Iterate through all key-value pairs
        print("\nAll items in the shelve:")
        for key, value in db.items():
            print(f"{key}: {value}")

except Exception as e:
    print(f"An error occurred: {e}")