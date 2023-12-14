import os
import shutil

def move_files(source_folder, destination_folder):
    for root, dirs, files in os.walk(source_folder):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            for file_name in os.listdir(dir_path):
                if file_name.endswith('.pdf'):  # 只处理PDF文件
                    file_path = os.path.join(dir_path, file_name)
                    new_file_name = dir_name.replace(' ', '_') + '-' + file_name.replace(',', '-').replace('&', '-')
                    print(f"{new_file_name}")
                    new_file_path = os.path.join(destination_folder, new_file_name)
                    shutil.move(file_path, new_file_path)
                    print(f"Moved {file_path} to {new_file_path}")

# 指定源文件夹和目标文件夹的路径
source_folder = r"data\report_pdf"
destination_folder = r"data\PDF"

# 调用函数移动文件
move_files(source_folder, destination_folder)