# 计算每个数据集的不同阶数的转移概率分布情况

import pandas as pd
import numpy as np
from dependencies.ExtractVariableOrderRules import *
from dependencies.variables_to_pickleFile import *
from dependencies.different_orders_rules_count import *
from dependencies.input_output_file import *
def cal_first_order_trans_pro_matrix(trajectories, NetType):
    '''
    计算轨迹数据集的一阶转移概率矩阵
    :param trajectories: 轨迹数据集
    :return: first_order_trans_pro_matrix
    '''
    num_pages = max(max(trajectory) for trajectory in trajectories) + 1 #找到所有轨迹中page编号的最大值(99)+1
    # num_pages = 4
    first_order_trans_count_matrix = np.zeros((num_pages, num_pages), dtype=int)#创建一个状态转移计数矩阵,每个元素表示从当前状态到下一个状态的转移次数

    for trajectory in trajectories:
        for i in range(len(trajectory) - 1):
            prev = trajectory[i]
            page = trajectory[i + 1]
            prev = int(trajectory[i])-1
            page = int(trajectory[i + 1])-1
            first_order_trans_count_matrix[prev][page] += 1
    first_order_trans_pro_matrix = first_order_trans_count_matrix / first_order_trans_count_matrix.sum(axis=1, keepdims=True)

    # 1. 判断数据集的最高阶数
    if NetType == NetType_mo1:
        net_type_suffix = 'mo1'
    elif NetType == NetType_mo2:
        net_type_suffix = 'mo2'
    elif NetType == NetType_mo3:
        net_type_suffix = 'mo3'
    else:
        net_type_suffix = 'mo4'


    # 2. 将一阶转移概率矩阵输出为csv
    # 2.1 创建一个DataFrame对象
    df = pd.DataFrame(first_order_trans_pro_matrix)
    # 2.2 将DataFrame保存为CSV文件
    df.to_csv(OutputCSVFolder + 'FirstOrderTransitionProbability-' + net_type_suffix + '.csv')
    # 3. 将一阶转移概率矩阵保存为.npy文件
    np.save(save_first_order_rule_variable_direcname + 'real/' + 'Rules_1st_order_' + net_type_suffix + '.npy', first_order_trans_pro_matrix)
    return first_order_trans_pro_matrix, num_pages

def dict_to_array(rules_x_order, rules_x_order_zero_array):
    '''
    使用numpy数组表示不同阶数的rules的概率分布
    :param rules_x_order: defaultdict结构的rules, eg.{
    (78, 88): {98: 0.5147679324894515, 89: 0.48523206751054854},}
    :param rules_x_order_zero_array:
    :return: rules_x_order_array
    '''
    rules_x_order_array = rules_x_order_zero_array
    # 1. 获得数组的维数
    dim = len(rules_x_order_zero_array.shape)
    # 2. 遍历dict，获得numpy数组
    for key in rules_x_order:#key: pattern的source节点(78, 88)
        for tar in rules_x_order[key]:

            index_tuple_1 = tuple(map(lambda x: int(x)-1, key))
            tar_index = int(tar) -1

            # 确定数组元素的位置，创建一个新的元组，包含原始元组的元素和新元素
            # element_position_tuple = key + (tar,)
            element_position_tuple = index_tuple_1 + (tar_index,)
            # 为特定位置的数组元素赋值

            rules_x_order_array[element_position_tuple] = rules_x_order[key][tar]
    return rules_x_order_array




save_trajectories_variable_direcname = './variable/trajectories/20231114/'
save_first_order_rule_variable_direcname = './variable/rules/20231114/1st-order/'
save_second_order_rule_variable_direcname = './variable/rules/20231114/2nd-order/'
save_third_order_rule_variable_direcname = './variable/rules/20231114/3rd-order/'
save_fourth_order_rule_variable_direcname = './variable/rules/20231114/4th-order/'
save_fifth_order_rule_variable_direcname = './variable/rules/20231114/5th-order/'
save_higher_order_rule_variable_direcname = './variable/rules/20231114/higher-order/'
OutputCSVFolder = './data/trajectories/20231114/' # ./

# save_trajectories_variable_direcname = './variable/trajectories/20231217/'
# save_first_order_rule_variable_direcname = './variable/rules/20231217/1st-order/'
# save_second_order_rule_variable_direcname = './variable/rules/20231217/2nd-order/'
# save_third_order_rule_variable_direcname = './variable/rules/20231217/3rd-order/'
# save_fourth_order_rule_variable_direcname = './variable/rules/20231217/4th-order/'
# save_fifth_order_rule_variable_direcname = './variable/rules/20231217/5th-order/'
# save_higher_order_rule_variable_direcname = './variable/rules/20231217/higher-order/'
# OutputCSVFolder = './data/trajectories/20231217/' # ./

# save_trajectories_variable_direcname = './variable/trajectories/20231229/'
# save_first_order_rule_variable_direcname = './variable/rules/20231229/1st-order/'
# save_second_order_rule_variable_direcname = './variable/rules/20231229/2nd-order/'
# save_third_order_rule_variable_direcname = './variable/rules/20231229/3rd-order/'
# save_fourth_order_rule_variable_direcname = './variable/rules/20231229/4th-order/'
# save_fifth_order_rule_variable_direcname = './variable/rules/20231229/5th-order/'
# save_higher_order_rule_variable_direcname = './variable/rules/20231229/higher-order/'
# OutputCSVFolder = './data/trajectories/20231229/'


NetType_mo1 = '1st-order'
NetType_mo2 = '2nd-order'
NetType_mo3 = '3rd-order'
NetType_mo4 = '4th-order'

MinSupport = 1 # 每个pattern出现的最少次数


#---------------------------------------处理clickstream-simulated-4th-order.csv--------------------------------------------
# 1. 计算clickstream-simulated-4th-order.csv的一阶转移概率矩阵
trajectories_simulated_4th_order = np.load(save_trajectories_variable_direcname + 'clickstream-simulated-' + NetType_mo4 + '.npy')
Rules_1st_order_mo4, dim_len = cal_first_order_trans_pro_matrix(trajectories_simulated_4th_order, NetType_mo4)
trajectories_simulated_4th_order = np.load(save_trajectories_variable_direcname + 'clickstream-simulated-' + NetType_mo4 + '.npy')
# 2. 提取higher-order dependencies
Rules_mo4 = ExtractRules(trajectories_simulated_4th_order, 5, MinSupport)# 二阶依赖的概率分布
SaveVariablestoPickleFile(Rules_mo4, save_higher_order_rule_variable_direcname + 'real/' + 'Rules_mo4.pickle')
# 3. 提取不同阶数的rules的概率分布
(Rules_1st_order_mo4, Rules_2nd_order_mo4, Rules_3rd_order_mo4, Rules_4th_order_mo4, Rules_5th_order_mo4) = RuleStats(Rules_mo4)
SaveVariablestoPickleFile(Rules_1st_order_mo4, save_first_order_rule_variable_direcname + 'real/' + 'Rules_1st_order_mo4.pickle')
SaveVariablestoPickleFile(Rules_2nd_order_mo4, save_second_order_rule_variable_direcname + 'real/' + 'Rules_2nd_order_mo4.pickle')
SaveVariablestoPickleFile(Rules_3rd_order_mo4, save_third_order_rule_variable_direcname + 'real/' + 'Rules_3rd_order_mo4.pickle')
SaveVariablestoPickleFile(Rules_4th_order_mo4, save_fourth_order_rule_variable_direcname + 'real/' + 'Rules_4th_order_mo4.pickle')
SaveVariablestoPickleFile(Rules_5th_order_mo4, save_fifth_order_rule_variable_direcname + 'real/' + 'Rules_5th_order_mo4.pickle')
print("!")

# Rules_mo4 = LoadVariablestoPickleFile(r"D:\PycharmProjects\HONSigTest\simulation-test\variable\rules\20231114\higher-order\real\Rules_mo4.pickle")
# first_order_trans_pro = np.load(r"D:\PycharmProjects\HONSigTest\simulation-test\variable\rules\20231114\1st-order\real\Rules_1st_order_mo2.npy" )
# print("!")


