# -*- coding: utf-8 -*-
from openai import OpenAI
import os
import pandas as pd
import numpy as np
import timeout_decorator
import time
import globals
import re
import ast

COMPLETION_MODEL = globals.COMPLETION_MODEL
API_KEY = globals.API_KEY


@timeout_decorator.timeout(100)
def chat_gpt_turbo(message_our,COMPLETION_MODEL,n=1,max_tokens=3000):

    client = OpenAI(api_key=API_KEY)

    completion = client.chat.completions.create(
        model=COMPLETION_MODEL,
        max_tokens = max_tokens,
        n = n,
        temperature = 0,
        messages=message_our
        )

    return completion.choices[0].message


def entity_extraction_func(text):
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY)

    system_prompt = """
        As an Operations Management Researcher and Natural Language Processing (NLP) Engineer, your primary task is to extract key information about suppliers from the provided text. Please follow these steps strictly:
        1 Entity Recognition: Identify and extract all supplier names present in the text. These are the names of companies or organizations mentioned as distinct entities in the text.
        2 Text Summary: Summarize the main activities or characteristics of each identified supplier based on the content of the text. Ensure that the summary accurately reflects the information in the text.
        Adhere to this format:
        {
            'Supplier Company Name': 'Summary of content about current Supplier',
            ...
        }.
        Do not add or change any content; simply fill in the relevant information.

        Example input text:
        "...Solar Solutions recently completed a large-scale solar energy project, which successfully increased the region's renewable energy supply..."
        Example output:
        { 'Solar Solutions': 'Completed a large-scale solar energy project, increasing the region's renewable energy supply'. }

    """

    user_prompt = f"Here is the text: \n {text}" 

    response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    )

    out_put = response.choices[0].message.content
    # print(out_put)

    try:

        # 使用正则表达式匹配可能的字典格式
        dict_match = re.search(r'\{.*?\}', out_put, re.DOTALL)
        # # 将匹配的文本中的单引号转换为双引号，并清理内部的双引号
        # dict_str = dict_match.group().replace("'", '"')
        # dict_str = re.sub(r'(?<!\\)"', '', dict_str)  # 移除非转义的双引号

        # 将匹配的文本处理为符合字典格式的字符串
        dict_str = dict_match.group()
        dict_str = re.sub(r"[^a-zA-Z0-9{}:,. '\"\[\]]", '', dict_str)  # 移除不合法的字符
        dict_str = re.sub(r'(?<!")\b\w+\b(?=":)', lambda x: '"' + x.group() + '"', dict_str)  # 确保键被双引号包围
        # 尝试解析字典
        data = ast.literal_eval(dict_str)
    
    except Exception as e:
        return {}
        # 可以在此处添加其他错误处理逻辑，如返回默认值或继续执行其他任务



    return data


def extract_and_save_data(text, path, company_name, entity_extraction_func):
    try:
        # 使用正则表达式匹配可能的字典格式
        dict_match = re.search(r'\{.*?\}', text, re.DOTALL)
        if dict_match:
            # 将匹配的文本中的单引号转换为双引号，并清理内部的双引号
            # dict_str = dict_match.group().replace("'", '"')
            # dict_str = re.sub(r'(?<!\\)"', '', dict_str)  # 移除非转义的双引号

            # 将匹配的文本处理为符合字典格式的字符串
            dict_str = dict_match.group()
            dict_str = re.sub(r"[^a-zA-Z0-9{}:,. '\"\[\]]", '', dict_str)  # 移除不合法的字符
            dict_str = re.sub(r'(?<!")\b\w+\b(?=":)', lambda x: '"' + x.group() + '"', dict_str)  # 确保键被双引号包围

            try:
                # 尝试解析字典
                data = ast.literal_eval(dict_str)
            except (SyntaxError, ValueError):
                # 如果解析失败，使用命名实体识别函数处理文本
                data = entity_extraction_func(text)
        else:
            # 如果没有匹配到字典格式，同样使用命名实体识别函数
            data = entity_extraction_func(text)

        # 创建 DataFrame
        df = pd.DataFrame(list(data.items()), columns=['Supplier', 'Content of Supplier'])

        # # 添加编号列
        # df.insert(0, 'Number', range(1, len(df) + 1))

        # # 构建文件路径
        # file_path = f'{path}/{company_name}_suppliers.csv'
        # 构建文件路径
        file_path = f'{path}/{company_name}.csv'

        # 检查路径是否存在，如果不存在，则创建它
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 检查文件是否存在，根据情况选择写入模式
        if os.path.exists(file_path):
            # 文件存在，使用追加模式
            df.to_csv(file_path, mode='a', header=False, index=False, sep="\t")
        else:
            # 文件不存在，使用写入模式
            df.to_csv(file_path, index=False, sep="\t")
    except Exception as e:
        pass


def read_and_replace_newlines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # 读取文件内容
        text = file.read()

    # 删除额外的空白字符和无用符号
    text = re.sub(r'\n+', '\n', text)  # 替换多个连续换行符为单个换行符
    text = re.sub(r'\s+\n', '\n', text)  # 删除行末的空白字符
    text = re.sub(r'\n\s+', '\n', text)  # 删除行首的空白字符
    text = re.sub(r'[^A-Za-z0-9.,;:\'"\(\)\[\]\n]+', ' ', text)  # 删除除基本标点符号和数字字母外的所有字符

    return text


def split_text_into_parts(text, num_parts=10):
    # 计算每部分的大致长度
    part_length = len(text) // num_parts

    # 初始化结果列表和当前部分的开始索引
    parts = []
    start = 0

    for _ in range(num_parts - 1):
        # 计算这部分应当结束的大致位置
        end = start + part_length

        # 如果不是在文本末尾，尽量在句子或单词结束处分割
        if end < len(text):
            while end < len(text) and text[end] not in " .,;?!":
                end += 1

        # 截取当前部分
        parts.append(text[start:end])

        # 更新下一部分的开始位置
        start = end

    # 添加最后一部分
    parts.append(text[start:])

    return parts



folder_path = './OriginalReports_Convert_Txts'  # 替换为您的PDF文件所在的文件夹路径，由1_1_convert_pdf2txt.py从产生


txt_path_list = os.listdir(f"{folder_path}")
txt_path_list = sorted(txt_path_list)

print(txt_path_list)

# xxx


# 断点重续
try:
    existed_reports = set()
    existed_report_list = os.listdir(f"./Supply_After_GPT/{COMPLETION_MODEL}")
    for existed_report in existed_report_list[:-1]:
        # existed_report = existed_report.replace("_suppliers", "")
        existed_report = existed_report.split(".")[0]
        existed_reports.add(existed_report)
    print(existed_reports)

    if len(existed_report_list) >= 1:
        last_report = existed_report_list[-1] # 删除，重新生成，以保证完整性
        import os
        last_file_path = f"./Supply_After_GPT/{COMPLETION_MODEL}/{last_report}"# 替换为要删除的文件的路径
        # print(last_file_path)
        # 检查文件是否存在
        if os.path.exists(last_file_path):
            os.remove(last_file_path)
            print(f"File {last_file_path} has been deleted.")
        else:
            print(f"File {last_file_path} does not exist.")

except:
    pass


for txt_path in txt_path_list:
    company_name = txt_path.replace(".txt", "")
    print("company_name", txt_path)
    if company_name in existed_reports:
        continue
    modified_text = read_and_replace_newlines(f"{folder_path}/{txt_path}")

    modified_text_parts = split_text_into_parts(modified_text)

    system_prompt = """
        As an operations management researcher, \
        your task is to extract the names of suppliers from a company's provided responsibility report and summarize the overall situation of the supplier as mentioned in the report.\
        Strictly adhere to the following example format, without adding or altering any content:\
        {
            'Supplier Company Name': 'Summary of content about current Supplier',
            ...
        }.\
        Here is an output example:\
        {
            'Umicore Finland Oy': 'Conformant refiner sourcing cobalt for Gigafactory Nevada and Fremont external cell sourcing, located in Finland.',
            'Murrin Murrin Nickel Cobalt Plant': 'Conformant refiner sourcing cobalt for Gigafactory Nevada and Fremont external cell sourcing, located in Australia.',
            ...
        }.\
        If it does not exist any supplier companies, an empty {} is returned.\
        Any deviation from this format will not be accepted. \
        Any information beyond this format will be disregarded. \
        Please ensure your response strictly follows this structure. \
        Extract the names of the suppliers accurately based on the report's content, and output them in the specified format.

"""

    for modified_text_item in modified_text_parts:

        message_our = [
            {"role": "system", "content": system_prompt}
        ]


        user_prompt = f"{modified_text_item}" 
        user_prompt_dic = {"role": "user", "content": user_prompt}
        message_our.append(user_prompt_dic)

        attempts = 0
        success = False

        while attempts < 5 and not success:
            try:
                output = chat_gpt_turbo(message_our, COMPLETION_MODEL).content
                success = True
                print("output", output)
            except:
                print('no response from gpt')
                time.sleep(5)
                attempts += 1
                if attempts == 3:
                    break


        import re
        if re.match(r'^\s*\{\s*\}\s*$', output) is None:
            path = f"./Supply_After_GPT/{COMPLETION_MODEL}"
            extract_and_save_data(output, path, company_name,entity_extraction_func)


