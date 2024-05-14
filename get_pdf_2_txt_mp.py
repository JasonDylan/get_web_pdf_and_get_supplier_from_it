import os
import pandas as pd
import logging
from util.my_request import make_request
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pdfplumber
import multiprocessing


def output_folder_has_no_pdf(output_folder, pdf_file_name):
    """检查输出文件夹中是否没有指定名称的 PDF 文件。

    Args:
      output_folder: 输出文件夹的路径。
      pdf_file_name: PDF 文件的名称。

    Returns:
      如果输出文件夹中没有指定名称的 PDF 文件，则返回 True，否则返回 False。
    """

    # 获取输出文件夹中所有 PDF 文件的名称。
    pdf_file_names = os.listdir(output_folder)

    # 检查输出文件夹中是否有指定名称的 PDF 文件。
    if pdf_file_name in pdf_file_names:
        return False
    else:
        return True


def process_company(df, process_id):
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
        company_url = f"https://www.responsibilityreports.com/Companies?search={tic}"

        # Request company list page
        response = make_request(company_url, "GET", headers={}, data={})

        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all company links
        company_links = soup.select(".apparel_stores_company_list .companyName a")

        # Iterate over each company link
        print(f"---Process {process_id}: {tic=} {len(company_links)=}")
        for link in company_links:
            company_name = link.text.strip()
            print(f"Process {process_id}: {tic=} {company_name=} read start")

            company_url = "https://www.responsibilityreports.com" + link["href"]

            # Request company's PDF list page
            pdf_list_response = make_request(company_url, "GET", headers={}, data={})

            # Parse the PDF list page HTML content
            pdf_list_soup = BeautifulSoup(pdf_list_response.content, "html.parser")

            # Find all PDF download links
            pdf_links = pdf_list_soup.select(
                ".archived_report_content_block .btn_archived.view_annual_report a"
            )

            # Iterate over each PDF link and convert to text
            for pdf_link in pdf_links:
                pdf_url = "https://www.responsibilityreports.com" + pdf_link["href"]

                output_folder = "./data/pdf_files"
                parsed_url = urlparse(pdf_url)
                pdf_file_name = os.path.basename(parsed_url.path)
                pdf_file_name = pdf_file_name.replace("\\", "-").replace("/", "-")
                # Save PDF to file
                if output_folder_has_no_pdf(output_folder, pdf_file_name):
                    save_pdf_to_file(pdf_url)

                # Convert PDF to text
                # pdf_file_path = get_pdf_file_path(pdf_url)
                # pdf_to_text(pdf_file_path)
            print(f"Process {process_id}:----------{tic=}  {company_name=} read done")
        completed_tasks += 1
        print(
            f"Process {process_id}:---------------------{tic=} Completed {completed_tasks}/{total_tasks}  tasks"
        )


def save_pdf_to_file(pdf_url):
    try:
        # Send request to download PDF
        response = make_request(pdf_url, "GET", headers={}, data={})
        if response and response.content:
            # Extract file name from URL
            parsed_url = urlparse(pdf_url)
            pdf_file_name = os.path.basename(parsed_url.path)
            pdf_file_name = pdf_file_name.replace("\\", "-").replace("/", "-")

            if pdf_file_name:
                # Save PDF to file
                output_folder = "./data/pdf_files"
                os.makedirs(output_folder, exist_ok=True)
                output_path = os.path.join(output_folder, pdf_file_name)
                with open(output_path, "wb") as file:
                    file.write(response.content)
                    print(f"PDF saved: {pdf_file_name}")
    except Exception as e:
        print(f"Error saving PDF: {e}")


def get_pdf_file_path(pdf_url):
    parsed_url = urlparse(pdf_url)
    pdf_file_name = os.path.basename(parsed_url.path)
    pdf_file_name = pdf_file_name.replace("\\", "-").replace("/", "-")
    pdf_file_path = os.path.join("./data/pdf_files", pdf_file_name)
    return pdf_file_path


def pdf_to_text(pdf_file_path):
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                pages_text.append(text)
            extracted_text = "\n".join(pages_text)

            if extracted_text:
                # Save text to TXT file
                output_folder = "./data/text_files"
                os.makedirs(output_folder, exist_ok=True)
                file_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
                output_path = os.path.join(output_folder, f"{file_name}.txt")
                with open(output_path, "w", encoding="utf-8") as file:
                    file.write(extracted_text)
                    print(f"----------Text saved for {pdf_file_path}")
            else:
                print(f"Failed to extract text from {pdf_file_path}")
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")


def process_company_batch(rows, process_id):
    process_company(rows, process_id)


if __name__ == "__main__":
    df = pd.read_csv("input/sp500cik.csv")
    num_processes = 8

    # Exclude completed rows
    # df = df.iloc[51:]

    # Divide the dataframe into chunks
    chunks = [
        df[i : i + len(df) // num_processes]
        for i in range(0, len(df), len(df) // num_processes)
    ]

    # Create a list to hold the processes
    processes = []

    # Create and start a process for each chunk
    for i, chunk in enumerate(chunks):
        process = multiprocessing.Process(target=process_company_batch, args=(chunk, i))
        processes.append(process)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()
