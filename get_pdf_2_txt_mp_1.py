import logging
import multiprocessing
import os
import shutil
from urllib.parse import urlparse

import pandas as pd
import pdfplumber
from bs4 import BeautifulSoup
from tqdm.contrib.concurrent import process_map, thread_map

from util.my_request import make_request


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


def process_company(df, process_id):
    try:
        completed_tasks = 0
        total_tasks = len(df)
        for idx, row in df.iterrows():
            tic_col_name = "tic"  # 列名
            conm_col_name = "conm"  # 列名
            cik_col_name = "cik"  # 列名

            tic, conm, cik = row[tic_col_name], row[conm_col_name], row[cik_col_name]
            # Remove leading and trailing spaces, quotes, and commas
            company_name = conm.strip().strip(",").strip("\"'")
            print(f"Process {process_id}: {tic=}, {conm=}, {cik=}")
            company_to_search = company_name

            # URL for company page
            company_url = (
                f"https://www.responsibilityreports.com/Companies?search={tic}"
            )

            # Request company list page
            response = make_request(company_url, "GET", headers={}, data={})

            # Parse the HTML content
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all company links
            company_links = soup.select(".apparel_stores_company_list .companyName a")

            # Iterate over each company link
            # print(f"---Process {process_id}: {tic=} {len(company_links)=}")
            for link in company_links:
                company_name = link.text.strip()
                # print(f"Process {process_id}: {tic=} {company_name=} read start")

                try:
                    company_url = "https://www.responsibilityreports.com" + link["href"]

                    # Request company's PDF list page
                    pdf_list_response = make_request(
                        company_url, "GET", headers={}, data={}
                    )

                    # Parse the PDF list page HTML content
                    if pdf_list_response:
                        pdf_list_soup = BeautifulSoup(
                            pdf_list_response.content, "html.parser"
                        )

                        # Find all PDF download links
                        pdf_links = pdf_list_soup.select(
                            ".archived_report_content_block .btn_archived.view_annual_report a"
                        )

                        # Iterate over each PDF link and convert to text
                        for pdf_link in pdf_links:
                            pdf_url = (
                                "https://www.responsibilityreports.com"
                                + pdf_link["href"]
                            )

                            parsed_url = urlparse(pdf_url)
                            file_name = os.path.basename(parsed_url.path)
                            file_name = file_name.replace("\\", "-").replace("/", "-")
                            # # Save PDF to file
                            # if output_folder_has_no_file(
                            #     output_folder="./data/pdf_files",
                            #     file_name=file_name,
                            # ):
                            #     response, file_name = (
                            #         make_request_and_get_file_name(pdf_url)
                            #     )
                            #     save_pdf_to_file(
                            #         response,
                            #         file_name,
                            #         output_folder="./data/pdf_files",
                            #     )
                            #     save_pdf_to_file(
                            #         response,
                            #         file_name,
                            #         output_folder="./data/pdf_new_files",
                            #     )
                            # else:
                            #     print(f"input {file_name=} already have")
                            #     if output_folder_has_no_file(
                            #         output_folder="./data/pdf_new_files",
                            #         file_name=file_name,
                            #     ):
                            #         copy_file_to_new_dir(
                            #             file_name,
                            #             output_folder="./data/pdf_new_files",
                            #             input_folder="./data/pdf_files",
                            #         )
                            #     else:
                            #         print(f"output {file_name=} already have")

                            # Convert PDF to text
                            pdf_file_path = get_file_path(
                                pdf_url, folder_name="./data/pdf_new_files"
                            )
                            pdf_to_text(pdf_file_path)
                    # print(f"Process {process_id}:----------{tic=}  {company_name=} read done")
                    else:
                        print(f"no pdf {company_url=}")
                except Exception as e:
                    print(f"{e=} {link['href']=}")

            completed_tasks += 1
            print(
                f"Process {process_id}:---------------------{tic=} Completed {completed_tasks}/{total_tasks}  tasks"
            )
    except Exception as e:
        print(f"{e=}")
    finally:

        print(f"{process_id} is Done")


def copy_file_to_new_dir(file_name, output_folder, input_folder):
    """将PDF文件从输入文件夹复制到输出文件夹。

    Args:
        file_name: PDF 文件的名称。
        output_folder: 输出文件夹的路径。
        input_folder: 输入文件夹的路径。
    """
    try:
        if file_name:
            # 构建输入文件路径
            input_path = os.path.join(input_folder, file_name)
            # 构建输出文件路径
            output_path = os.path.join(output_folder, file_name)
            # 确保输出文件夹存在
            os.makedirs(output_folder, exist_ok=True)
            # 复制文件
            shutil.copyfile(input_path, output_path)
            print(f"file copied to: {output_path}")
    except Exception as e:
        print(f"Error copying file: {e}")


def make_request_and_get_file_name(pdf_url):

    # Send request to download PDF
    file_name = None
    response = make_request(pdf_url, "GET", headers={}, data={})
    if response and response.content:
        # Extract file name from URL
        parsed_url = urlparse(pdf_url)
        file_name = os.path.basename(parsed_url.path)
        file_name = file_name.replace("\\", "-").replace("/", "-")

    return response, file_name


def save_pdf_to_file(response, file_name, output_folder):
    try:
        if file_name:
            # Save PDF to file
            os.makedirs(output_folder, exist_ok=True)
            output_path = os.path.join(output_folder, file_name)
            with open(output_path, "wb") as file:
                file.write(response.content)
                print(f"PDF saved: {file_name}")
    except Exception as e:
        print(f"Error saving PDF: {e}")


def get_file_path(pdf_url, folder_name="./data/pdf_files"):
    parsed_url = urlparse(pdf_url)
    file_name = os.path.basename(parsed_url.path)
    file_name = file_name.replace("\\", "-").replace("/", "-")
    pdf_file_path = os.path.join(folder_name, file_name)
    return pdf_file_path


def pdf_to_text(pdf_file_path):

    # Save text to TXT file
    os.makedirs("./data/text_new_files", exist_ok=True)
    try:
        output_folder = "./data/text_new_files"
        file_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
        output_path = os.path.join(output_folder, f"{file_name}.txt")

        if output_folder_has_no_file(
            output_folder="./data/text_files",
            file_name=f"{file_name}.txt",
        ):
            with pdfplumber.open(pdf_file_path) as pdf:
                pages_text = []
                for page in pdf.pages:
                    text = page.extract_text()
                    pages_text.append(text)
                extracted_text = "\n".join(pages_text)

                if extracted_text:
                    with open(output_path, "w", encoding="utf-8") as file:
                        file.write(extracted_text)
                    print(f"----------Text  {output_path} saved for {pdf_file_path}")
                else:
                    print(f"Failed to extract text from {pdf_file_path}")
        else:
            print(f"input {file_name=} already have")
            if output_folder_has_no_file(
                output_folder="./data/pdf_new_files",
                file_name=f"{file_name}.txt",
            ):
                copy_file_to_new_dir(
                    file_name=f"{file_name}.txt",
                    output_folder="./data/text_new_files",
                    input_folder="./data/text_files",
                )
            else:
                print(f"output {file_name=} already have")

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    else:
        print(f"Folder '{folder_path}' already exists.")


def process_company_batch(args):
    chunk, process_id = args
    process_company(chunk, process_id)


if __name__ == "__main__":
    df = pd.read_csv("uscik.csv")
    print("uscik.csv")
    # df = pd.read_csv("missing_tic_1.csv")
    # print("missing_tic.csv_1")
    num_processes = 32

    # Exclude completed rows
    # df = df.iloc[51:]

    output_folder = "./data/pdf_files"
    create_folder_if_not_exists(folder_path=output_folder)
    create_folder_if_not_exists(folder_path="./data/pdf_new_files")
    create_folder_if_not_exists(folder_path="./data/text_files")
    create_folder_if_not_exists(folder_path="./data/text_new_files")

    # Divide the dataframe into chunks
    chunk_size = len(df) // num_processes
    chunks = [df[i : i + chunk_size] for i in range(0, len(df), chunk_size)]

    # 准备包含 (chunk, process_id) 的参数列表
    args_list = [(chunk, i) for i, chunk in enumerate(chunks)]

    # 使用 process_map 来并行处理 chunks，并显示进度条
    results = thread_map(process_company_batch, args_list, max_workers=num_processes)
