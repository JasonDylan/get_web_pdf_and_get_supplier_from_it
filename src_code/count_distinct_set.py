import os
import re

def extract_year_and_content(filename):
    pattern = r"(.*?)_([0-9]{4})__(.*?)_([0-9]{4})"
    match = re.search(pattern, filename)
    if match:
        uk = match.group(1)
        year = match.group(2)
        content = match.group(3)
        return uk, year, content
    else:
        return None, None, None

def process_files(folder_path):
    files = os.listdir(folder_path)
    extracted_data = set()
    uk_data = set()
    for file in files:
        uk, year, content = extract_year_and_content(file)
        if content:
            extracted_data.add(content)
        if uk:
            uk_data.add(uk)
    print(len(extracted_data))
    print(len(uk_data))
    return extracted_data,uk_data

# 指定文件夹路径
folder_path = r"D:\Users\sjc\get_web_pdf_and_get_supplier_from_it\data\report_pdf"

# 处理文件夹中的文件
extracted_data, uk_data = process_files(folder_path)

# 打印提取的数据
for uk in uk_data:
    # print("Year:", year)
    print("uk:", uk)
    # print()


for uk in uk_data:
    # print("Year:", year)
    print("uk:", uk)