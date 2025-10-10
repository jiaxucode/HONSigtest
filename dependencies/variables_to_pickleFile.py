# 把内存中的variable存储到.pickle file中, 把存储到.pickle file的变量装载到内存中
import pickle
import dill as pickle
import os
from collections import defaultdict
import numpy as np
def SaveVariablestoPickleFile(save_contents, filename):
    '''
    把内存中的variable存储到.pickle file中
    :param save_contents:内存中的变量
    :param filename:保存变量的地址
    :return:
    '''
    with open(filename, 'wb') as f:
        pickle.dump(save_contents, f)#save_contents: [X_train, y_train]
def LoadVariablestoPickleFile(filename):
    '''
    把存储到.pickle file的变量装载到内存中
    :param filename:
    :return:
    '''
    with open(filename, 'rb') as f:
        var_load_into = pickle.load(f)
    return var_load_into

def read_all_defaultdictPickleFile(folder_path):
    '''
    读取一个文件夹下的所有PickleFile, 并合并为一个变量
    :param folder_path:
    :return:global_variable
    '''
    global_variable = defaultdict(lambda: defaultdict(list))
    for filename in os.listdir(folder_path):
        if filename.endswith('.pickle'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'rb') as file:
                local_variable = LoadVariablestoPickleFile(file_path)

                for dependency in local_variable:
                    for target in local_variable[dependency]:
                        specified_proba = local_variable[dependency][target]
                        global_variable[dependency][target].append(specified_proba)  # 更新数据结构
    # 先按照tuple内的第一位排序，然后按tuple的第二个元素等对字典的元素排序
    sorted_global_variable = dict(sorted(global_variable.items(), key=lambda data: data[0]))
    return sorted_global_variable


def merge_pickled_statindex(pickle_files, default_factory=dict):
    """
    合并多个pickle文件中的defaultdict结构

    Args:
        pickle_files: 包含pickle文件路径的列表
        default_factory: defaultdict的默认工厂函数

    Returns:
        合并后的defaultdict
    """
    # 创建一个新的defaultdict用于存储合并结果
    merged_dict = defaultdict(default_factory)

    # 遍历所有pickle文件
    for file_path in pickle_files:
        try:
            with open(file_path, 'rb') as f:
                current_dict = pickle.load(f)
                # 确保加载的对象是defaultdict类型
                if not isinstance(current_dict, defaultdict):
                    raise TypeError(f"文件 {file_path} 中的对象不是defaultdict类型")

                # 合并字典
                for key, value in current_dict.items():
                    if key not in merged_dict:
                        # 如果key不存在,直接添加
                        merged_dict[key] = value
                    else:
                        # 如果key已存在,则根据值的类型进行合并
                        if isinstance(value, dict):
                            # 对于嵌套的字典,递归合并
                            existing_value = merged_dict[key]
                            for k, v in value.items():
                                if k in existing_value:
                                    # 对于stats数据,合并统计值
                                    if k in ['mean', 'standard_deviation', 'z_score', 'p-val']:
                                        existing_value[k] = np.mean([existing_value[k], v])
                                    elif k in ['95%CI', '99%CI', '90%CI']:
                                        # 对于置信区间,取并集
                                        existing_ci = existing_value[k]
                                        new_ci = v
                                        merged_ci = (
                                            min(existing_ci[0], new_ci[0]),
                                            max(existing_ci[1], new_ci[1])
                                        )
                                        existing_value[k] = merged_ci
                                else:
                                    existing_value[k] = v
                        else:
                            # 对于其他类型的值,取平均值
                            merged_dict[key] = (merged_dict[key] + value) / 2

        except FileNotFoundError:
            print(f"警告: 文件 {file_path} 不存在")
        except Exception as e:
            print(f"处理文件 {file_path} 时发生错误: {str(e)}")

    return merged_dict

def merge_pickled_rules(pickle_files, default_factory=dict):
    """
    合并多个pickle文件中的defaultdict结构

    Args:
        pickle_files: 包含pickle文件路径的列表
        default_factory: defaultdict的默认工厂函数

    Returns:
        合并后的defaultdict
    """
    # 创建一个新的defaultdict用于存储合并结果
    merged_dict = defaultdict(default_factory)

    # 遍历所有pickle文件
    for file_path in pickle_files:
        try:
            with open(file_path, 'rb') as f:
                current_dict = pickle.load(f)
                # 合并字典
                for key, value in current_dict.items():
                    if key not in merged_dict:
                        # 如果key不存在,直接添加
                        merged_dict[key] = value
        except FileNotFoundError:
            print(f"警告: 文件 {file_path} 不存在")
        except Exception as e:
            print(f"处理文件 {file_path} 时发生错误: {str(e)}")

    return merged_dict


