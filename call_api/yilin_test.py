# %%
import PyPDF2
import re

def extract_text_between_items(pdf_file_path, start_item, end_item):
    # Step 1: Convert PDF to text
    text = extract_text_from_pdf(pdf_file_path)

    # Step 2: Find indices of start and end items
    start_indices = [match.start() for match in re.finditer(re.escape(start_item), text)]
    end_indices = [match.start() for match in re.finditer(re.escape(end_item), text)]

    # Step 3: Extract text between the second occurrence of start item and the second occurrence of end item
    if len(start_indices) >= 2 and len(end_indices) >= 2:
        start_index = start_indices[1] + len(start_item)
        end_index = end_indices[1]
        extracted_text = text[start_index:end_index].strip()
        return extracted_text
    else:
        return None

def extract_text_from_pdf(pdf_file_path):
    # Open the PDF file in read-binary mode
    with open(pdf_file_path, 'rb') as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Extract text from each page
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        text=text.lower()
        return text

pdf_file_path = "./PDF/AMD-10k-2018.pdf"
start_item = "item 1."
end_item = "item 1b."

# Extract text between the second occurrence of start item and the second occurrence of end item
extracted_text = extract_text_between_items(pdf_file_path, start_item, end_item)

if extracted_text:
    output_file_path = "./RESULT/extracted_text.txt"
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(extracted_text)
    print("Text extracted and saved successfully.")
else:
    print("Could not find the specified start and end items in the PDF.")

# %%
def count_words_in_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        word_count = len(text.split())
        return word_count

extracted_text_file_path = "./RESULT/extracted_text.txt"

# 统计提取文本文件中的字数
word_count = count_words_in_text_file(extracted_text_file_path)
print("Word count:", word_count)

# %%
import openai
openai.api_key = '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'


import openai

def split_text_into_segments(text, max_segment_length):
    segments = []
    current_segment = ""

    for word in text.split():
        if len(current_segment) + len(word) + 1 <= max_segment_length:
            current_segment += word + " "
        else:
            segments.append(current_segment.strip())
            current_segment = word + " "
    
    if current_segment:
        segments.append(current_segment.strip())

    return segments

def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.3
    )
    return response.choices[0].message['content']

def identify_vendors_in_text(text):
    segments = split_text_into_segments(text, 2048)
    identified_vendors = set()

    for segment in segments:
        prompt = "extract the supplier names based on the text, for each identified supplier, give your \
        explanation why it is identified as a supplier. You should give your response in such \
        format: supplier name, explanation" + segment
        response = generate_response(prompt)
        identified_vendors.update(extract_vendors_from_response(response))
    
    return identified_vendors

def extract_vendors_from_response(response):
    # Placeholder implementation, replace with your logic to extract vendors from the response
    vendors = set()
    # Example placeholder logic: extract any uppercase words from the response
    words = response.split()
    for word in words:
        if word.isupper():
            vendors.add(word)
    return vendors

# Read the text file
text_file_path = "./RESULT/extracted_text.txt"
with open(text_file_path, 'r', encoding='utf-8') as file:
    text = file.read()

# Identify vendors in the text
identified_vendors = identify_vendors_in_text(text)

# Print the identified vendors
for vendor in identified_vendors:
    print(vendor)

# %%



