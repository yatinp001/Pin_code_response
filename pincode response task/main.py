import csv
import requests
import concurrent.futures
import os
import json

 

def get_pincode_data(pincode):
    url = f"https://api.postalpincode.in/pincode/{pincode}"
    response = requests.get(url)
    data = response.json()
    return data

def save_response_to_json(pincode, data):
    filename = f"{pincode}.json"
    with open(filename, "w") as json_file:
        json.dump(data, json_file) 

def fetch_all_pincodes(csv_filename):
    all_pincodes = []

    # Read the PIN codes from the "Pincode" column in the CSV file
    with open(csv_filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_pincodes.append(row["Pincode"])

    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_pincode_data, pincode) for pincode in all_pincodes]

        for future, pincode in zip(concurrent.futures.as_completed(futures), all_pincodes):
            try:
                data = future.result()
                results.append(data)
                save_response_to_json(pincode, data)
            except Exception as e:
                print(f"An error occurred for PIN code {pincode}: {e}")

 

    return results

 

if __name__ == "__main__":
    csv_filename = "pincodes.csv"
    all_pincode_data = fetch_all_pincodes(csv_filename)
    print("API responses saved as JSON files.")