import pandas as pd
import os
import re



# def standardize_supplier_name(name):
#     """ 标准化供应商名称，可根据需要调整正则表达式 """
#     # 示例：将简写转换为完整名称，如“Tesla”转换为“Tesla Inc.”
#     # 注意：这里的规则需要根据具体情况来定制
#     name = re.sub(r'\bTesla\b', 'Tesla Inc.', name)
#     return name

def process_supplier_data(df):

    # # 标准化供应商名称
    # df['Supplier'] = df['Supplier'].apply(standardize_supplier_name)

    # 确保所有的内容都是字符串类型
    df['Content of Supplier'] = df['Content of Supplier'].astype(str)


    # 合并相同的供应商行，拼接内容
    df = df.groupby('Supplier')['Content of Supplier'].apply(lambda x: ' '.join(x)).reset_index()

    # 在结尾添加一行编号
    df['Number'] = range(1, len(df) + 1)

    return df



def process_all(folder_path):

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):  # 确保文件是CSV格式

            if filename.split(".")[0].endswith('CSR'):
            
                company_name = filename.split(".")[0].split("_")[1]
                year = filename.split(".")[0].split("_")[2]
                report_type = filename.split(".")[0].split("_")[-1]
                # print(company_name)
                # print(year)
                # print(report_type)
            elif filename.split(".")[0].endswith('10K'):
                company_name = filename.split(".")[0].split("-")[0]
                year = filename.split(".")[0].split("_")[-2][:4]
                report_type = filename.split(".")[0].split("_")[-1]


            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path, sep="\t")

            # 合并相同的
            result_df = process_supplier_data(df)

            # 把company_name, year, type加到result_df后，每一行的值都相同

            # 向结果DataFrame中添加公司名、年份和类型的列
            result_df['Company'] = company_name
            result_df['Year'] = year
            result_df['Report_type'] = report_type

            # 需要代码补全

            # 可以选择将结果保存回文件
            new_folder_path = f"{folder_path}_post"
            new_file_path = os.path.join(new_folder_path, f"{filename}")
            # 检查路径是否存在，如果不存在，则创建它
            directory = os.path.dirname(new_file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            result_df.to_csv(new_file_path, index=False,sep="\t")


process_all("./Supply_After_GPT/gpt-3.5-turbo-1106")