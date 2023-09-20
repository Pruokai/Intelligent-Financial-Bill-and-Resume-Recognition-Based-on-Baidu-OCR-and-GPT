# -*- coding: utf-8 -*-
import pandas as pd
import os
import re
import openai
import json
from tqdm import tqdm
import pandas as pd



# Z2U
openai.api_key = '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'
os.environ["OPENAI_API_KEY"] = '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'

def openai_api_call(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."\
                                              "Knowledge cutoff: 2021-09"\
                                              "Current date: [current date]"},
                {"role": "user", "content":  prompt},
            ],
        )
    return response.choices[0]['message']['content'].strip()


def construct_prompt(json_data):
    prompt = f"""
    {json_data}
解析上述信息，获取以下数据：
"姓名","性别","手机号","电子邮箱","出生日期","学历","毕业院校1（最近）","学业的起止时间1","毕业院校2","学业的起止时间2","工作单位1（最近）","工作起止时间1","工作单位2","工作起止时间2","工作单位3","工作起止时间3","期望薪资","岗位名称"，输出格式如下：
姓名：
性别：
如果没有相关内容，则填写"     "，不要填写其他内容，请注意，不需要其他内容，不需要任何解释和说明,不要添加其他任何东西,不要给任何代码。
"""
    # " Please use your imagination to continue the above script, writing the next five shots, and specify the type of shot for each scene.
    # No less than 100 words per shot.
    # Use Chinese to output."
    return prompt

# 正则匹配模式，用于提取信息
patterns = {
    "姓名": r"姓名：(.*?)\n",
    "性别": r"性别：(.*?)\n",
    "手机号": r"手机号：(.*?)\n",
    "电子邮箱": r"电子邮箱：(.*?)\n",
    "出生日期": r"出生日期：(.*?)\n",
    "学历": r"学历：(.*?)\n",
    "毕业院校1（最近）": r"毕业院校1（最近）：(.*?)\n",
    "学业的起止时间1": r"学业的起止时间1：(.*?)\n",
    "毕业院校2": r"毕业院校2：(.*?)\n",
    "学业的起止时间2": r"学业的起止时间2：(.*?)\n",
    "工作单位1（最近）": r"工作单位1（最近）：(.*?)\n",
    "工作起止时间1": r"工作起止时间1：(.*?)\n",
    "工作单位2": r"工作单位2：(.*?)\n",
    "工作起止时间2": r"工作起止时间2：(.*?)\n",
    "工作单位3": r"工作单位3：(.*?)\n",
    "工作起止时间3": r"工作起止时间3：(.*?)\n",
    "期望薪资": r"期望薪资：(.*?)\n",
    "岗位名称": r"岗位名称：(.*?)\n",
}


def parse_json(json_data):
    prompt = construct_prompt(json_data)
    response = openai_api_call(prompt)
    return response

# 文件夹路径
txt_folder = 'E:/project/简历识别/txt'  # Update this path to your .txt files folder

parsed_data_list = []

# 获取文件夹中所有的txt文件名
txt_files = [f for f in os.listdir(txt_folder) if f.endswith('.txt')]

# 循环处理每个txt文件
for txt_file in txt_files:
    with open(os.path.join(txt_folder, txt_file), 'r', encoding='utf-8') as f:
        txt_data = f.read()  # 读取文本数据

    # 构建提示内容
    prompt = construct_prompt(txt_data)

    # 检查输入消息的长度是否超过最大上下文长度
    if len(prompt) > 4000:  # 调整此限制以匹配模型的最大上下文长度
        print(f"Input message for {txt_folder + txt_file} is too long. Skipping.")
        continue

    # 解析文本数据
    parsed_data = parse_json(prompt)
    print(parsed_data)
    # 使用正则匹配提取信息
    info_dict = {}
    for key, pattern in patterns.items():
        value = re.search(pattern, parsed_data)
        info_dict[key] = value.group(1).strip() if value else ""

    # 将提取的信息添加到列表中
    parsed_data_list.append(info_dict)

# 将提取的信息输出到Excel文件
output_excel = "TEST2.xlsx"
all_extracted_data = pd.DataFrame(parsed_data_list)
all_extracted_data.to_excel(output_excel, index=False, engine="openpyxl")

print(f"Extracted information has been saved to {output_excel}")