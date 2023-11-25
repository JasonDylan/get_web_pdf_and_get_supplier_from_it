import requests
import os
import json
import pandas as pd
url = "http://127.0.0.1:5000/v1/chat/completions"

headers = {
    "Content-Type": "application/json"
}

history = []
path = "..\All-Day-TA\Textchunks"

def process_csv(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Extract the text column from the DataFrame
    text_list = df['Text'].tolist()

    # Initialize a dictionary to store supplier information
    supplier_dict = {}

    # Loop through each text entry
    for text in text_list:
        # Format the prompt with the text
        prompt = '请识别以下文本中的供应商，并给出识别结果，识别结果以json list格式返回 例如[{"supplier_name":"XXXX", "is_supplier_probability":"98.12"},{"supplier_name":"XXXX", "is_supplier_probability":"50.12"}]：\n\n文本：{}'.format(text)

        # Create the data payload for the API request
        data = {
            "mode": "chat",
            "messages": [{"role": "system", "content": "assistant"}, {"role": "user", "content": prompt}],
            "history": history
        }

        # Send the API request
        response = requests.post(url, headers=headers, json=data, verify=False)
        assistant_message = response.json()['choices'][0]['message']['content']

        # Parse the response to extract supplier information
        try:
            supplier_info = json.loads(assistant_message)
        except ValueError:
            supplier_info = []

        # Update the supplier dictionary
        for info in supplier_info:
            supplier_name = info['supplier_name']
            is_supplier_probability = float(info['is_supplier_probability'])

            if supplier_name in supplier_dict:
                # Update probability if the supplier already exists in the dictionary
                if is_supplier_probability > supplier_dict[supplier_name]:
                    supplier_dict[supplier_name] = is_supplier_probability
            else:
                # Add supplier to the dictionary if it doesn't exist
                supplier_dict[supplier_name] = is_supplier_probability

    # Save the supplier dictionary to a file
    file_name = os.path.basename(file_path)
    output_file = os.path.join(output_folder, file_name + "-supplier_results.txt")
    with open(output_file, 'w') as file:
        for supplier, probability in supplier_dict.items():
            file.write(f"Supplier: {supplier}, Probability: {probability}\n")

# Create the output folder if it doesn't exist
output_folder = "SupplierResults"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Loop through all CSV files in the specified path
for root, _, files in os.walk(path):
    for file in files:
        if file.endswith(".csv"):
            file_path = os.path.join(root, file)
            process_csv(file_path)

            # Clear history after processing each CSV file
            history = []