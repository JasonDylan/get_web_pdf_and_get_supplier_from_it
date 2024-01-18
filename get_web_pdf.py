import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
import pandas as pd
import re
from util.my_request import make_request
# Read company names from txt file and process each line
company_list = []
df = pd.read_csv('input/sp500cik.csv')
for _, row in df.iterrows():
    tic, conm, cik = row['tic'], row['conm'], row['cik']
    # Remove leading and trailing spaces, quotes, and commas
    company_name = conm.strip().strip(',').strip('\"\'')
    print( tic, conm, cik)
    company_to_search = company_name
    
    # URL for company page
    company_url = f"https://www.responsibilityreports.com/Companies?search={tic}"

    # Request company list page
    # response = requests.get(company_url)
    response = make_request(company_url, "GET", headers={}, data={})

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all company links
    company_links = soup.select(".apparel_stores_company_list .companyName a")
    # if_continue = False
    # Iterate over each company link
    for link in company_links:
        company_name = link.text.strip()
        print(f"{company_name=} read start")
            
        company_url = "https://www.responsibilityreports.com" + link["href"]
        
        # Request company's PDF list page
        # pdf_list_response = requests.get(company_url)
        pdf_list_response = make_request(company_url, "GET", headers={}, data={})
        
        # Parse the PDF list page HTML content
        pdf_list_soup = BeautifulSoup(pdf_list_response.content, "html.parser")
        
        # Find all PDF download links
        pdf_links = pdf_list_soup.select(".archived_report_content_block .btn_archived.view_annual_report a")
        
        # Create a directory to store the PDF files
        directory = "./data/report_pdf"
        print(f"{directory=}")
        os.makedirs(directory, exist_ok=True)
        
        # Iterate over each PDF link and download the file
        for pdf_link in pdf_links:
            pdf_url = "https://www.responsibilityreports.com" + pdf_link["href"]
            
            # Get the PDF file name from the URL
            parsed_url = urlparse(pdf_url)
            pdf_file_name = os.path.basename(parsed_url.path)
            pdf_file_name = pdf_file_name.replace("\\", "-").replace("/","-")
            match = re.search(r"_(\d{4})", pdf_file_name)
            year = ""
            if match:
                year = match.group(1)
                print(year)  # 输出: 2021
            else:
                print("未找到匹配的部分")

            the_name = f"{str(tic)}_{str(year)}_csr"
            print(f"{the_name=}")

            if pdf_file_name:
                pdf_file_name = the_name + "__" + pdf_file_name
                print(f"{parsed_url=} {pdf_url=} {pdf_file_name=}")
                pdf_file_path = os.path.join(directory, pdf_file_name)
                # Download the PDF file
                # pdf_response = requests.get(pdf_url)
                pdf_response = make_request(pdf_url, "GET", headers={}, data={})
                with open(pdf_file_path, "wb") as pdf_file:
                    pdf_file.write(pdf_response.content)
        print(f"{company_name=} read done")