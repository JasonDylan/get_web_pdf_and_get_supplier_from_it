# %%
# -*- coding: utf-8 -*-
import openai
#from openai import OpenAI
import os
import pandas as pd
import numpy as np
# import timeout_decorator
import time
pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
 # 不要本地跑，会封号，要在服务器上跑
API_KEY = ""
# COMPLETION_MODEL = "gpt-4-1106-preview" # 选用超长
# COMPLETION_MODEL = "gpt-3.5-turbo-16k" # 选用长
COMPLETION_MODEL="gpt-3.5-turbo-16k"

openai.api_key =API_KEY

# %%

def chat_gpt_turbo(message_our,COMPLETION_MODEL,n=1,max_tokens=1000):

    # client = OpenAI(api_key=API_KEY)

    completion = openai.ChatCompletion.create(
        model=COMPLETION_MODEL,
        messages=message_our,
        max_tokens=300,
        n=1,
        stop=None,  # Disable the default stop behavior
        temperature=0.3,  # Set temperature to 0 for deterministic output
    )

    return completion.choices[0].message


# %%
import pdfplumber
import os

def pdf_to_text(pdf_path, output_folder):
    """
    将PDF文件转换为文本文件。
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + '\n'

    base_name = os.path.basename(pdf_path)
    file_name, _ = os.path.splitext(base_name)
    output_path = os.path.join(output_folder, f"{file_name}.txt")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    return output_path

def convert_all_pdfs_in_folder(folder_path):
    """
    转换指定文件夹内的所有PDF文件。
    """
    # 检查并创建输出目录
    output_folder = folder_path + "_convert_txt"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历文件夹内的所有文件
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file)
            txt_file = pdf_to_text(pdf_path, output_folder)
            print(f"Text saved to {txt_file}")

# 使用示例
folder_path = './PDF'  # 替换为您的PDF文件所在的文件夹路径
convert_all_pdfs_in_folder(folder_path)


# %%
def read_and_replace_newlines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # 读取文件内容
        text = file.read()

        # 替换换行符为句号
        # 注意：这可能会在文本中间产生一些不自然的句号
        # 可以根据需要调整逻辑以处理特殊情况
        text = text.replace('\n', '.')

    return text

# 使用函数
file_path = './PDF_convert_txt/NYSE_MMM_2011.txt'  # 替换为你的文本文件路径
modified_text = read_and_replace_newlines(file_path)
print(modified_text)

# 统计字数
word_count = len(modified_text.split())
print(f"Word count: {word_count}")

# %%
import pandas as pd

def extract_and_save_data(text, path, company_name):
    # 将字符串文本转换为字典
    data = eval(text)

    # 初始化列表来存储数据
    suppliers = []
    contents = []

    # 提取供应商名称和内容
    for i in range(len(data) // 2):
        suppliers.append(data[f'Supplier Company {i+1}'])
        contents.append(data[f'Content of Supplier {i+1}'])

    # 创建 DataFrame
    df = pd.DataFrame({'Supplier': suppliers, 'Content of Supplier': contents})

    # 添加编号列
    df.insert(0, 'Number', range(1, len(df) + 1))

    file_path = f'{path}/{company_name}_suppliers.csv'

    # 检查路径是否存在，如果不存在，则创建它
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # # 保存为 CSV 文件
    df.to_csv(file_path, index=False)


# %%
txt_path_list = os.listdir(f"{folder_path}_convert_txt")[0:]

print(txt_path_list)

for txt_path in txt_path_list:
    company_name = txt_path.replace(".txt", "")
    print(company_name)
    modified_text = read_and_replace_newlines(f"{folder_path}_convert_txt/{txt_path}")[0:10000]

    # system_prompt = """

    #     As an operation management researcher, please help me extract the names of the suppliers from the responsibility report of \
    #     a provided company and summarize the overall situation of the company as mentioned in the report.
    #     Strictly adhere to the specified output format:
    #     {
    #         'Supplier Company 1': 'xxxx', e.g., tesla, 'Content of Supplier 1': 'xxxx',
    #         'Supplier Company 2': 'xxxx', e.g., apple, 'Content of Supplier 2': 'xxxx',
    #         ...
    #     }.
    #     Any deviation from this format will not be accepted. Extract the names of the suppliers accurately based on the content of the report.

    # """


    system_prompt = """
        As an operations management researcher, \
        your task is to extract the names of suppliers from a company's provided responsibility report and summarize the overall situation of the company as mentioned in the report.\
        Strictly adhere to the following example format, without adding or altering any content:\
        Example Output:
        {
            'Supplier Company 1': 'Name of the first supplier',
            'Content of Supplier 1': 'Summary of content about the first supplier',
            'Supplier Company 2': 'Name of the second supplier',
            'Content of Supplier 2': 'Summary of content about the second supplier',
            ...
            'Supplier Company N': 'Name of the Nth supplier',
            'Content of Supplier N': 'Summary of content about the Nth supplier'
        }.\
        Any deviation from this format will not be accepted. \
        Any information beyond this format will be disregarded. \
        Please ensure your response strictly follows this structure. \
        Extract the names of the suppliers accurately based on the report's content, and output them in the specified format.

"""
    message_our = [
        {"role": "system", "content": system_prompt}
    ]


    # 在这里处理每一个文件的数据，例如打印或进行其他操作
    user_prompt = f"{modified_text}"
    user_prompt_dic = {"role": "user", "content": user_prompt}
    message_our.append(user_prompt_dic)

    attempts = 0
    success = False

    while attempts < 5 and not success:
        try:
            output = chat_gpt_turbo(message_our, COMPLETION_MODEL)['content']
            success = True
            print("output", output)
        except Exception as ex:
            print(f'no response from gpt {ex}')
            time.sleep(5)
            attempts += 1
            if attempts == 3:
                break
    
    path = f"./Supply_After_GPT/{COMPLETION_MODEL}"
    extract_and_save_data(output, path, company_name)





