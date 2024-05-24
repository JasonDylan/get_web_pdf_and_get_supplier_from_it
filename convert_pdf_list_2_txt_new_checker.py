import io
import os
import shutil
import sys
from typing import List

import fitz  # 使用 PyMuPDF
from tqdm.contrib.concurrent import process_map

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def convert_pdf_to_text(pdf_path: str, output_dir: str) -> None:
    """将 PDF 文件转换为文本文件。

    Args:
        pdf_path (str): PDF 文件路径。
        output_dir (str): 输出目录。
    """
    try:
        with fitz.open(pdf_path) as doc:
            text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                try:
                    text += page.get_text()
                except Exception as e:
                    print(f"跳过页面，因为解码错误：{e}")
                    # 或者你可以尝试使用其他方法提取文本，例如 OCR
            txt_filename = os.path.splitext(os.path.basename(pdf_path))[0] + ".txt"
            txt_path = os.path.join(output_dir, txt_filename)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
            # print(f"{txt_path=} saved")
    except Exception as e:
        print(f"解析 {pdf_path} 时出错：{e}")


def process_file(args):
    """处理单个文件。

    Args:
        args (tuple): (filename, source_dir, dest_dir, is_pdf)
    """
    filename, source_dir, dest_dir, is_pdf = args
    source_path = os.path.join(source_dir, filename)
    dest_path = os.path.join(dest_dir, filename)
    if is_pdf:
        convert_pdf_to_text(source_path, dest_dir)
    else:
        if not os.path.exists(dest_path):
            shutil.copy2(source_path, dest_path)
            print(f"copied to {dest_path}")


def main():
    pdf_dir = r"D:\Users\sjc\get_web_pdf_and_get_supplier_from_it\data\pdf_new_files"
    text_dir = r"D:\Users\sjc\get_web_pdf_and_get_supplier_from_it\data\text_files"
    text_new_dir = (
        r"D:\Users\sjc\get_web_pdf_and_get_supplier_from_it\data\text_new_files"
    )

    # 创建输出目录
    os.makedirs(text_new_dir, exist_ok=True)

    parsed_pdfs: List[str] = []
    unparsed_pdfs: List[str] = []

    # 获取已解析和未解析的文件名
    for filename in os.listdir(pdf_dir):
        if not filename.endswith(".pdf"):
            continue

        pdf_path = os.path.join(pdf_dir, filename)
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_path = os.path.join(text_dir, txt_filename)
        txt_new_path = os.path.join(text_new_dir, txt_filename)

        if os.path.exists(txt_path) or os.path.exists(txt_new_path):
            parsed_pdfs.append((txt_filename, text_dir, text_new_dir, False))
        else:
            unparsed_pdfs.append((filename, pdf_dir, text_new_dir, True))

    print(f"{len(parsed_pdfs)=}")
    print(f"{len(unparsed_pdfs)=}")
    # 使用 process_map 多进程处理文件
    # process_map(
    #     process_file,
    #     unparsed_pdfs,
    #     max_workers=os.cpu_count(),
    #     desc="解析PDF",
    #     chunksize=100,
    # )
    process_map(
        process_file,
        parsed_pdfs,
        max_workers=os.cpu_count(),
        desc="复制TXT",
        chunksize=100,
    )


if __name__ == "__main__":
    main()
