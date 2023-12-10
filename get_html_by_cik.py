import requests
from bs4 import BeautifulSoup
import json
from util.my_request import make_request
def extract_text_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    return text
import os
import pandas as pd

payload = {}
headers = {
  'authority': 'www.sec.gov',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
  'cache-control': 'max-age=0',
  'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

# 完成一个需求，
# 从文件input/sp500cik.csv读取数据
# 这个csv 分三行tic conm cik
# 从input/test.json文件读取为company_info_json
# tic_conm_ciks = read csv
# tics = []
# conms = []
# ciks = ["1318605"]
need_form_types = ["10-K"]

# Read data from CSV
df = pd.read_csv('input/sp500cik.csv')

# Create empty DataFrame to store the extracted data
data = pd.DataFrame(columns=['tic', 'conm', 'cik', 'form_url', 'text'])

for _, row in df.iterrows():
    tic, conm, cik = row['tic'], row['conm'], row['cik']

    # Create directory for saving files
    save_dir = f"./data/EDGAR/ORG/{tic}_{cik}"
    os.makedirs(save_dir, exist_ok=True)

    cik_10 = str(cik).zfill(10)
    company_info_json_url = f"https://data.sec.gov/submissions/CIK{cik_10}.json"

    # Retrieve company info JSON
    response = make_request(company_info_json_url, "GET", headers=headers, data=payload)
    company_info_json = json.loads(response.text)

    # Save company info JSON to file
    filename = f"CIK{cik_10}.json"
    with open(f"./data/EDGAR/JSON/{filename}", 'w') as file:
        json.dump(company_info_json, file)
        print(f"JSON data saved to {filename}")

    filings = company_info_json['filings']
    if 'recent' in filings:
        recent_filing = filings['recent']
        accessionNumber = recent_filing['accessionNumber']
        reportDate = recent_filing['reportDate']
        form = recent_filing['form']
        primaryDocument = recent_filing['primaryDocument']

        for a_accessionNumber, a_reportDate, a_form_type, a_primaryDocument in zip(accessionNumber, reportDate, form, primaryDocument):
            if a_form_type in need_form_types:
                form_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{a_accessionNumber.replace('-', '')}/{a_primaryDocument}"
                file_name = str(tic.replace(" ", "_")) +"_"+ str(conm.replace(" ", "_"))+"_"+str(a_reportDate.replace("-","_"))+"_"+ a_primaryDocument.split(".")[0]
                
                if file_name == "CLX_CLOROX_CO/DE_2023_06_30_clx-20230630.html":
                    print(f"{file_name=}")
                file_name = file_name.replace("\\", "-").replace("/","-")
                # Retrieve form HTML
                response_form = make_request(form_url, "GET", headers=headers, data=payload)
                html = response_form.text
                
                # Save HTML file
                html_file_path = os.path.join(save_dir, f"{file_name}.html")
                with open(html_file_path, 'w', encoding='utf-8') as file:
                    file.write(html)
                    print(f"HTML file saved to {html_file_path}")

                # Extract text from HTML
                text = extract_text_from_html(html)
                if text:
                    # Save text to file
                    text_file_path = os.path.join(save_dir, f"{file_name}.txt")
                    with open(text_file_path, 'w', encoding='utf-8') as file:
                        file.write(text)
                        print(f"Text file saved to {text_file_path}")
                else:
                    print("Failed to extract text from HTML.")
                    text = ""

                # Append data to DataFrame
                data = data.append({'tic': tic, 'conm': conm, 'cik': cik, 'form_url': form_url, 'text': text}, ignore_index=True)
    else:
        print("No recent filings found for the company.")

# Save data to Excel and CSV files
data.to_excel('output/data.xlsx', index=False)
data.to_csv('output/data.csv', index=False)