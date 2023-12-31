import csv
import requests
import concurrent.futures
import os
import json
import time

def get_pincode_data(pincode):
    url = f"https://api.postalpincode.in/pincode/{pincode}"
    try:
        response = requests.get(url)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred for PIN code {pincode}: {e}")
        return None

def save_response_to_json(responses):
    with open("pincodes_response.json", "w") as json_file:
        json.dump(responses, json_file) 

def fetch_all_pincodes(csv_filename):
    all_pincodes = []

    # Read the PIN codes from the "Pincode" column in the CSV file
    with open(csv_filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_pincodes.append(row["Pincode"])

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=1500) as executor:
        futures = [executor.submit(get_pincode_data, pincode) for pincode in all_pincodes]

        for future, pincode in zip(concurrent.futures.as_completed(futures), all_pincodes):
            retries = 3
            while retries > 0:
                try:
                    data = future.result()
                    if data and data not in results:  # Check if data is already in the results list
                        pin =data[0]["PostOffice"][0]["Pincode"]
                        results.append({pin:data})
                    break 
                except Exception as e:
                    print(f"An error occurred for PIN code {pincode}: {e}")
                    retries -= 1
                    if retries == 0:
                        print(f"Max retries exceeded for PIN code {pincode}. Skipping...")
                        break
                    time.sleep(1)  # Wait for 1 second before retrying

    # Save all responses to a single JSON file
    save_response_to_json(results)

    return results

if __name__ == "__main__":
    csv_filename = "pincodes.csv"
    all_pincode_data = fetch_all_pincodes(csv_filename)
    print("API responses saved as JSON file.")
