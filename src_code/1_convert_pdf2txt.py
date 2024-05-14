import multiprocessing
import os
import PyPDF2
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def output_folder_has_no_file(output_folder, file_name):
    """检查输出文件夹中是否没有指定名称的 PDF 文件。

    Args:
        output_folder: 输出文件夹的路径。
        file_name: PDF 文件的名称。

    Returns:
        如果输出文件夹中没有指定名称的 PDF 文件，则返回 True，否则返回 False。
    """

    # 获取输出文件夹中所有 PDF 文件的名称。
    file_names = os.listdir(output_folder)

    # 检查输出文件夹中是否有指定名称的 PDF 文件。
    if file_name in file_names:
        return False
    else:
        return True

def convert_pdf_to_text(pdf_path, output_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(text)
        
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(text)

def pdf_to_text(pdf_path, output_folder):
    try:
        base_name = os.path.basename(pdf_path)
        file_name, _ = os.path.splitext(base_name)
        output_path = os.path.join(output_folder, f"{file_name}_CSR.txt")
        output_path2 = os.path.join(output_folder+"_rest", f"{file_name}_CSR.txt")
        if output_folder_has_no_file(output_folder, f"{file_name}_CSR.txt"):
            # 使用pdftotext命令行工具
            try:
                convert_pdf_to_text(pdf_path, output_path2)
                logging.info(f"Text saved to {output_path2}")
            except Exception as ex:
                logging.error(f"{ex=} {pdf_path} {output_path}")
        # else:
        #     print(f"{file_name=} already exists")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting PDF to text: {e}")

def html_to_txt(html_file_path, output_folder):
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)

        base_name = os.path.basename(html_file_path)
        file_name, _ = os.path.splitext(base_name)
        txt_file_path = os.path.join(output_folder, f"{file_name}_10K.txt")

        with open(txt_file_path, 'w', encoding='utf-8') as file:
            file.write(text)

        logging.info(f"HTML content successfully converted to TXT and saved at {txt_file_path}")
    except Exception as e:
        logging.error(f"Error converting HTML to text: {e}")

def process_file(file_path, output_folder):
    file_name = os.path.basename(file_path)
    if file_name.endswith(".pdf"):
        pdf_to_text(file_path, output_folder)
    elif file_name.endswith(".html"):
        html_to_txt(file_path, output_folder)

def convert_files_in_batches(folder_path, output_folder, batch_size=10):
    files = [f for f in os.listdir(folder_path) if f.endswith('.pdf') or f.endswith('.html')]
    total_files = len(files)
    completed_files = multiprocessing.Value('i', 0)

    with multiprocessing.Pool(processes=7) as pool:
        pool.starmap(process_file, [(os.path.join(folder_path, file), output_folder) for file in files])

    print(f"Completed {completed_files.value}/{total_files} files.")

# 使用示例
    
if __name__ == '__main__':
    folder_path = r'D:\Users\sjc\get_web_pdf_and_get_supplier_from_it\data\pdf_files'
    output_folder = folder_path + "_Convert_Txts"  # 替换为您的PDF和HTML文件所在的文件夹路径
    output_folder1 = folder_path + "_Convert_Txts_rest"  # 替换为您的PDF和HTML文件所在的文件夹路径
    # output_folder = r"D:\Users\sjc\get_web_pdf_and_get_supplier_from_it\data\text_files"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(output_folder1):
        os.makedirs(output_folder1)

    convert_files_in_batches(folder_path, output_folder)