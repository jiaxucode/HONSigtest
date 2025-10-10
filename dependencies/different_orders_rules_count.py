# 对不同阶数的rules进行计数, 存储

import numpy as np
import pandas as pd
from collections import defaultdict
import re
import csv
import traceback
import os





def RuleStats(Rules):
    '''
    依据Rules，统计rules总数，不同阶数的rules在网络中出现的次数,把不同阶数的rules放在一个字典中.
    :param Rules:从轨迹数据中提取的higher-order dependencies rules, eg.{
    (89,): {99: 0.5132382892057027, 80: 0.48676171079429736},
    (78,): {88: 0.4785643070787637, 79: 0.5214356929212363},
    (78, 88): {98: 0.5147679324894515, 89: 0.48523206751054854},
    (78, 88, 89): {80: 0.4911504424778761, 99: 0.5088495575221239}}
    '''
    Rules_1st_order = defaultdict(dict)  # {A1:{},..., An:{}}#一阶依赖
    Rules_2nd_order = defaultdict(dict)  # {A1:{},..., An:{}}#二阶依赖
    Rules_3nd_order = defaultdict(dict)  # {A1:{},..., An:{}}#三阶依赖
    Rules_4th_order = defaultdict(dict)  # {A1:{},..., An:{}}#四阶依赖
    Rules_5th_order = defaultdict(dict)  # {A1:{},..., An:{}}#五阶依赖
    Rules_6th_order = defaultdict(dict)  # {A1:{},..., An:{}}#五阶依赖

    orders = defaultdict(int)#存储不同阶数的依赖的个数{1: 200, 2:20, 3:12}
    NumRules = 0#网络中pattern的总数
    for key in Rules:#key: pattern的source节点('33',)
        for val in Rules[key]:#val:'34'
            order = len(key)
            orders[order] += 1 #orders: 统计高阶节点阶数出现的次数{1: 200, 2:20, 3:12}
            NumRules += 1 #网络中pattern的总数

            if order == 1:
                Rules_1st_order[key] = Rules[key]  # pattern key 赋给Distribution字典
            elif order == 2:#存储二阶模式
                Rules_2nd_order[key] = Rules[key] # pattern key 赋给Distribution字典
            elif order == 3:#存储三阶模式
                Rules_3nd_order[key] = Rules[key] # pattern key 赋给Distribution字典
            elif order == 4:#存储四阶模式
                Rules_4th_order[key] = Rules[key] # pattern key 赋给Distribution字典
            elif order == 5:#存储五阶模式
                Rules_5th_order[key] = Rules[key] # pattern key 赋给Distribution字典
            elif order == 6:#存储五阶模式
                Rules_6th_order[key] = Rules[key] # pattern key 赋给Distribution字典
            # if order == 5:#存储五阶模式
            #     Rules_5th_order[key]=Rules[key] # pattern key 赋给Distribution字典

    list_orders = list(orders)#字典中的key转换为列表, [1, 2, 3]
    keys = sorted(list(orders))#[1, 2, 3]
    # print('Total rules:', NumRules)
    # for key in keys:
    #     print('Extracted', orders[key], 'rules of order', key)#输出每种阶数的rules的个数

    # return Rules_1st_order, Rules_2nd_order #最高阶数为2
    # return Rules_1st_order, Rules_2nd_order, Rules_3nd_order #最高阶数为3
    # return Rules_1st_order, Rules_2nd_order, Rules_3nd_order, Rules_4th_order #最高阶数为4
    return Rules_1st_order, Rules_2nd_order, Rules_3nd_order, Rules_4th_order, Rules_5th_order
    # return Rules_1st_order, Rules_2nd_order, Rules_3nd_order, Rules_4th_order, Rules_5th_order, Rules_6th_order






def sort_dependencies(input_file, output_file):
    """
    从单列CSV文件中提取不同阶数的依赖关系，并以有序方式输出到新的CSV文件

    参数:
    input_file: 输入的CSV文件路径，包含一列依赖关系
    output_file: 输出的CSV文件路径
    """
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_file):
            print(f"错误: 找不到输入文件 '{input_file}'")
            return

        # 读取CSV文件，只有一列数据
        df = pd.read_csv(input_file, header=None, names=['dependency'])
        print(f"成功读取文件 {input_file}，共 {len(df)} 行数据")

        # 查看前5行数据，了解格式
        print("前5行数据:")
        for i in range(min(5, len(df))):
            print(f"  {i + 1}: {df.iloc[i, 0]}")

        # 创建三个列表分别存储一阶、二阶和三阶依赖关系
        first_order = []  # 一阶依赖关系
        second_order = []  # 二阶依赖关系
        third_order = []  # 三阶依赖关系
        fourth_order = []# 四阶依赖关系
        fifth_order = []# 五阶依赖关系
        sixth_order = []  # 六阶依赖关系

        # 定义用于匹配不同阶数依赖关系的模式
        # 一阶：单个数字在 => 左侧
        # 二阶：两个数字在 => 左侧
        # 三阶：三个数字在 => 左侧

        # 遍历每一行依赖关系
        for index, row in df.iterrows():
            # 获取依赖关系字符串
            dependency_str = str(row['dependency']).strip()

            # 跳过空行或无效行
            if not dependency_str or "=>" not in dependency_str:
                continue

            # 分割依赖关系为左右两部分
            parts = dependency_str.split("=>")
            if len(parts) != 2:
                print(f"警告：在第 {index + 1} 行找到无效格式: '{dependency_str}'")
                continue

            left_part = parts[0].strip()
            right_part = parts[1].strip()

            # 分割左右部分的数字
            left_nums = left_part.split()
            right_nums = right_part.split()

            # 确保右部分至少有2个数字(依赖目标和频率)
            if len(right_nums) < 2:
                print(f"警告：在第 {index + 1} 行右侧数据不完整: '{right_part}'")
                continue

            # 提取右侧的依赖目标和频率
            target = right_nums[0]
            frequency = right_nums[1]

            # 根据左侧数字的数量确定阶数
            if len(left_nums) == 1:
                # 一阶依赖关系
                first_order.append({
                    'order': 1,
                    'left': left_nums[0],
                    'right': target,
                    'frequency': frequency
                })
            elif len(left_nums) == 2:
                # 二阶依赖关系
                second_order.append({
                    'order': 2,
                    'left1': left_nums[0],
                    'left2': left_nums[1],
                    'right': target,
                    'frequency': frequency
                })
            elif len(left_nums) == 3:
                # 三阶依赖关系
                third_order.append({
                    'order': 3,
                    'left1': left_nums[0],
                    'left2': left_nums[1],
                    'left3': left_nums[2],
                    'right': target,
                    'frequency': frequency
                })
            elif len(left_nums) == 4:
                # 四阶依赖关系
                fourth_order.append({
                    'order': 4,
                    'left1': left_nums[0],
                    'left2': left_nums[1],
                    'left3': left_nums[2],
                    'left4': left_nums[3],
                    'right': target,
                    'frequency': frequency
                })
            elif len(left_nums) == 5:
                # 五阶依赖关系
                fifth_order.append({
                    'order': 5,
                    'left1': left_nums[0],
                    'left2': left_nums[1],
                    'left3': left_nums[2],
                    'left4': left_nums[3],
                    'left5': left_nums[4],
                    'right': target,
                    'frequency': frequency
                })
            elif len(left_nums) == 6:
                # 六阶依赖关系
                sixth_order.append({
                    'order': 6,
                    'left1': left_nums[0],
                    'left2': left_nums[1],
                    'left3': left_nums[2],
                    'left4': left_nums[3],
                    'left5': left_nums[4],
                    'left6': left_nums[5],
                    'right': target,
                    'frequency': frequency
                })
            else:
                print(f"警告：在第 {index + 1} 行找到未知阶数依赖关系: '{dependency_str}'")

        # 打印提取的依赖关系数量
        print(f"\n提取结果:")
        print(f"一阶依赖关系: {len(first_order)} 个")
        print(f"二阶依赖关系: {len(second_order)} 个")
        print(f"三阶依赖关系: {len(third_order)} 个")
        print(f"四阶依赖关系: {len(fourth_order)} 个")
        print(f"五阶依赖关系: {len(fifth_order)} 个")
        print(f"六阶依赖关系: {len(sixth_order)} 个")

        # 如果没有提取到任何依赖关系，给出警告
        if len(first_order) + len(second_order) + len(third_order) == 0:
            print("警告：未提取到任何依赖关系，请检查输入文件格式")
            return

        # 将结果写入新的CSV文件
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # 写入标题行
            writer.writerow(['依赖关系阶数', '依赖关系', '频率'])

            # 写入一阶依赖关系
            for item in first_order:
                writer.writerow([
                    item['order'],
                    f"{item['left']} => {item['right']}",
                    item['frequency']
                ])

            # 写入二阶依赖关系
            for item in second_order:
                writer.writerow([
                    item['order'],
                    f"{item['left1']} {item['left2']} => {item['right']}",
                    item['frequency']
                ])

            # 写入三阶依赖关系
            for item in third_order:
                writer.writerow([
                    item['order'],
                    f"{item['left1']} {item['left2']} {item['left3']} => {item['right']}",
                    item['frequency']
                ])
            # 写入四阶依赖关系
            for item in fourth_order:
                writer.writerow([
                    item['order'],
                    f"{item['left1']} {item['left2']} {item['left3']} {item['left4']} => {item['right']}",
                    item['frequency']
                ])
            # 写入五阶依赖关系
            for item in fifth_order:
                writer.writerow([
                    item['order'],
                    f"{item['left1']} {item['left2']} {item['left3']} {item['left4']} {item['left5']} => {item['right']}",
                    item['frequency']
                ])
            # 写入六阶依赖关系
            for item in sixth_order:
                writer.writerow([
                    item['order'],
                    f"{item['left1']} {item['left2']} {item['left3']} {item['left4']} {item['left5']} {item['left6']} => {item['right']}",
                    item['frequency']
                ])

        print(f"已将结果保存到 {output_file}")

    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()






