import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse

# Read company names from txt file and process each line
company_list = []
with open("company_names.txt", "r") as file:
    for line in file:
        # Remove leading and trailing spaces, quotes, and commas
        company_name = line.strip().strip(',').strip('\"\'')
        if company_name:
            company_list.append(company_name)

for company_to_search in company_list:
    
    # URL for company page
    company_url = f"https://www.responsibilityreports.com/Companies?search={company_to_search}"

    # Request company list page
    response = requests.get(company_url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all company links
    company_links = soup.select(".apparel_stores_company_list .companyName a")

    # Iterate over each company link
    for link in company_links:
        company_name = link.text.strip()
        company_url = "https://www.responsibilityreports.com" + link["href"]
        
        # Request company's PDF list page
        pdf_list_response = requests.get(company_url)
        
        # Parse the PDF list page HTML content
        pdf_list_soup = BeautifulSoup(pdf_list_response.content, "html.parser")
        
        # Find all PDF download links
        pdf_links = pdf_list_soup.select(".archived_report_content_block .btn_archived.view_annual_report a")
        
        # Create a directory to store the PDF files
        directory = "./data/report_pdf/" + company_name
        os.makedirs(directory, exist_ok=True)
        
        # Iterate over each PDF link and download the file
        for pdf_link in pdf_links:
            pdf_url = "https://www.responsibilityreports.com" + pdf_link["href"]
            
            # Get the PDF file name from the URL
            parsed_url = urlparse(pdf_url)
            pdf_file_name = os.path.basename(parsed_url.path)
            pdf_file_path = os.path.join(directory, pdf_file_name)
            
            # Download the PDF file
            pdf_response = requests.get(pdf_url)
            with open(pdf_file_path, "wb") as pdf_file:
                pdf_file.write(pdf_response.content)
        print(f"{company_name} read done")