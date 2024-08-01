import json
import os

# 设定包含JSON文件的文件夹路径
folder_path = 'new'

# 初始化一个空列表，用于存储所有JSON文件的数据
combined_list = []

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    # 检查文件扩展名是否为.json
    if filename.endswith('.json'):
        # 构建文件的完整路径
        file_path = os.path.join(folder_path, filename)
        # 打开并读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as file:
            # 将读取的数据添加到合并列表中
            combined_list.extend(json.load(file))

# 将合并后的列表写入新的JSON文件
new_json_file = 'combined_data.json'
with open(new_json_file, 'w', encoding='utf-8') as file:
    json.dump(combined_list, file, ensure_ascii=False, indent=4)

print(f'All JSON files have been combined into {new_json_file}')