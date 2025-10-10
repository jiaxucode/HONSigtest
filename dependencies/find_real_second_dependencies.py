import pandas as pd
import re
import pickle
from collections import defaultdict


# 读取CSV文件
def find_matching_entries(csv_path, pickle_path, output_csv_path):
    # 读取CSV文件
    df = pd.read_csv(csv_path)
    print(f"{csv_path}文件大小: {df.shape}")

    # 从pickle文件加载字典(real second-order transition probability)
    with open(pickle_path, 'rb') as f:
        transition_dict = pickle.load(f)
    print(f"二阶转移概率字典键数量: {len(transition_dict)}")

    # 存储满足条件的结果
    matching_entries = defaultdict(lambda: defaultdict(int))
    # 记录修改的元素的数量
    modified_count = 0

    # 遍历CSV文件的每一行
    for row_idx, row in df.iterrows():
        target_node = row['target']  # 假设第一列是target/行名

        # 遍历每一列
        for col_name in df.columns[1:]:  # 跳过第一列
            value = row[col_name]
            # 检查值是否为1
            if value == 2:
                # 解析列名 "(i, j)"
                col_match = re.match(r"\((\d+),\s*(\d+)\)", col_name)
                if col_match:
                    i = int(col_match.group(1))
                    j = int(col_match.group(2))#元组(i,j)

                    # 检查字典中是否有对应的键值对
                    # 格式1: transition_dict[(i,j)][target_node] > 0
                    dict_key1 = (i, j)
                    if dict_key1 in transition_dict and target_node in transition_dict[dict_key1] and transition_dict[dict_key1][
                        target_node] > 0:
                        matching_entries[dict_key1][target_node] = 2
                    else:
                        df.at[row_idx, col_name] = 0
                        modified_count += 1
    print(f"修改了 {modified_count} 个不满足条件的元素值为0")
    # 保存修改后的DataFrame到新的CSV文件
    df.to_csv(output_csv_path, index=False)
    print(f"已将修改后的数据保存到 {output_csv_path}")

    return matching_entries


