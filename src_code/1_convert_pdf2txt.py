import pdfplumber
import os
import time
# import timeout_decorator
import logging
import re
import subprocess
# 本文件与ChopDocuments.py 功能重复了
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# @timeout_decorator.timeout(100)
# def pdf_to_text(pdf_path, output_folder):
#     try:
#         base_name = os.path.basename(pdf_path)
#         file_name, _ = os.path.splitext(base_name)
#         output_path = os.path.join(output_folder, f"{file_name}_CSR.txt")

#         # 打开输出文件并准备写入
#         with open(output_path, 'w', encoding='utf-8') as f:
#             with pdfplumber.open(pdf_path) as pdf:
#                 # 逐页处理PDF
#                 for page in pdf.pages:
#                     text = page.extract_text() + '\\n'
#                     f.write(text)  # 将每页的文本写入文件

#         logging.info(f"Text saved to {output_path}")
#     except Exception as e:
#         logging.error(f"Error converting PDF to text: {e}")


def pdf_to_text(pdf_path, output_folder):
    try:
        base_name = os.path.basename(pdf_path)
        file_name, _ = os.path.splitext(base_name)
        output_path = os.path.join(output_folder, f"{file_name}_CSR.txt")

        # 使用pdftotext命令行工具
        subprocess.run(["pdftotext", pdf_path, output_path], check=True,stderr=subprocess.DEVNULL)
        logging.info(f"Text saved to {output_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting PDF to text: {e}")


from bs4 import BeautifulSoup
def html_to_txt(html_file_path, output_folder):
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator='\\n', strip=True)

        base_name = os.path.basename(html_file_path)
        file_name, _ = os.path.splitext(base_name)
        txt_file_path = os.path.join(output_folder, f"{file_name}_10K.txt")

        with open(txt_file_path, 'w', encoding='utf-8') as file:
            file.write(text)

        logging.info(f"HTML content successfully converted to TXT and saved at {txt_file_path}")
    except Exception as e:
        logging.error(f"Error converting HTML to text: {e}")

def convert_files_in_batches(folder_path, output_folder, batch_size=10):
    files = [f for f in os.listdir(folder_path) if f.endswith('.pdf') or f.endswith('.html')]
    for i in range(0, len(files), batch_size):
        batch_files = files[i:i+batch_size]
        for file in batch_files:
            full_path = os.path.join(folder_path, file)
            if file.endswith(".pdf"):
                pdf_to_text(full_path, output_folder)
                # pass
            elif file.endswith(".html"):
                # html_to_txt(full_path, output_folder)
                pass
        time.sleep(1)  # 防止过快处理导致的内存问题

# 使用示例
folder_path = 'data\\report_pdf\\PDF'  # 替换为您的PDF和HTML文件所在的文件夹路径
output_folder = folder_path + "_Convert_Txts"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

convert_files_in_batches(folder_path, output_folder)
