# 对simulation data的高阶依赖的转移概率进行显著性统计检验
# 根据一阶转移概率+二阶转移概率+....矩阵，生成1000(csv files)*1000(1csv~1000 records) trajectories.

from webclickstream_tools_grid100 import Webclickstream
import numpy as np
from dependencies.variables_to_pickleFile import *
import pandas as pd
import csv
from dependencies.ExtractVariableOrderRules import *
from dependencies.different_orders_rules_count import *
from significancetest.ExtractElementsDistributions import *
from dependencies.rules_related_functions import *
from multiprocessing import Pool
import time
import os, psutil

def Simulate_Webclickstream_Trajectories(NetType):
    '''
    生成合成的轨迹，输出轨迹数据组成的数据框
    :return:df_trajectories:包含轨迹编号和轨迹；trajectories:轨迹组成的二维列表
    '''
    trajectories = []
    for id in range(1, trajectories_num+1):
        # Create a new customer object
        new_trajectory = Webclickstream(id, NetType)
        all_states = list(new_trajectory.gen)#将生成器转换为列表,可以一次性访问所有生成的元素，并将它们存储起来.生成器一次只产生一个元素，仅支持一次性迭代。
        # 一次性产生整条轨迹
        trajectories.append(new_trajectory.history)

    trajectories_list = []
    for trajectory in trajectories:
        trajectories_list.append(' '.join(map(str, trajectory)))
    d1 = {'trajectory_id': range(1, trajectories_num + 1), 'trajectory': trajectories_list}
    df_trajectories = pd.DataFrame(d1)
    return df_trajectories, trajectories

def WriteTrajectories(df_trajectories, NetType, iteration, OutputTrajectoriesMoFolder):
    '''
    把合成的轨迹数据输出为CSV文件
    :param df_trajectories: 轨迹数据生成的数据框
    :param NetType: 根据NetType网络转移概率矩阵生成的轨迹数据
    :param iteration: 轨迹文件的ID
    '''
    StrIteration = str(iteration)#轨迹文件的ID
    df_trajectories.to_csv(OutputTrajectoriesMoFolder + StrIteration + '_' + NetType + '.csv', index=False)

def generate_trajectories_list(iterations, NetType1, NetType2, SaveTrajectoriesVariableFolder, SaveRulesFolder, flag):
    for i in range(0, iterations):
        # 1.合成web点击流轨迹
        df_trajectories, trajectories = Simulate_Webclickstream_Trajectories(NetType1)

        # 2.将web点击流轨迹数据写入csv文件
        # WriteTrajectories(df_trajectories, NetType, i, OutputTrajectoriesFolder)# 输出合成的轨迹数据
        # 把内存中的trajectories存储到.pickle file中
        # SaveVariablestoPickleFile(trajectories, SaveTrajectoriesVariableFolder + NetType1 + '/' + str(i) + '_' + NetType1 + '_trajectories.pickle')

        # 3.得到高阶依赖规则集Rules
        Rules = ExtractRules(trajectories, MaxOrder, MinSupport)
        # 4.依据Rules，统计rules总数，不同阶数的rules在网络中出现的次数.并且把三阶依赖的概率分布输出为CSV文件20231114
        # (Rules_1st_order, Rules_2nd_order) = RuleStats(Rules)#最高阶数=2
        # (Rules_1st_order, Rules_2nd_order, Rules_3rd_order) = RuleStats(Rules)#最高阶数=3
        (Rules_1st_order, Rules_2nd_order, Rules_3rd_order, Rules_4th_order) = RuleStats(Rules)  # 最高阶数=4


        # 5. 多进程: 每次循环保存一个i_local_Distributions pickle文件
        # local_Distributions_differentElements = Rules_2nd_order #最高阶数为2
        # local_Distributions_differentElements = Rules_3rd_order #最高阶数为3
        local_Distributions_differentElements = Rules_4th_order  # 最高阶数为4

        SaveVariablestoPickleFile(local_Distributions_differentElements,
                                  SaveRulesFolder + str(flag) + '_local_Distributions_differentElements' + '_' + NetType2 + '.pickle')
    print(iterations, 'iterations finished!')

def aggregate_xorder_rules(Rules_x_order):
    '''
    把1000个dependency->Target概率分布汇总到一个数据结构中
    :param Rules_x_order: x order rules
    :return: distributions_differentElements
    '''
    # 1. 先按照tuple内的第一位排序，然后按tuple的第二个元素等对字典的元素排序
    sorted_Rules_x_order = dict(sorted(Rules_x_order.items(), key=lambda data: data[0]))
    # 2. 将每个转移概率矩阵的元素都保存至Distributions_differentElements结构中
    for dependency in sorted_Rules_x_order:
        for target in sorted_Rules_x_order[dependency]:
            specified_proba = sorted_Rules_x_order[dependency][target]
            Distributions_differentElements[dependency][target].append(specified_proba)  # 更新全局变量Distributions_differentElements
    return Distributions_differentElements



def process_function(iteration, NetType1, NetType2, SaveTrajectoriesVariableFolder, SaveRulesFolder):
    # 仅处理一个迭代
    generate_trajectories_list(1, NetType1, NetType2, SaveTrajectoriesVariableFolder, SaveRulesFolder, iteration)

def log_memory(msg=""):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / 1024**2  # MB
    print(f"[{msg}] 内存占用: {mem:.2f} MB")
    return mem


trajectories_num = 100 # 100条轨迹
iterations = 100
NetType_1 = '1st-order'
NetType_2 = '2nd-order'
NetType_3 = '3rd-order'
NetType_4 = '4th-order'
NetType_5 = '5th-order'

# MaxOrder = 2 #依赖关系的最高阶数
# MaxOrder = 3 #依赖关系的最高阶数
MaxOrder = 4 #依赖关系的最高阶数
SaveTrajectoriesVariableFolder = './variable/trajectories/20231114/'# p=0.1
Save1stRulesFolder = './variable/rules/20231114/1st-order/synthetic/'
Save2ndRulesFolder = './variable/rules/20231114/2nd-order/synthetic/'
Save3rdRulesFolder = './variable/rules/20231114/3rd-order/synthetic/'
Save4thRulesFolder = './variable/rules/20231114/4th-order/synthetic/'

# SaveTrajectoriesVariableFolder = './variable/trajectories/20231217/'# p=0.2
# Save1stRulesFolder = './variable/rules/20231217/1st-order/synthetic/'
# Save2ndRulesFolder = './variable/rules/20231217/2nd-order/synthetic/'
# Save3rdRulesFolder = './variable/rules/20231217/3rd-order/synthetic/'
# Save4thRulesFolder = './variable/rules/20231217/4th-order/synthetic/'

# SaveTrajectoriesVariableFolder = './variable/trajectories/20231229/'# p=0.3
# Save1stRulesFolder = './variable/rules/20231229/1st-order/synthetic/'
# Save2ndRulesFolder = './variable/rules/20231229/2nd-order/synthetic/'
# Save3rdRulesFolder = './variable/rules/20231229/3rd-order/synthetic/'
# Save4thRulesFolder = './variable/rules/20231229/4th-order/synthetic/'

#------------------------------------real probability distribution----------------------------
save_real_first_order_rule_variable_direcname = './variable/rules/20231114/2nd-order/'
# save_real_first_order_rule_variable_direcname = './variable/rules/20231217/2nd-order/'
# save_real_first_order_rule_variable_direcname = './variable/rules/20231229/2nd-order/'

save_real_second_order_rule_variable_direcname = './variable/rules/20231114/2nd-order/'
# save_real_second_order_rule_variable_direcname = './variable/rules/20231217/2nd-order/'
# save_real_second_order_rule_variable_direcname = './variable/rules/20231229/2nd-order/'

save_real_third_order_rule_variable_direcname = './variable/rules/20231114/3rd-order/'
# save_real_third_order_rule_variable_direcname = './variable/rules/20231229/3rd-order/'
# save_real_third_order_rule_variable_direcname = './variable/rules/20231217/3rd-order/'

save_real_fourth_order_rule_variable_direcname = './variable/rules/20231114/4th-order/'
# save_real_fourth_order_rule_variable_direcname = './variable/rules/20231217/4th-order/'
# save_real_fourth_order_rule_variable_direcname = './variable/rules/20231229/4th-order/'



Distributions_differentElements = defaultdict(lambda: defaultdict(list))#{(1, 2):{3:[0.6422, 0.662162, …., 0.655],...,},…,}
#----------------------------4. 使用算法检查包含一阶&二阶(page 25&51)&三阶(@page 84, 87)&四阶依赖(@page 38)的mo4轨迹数据中是否有高阶依赖----------------------
#-------------4.1 mo4轨迹数据中是否有二阶依赖(MaxOrder = 2)--------------------------
# 1. 根据真实数据的一阶转移概率，生成仿真轨迹。计算仿真轨迹数据的二阶转移概率。
# 创建一个进程池
if __name__ == '__main__':
    # 在主程序中
    log_memory("0.开始前:")
    with Pool(processes=10) as pool:  # 根据需要调整进程数
    # 使用 pool.map 来分配任务: 多进程生成仿真轨迹
        pool.starmap(process_function, [(i, NetType_1, NetType_2, SaveTrajectoriesVariableFolder, Save2ndRulesFolder) for i in range(iterations)])
    log_memory("1.生成仿真数据集的内存占用情况: ")
    Distributions_differentElements = read_all_defaultdictPickleFile(Save2ndRulesFolder)
    log_memory("2.合并仿真数据集的内存占用情况: ")
    # SaveVariablestoPickleFile(Distributions_differentElements,
    #                               Save2ndRulesFolder + 'mo4/' + 'Distributions_differentElements' + '_' + NetType_2 + '.pickle')
    # 2. 获得每个依赖项的概率分布的mean, std, 95%CI, 99%CI, Z-score
    # Distributions_differentElements = LoadVariablestoPickleFile(Save2ndRulesFolder+ 'mo4/' + 'Distributions_differentElements' + '_' + NetType_2 + '.pickle')
    statisticsindex_of_different_dependecies = CalculateStatisticsOfDifferentDistribution(Distributions_differentElements)
    log_memory("3.计算统计指标后的内存占用情况: ")

    # 3. 获得每个真实转移概率的Z-score, p-value
    Rules_2nd_order_mo4 = LoadVariablestoPickleFile(save_real_second_order_rule_variable_direcname + 'real/' + 'Rules_2nd_order_mo4.pickle')
    statisticsindex_of_different_dependecies, zscore_outliers, pval_outliers = CalculateZscoreofRealElements(statisticsindex_of_different_dependecies, Rules_2nd_order_mo4)
    log_memory("4.计算统计指标后zscore_outliers, pval_outliers的内存占用情况: ")
    SaveVariablestoPickleFile(zscore_outliers,
                              Save2ndRulesFolder+ 'mo4/' + 'zscore_outliers.pickle')
    SaveVariablestoPickleFile(pval_outliers,
                              Save2ndRulesFolder+ 'mo4/' + 'pval_outliers.pickle')
    SaveVariablestoPickleFile(statisticsindex_of_different_dependecies,
                              Save2ndRulesFolder+ 'mo4/' + 'statisticsindex_of_different_dependecies.pickle')
    print("!")
    # 4. 判断每个真实转移概率是否在置信区间内
    CI_outliers = ConfidenceIntervalTest(statisticsindex_of_different_dependecies, Rules_2nd_order_mo4)
    log_memory("5.计算统计指标后CI_outliers的内存占用情况: ")
    # 保存CI_outliers_mo1变量
    SaveVariablestoPickleFile(CI_outliers,
                              Save2ndRulesFolder+ 'mo4/' + 'CI_outliers.pickle')

    # 4. 输出99%置信区间外的依赖项输出到csv文件
    # OutputSigRulesFile = './data/rules/20231229/2nd_order_SignificantRules_mo4_99%CI.csv'
    # OutputSigRulesFile = './data/rules/20231217/2nd_order_SignificantRules_mo4_99%CI.csv'
    OutputSigRulesFile = './data/rules/20231114/2nd_order_SignificantRules_mo4_99%CI.csv'

    significant_2nd_order_rules_mo4 = DumpSignificantRules(statisticsindex_of_different_dependecies, zscore_outliers, Rules_2nd_order_mo4, Save2ndRulesFolder, OutputSigRulesFile)
    log_memory("5.输出显著性高阶依赖关系的内存占用情况: ")
    print("End!")
#-------------4.2 mo4轨迹数据中是否有三阶依赖(MaxOrder = 3)--------------------------
# 1. 根据真实数据的二阶转移概率，生成仿真轨迹。计算仿真轨迹数据的三阶转移概率。
# if __name__ == '__main__':
#     # 在主程序中
#     log_memory("0.开始前:")
#     with Pool(processes=10) as pool:  # 根据需要调整进程数
#     # 使用 pool.map 来分配任务: 多进程生成仿真轨迹
#         pool.starmap(process_function, [(i, NetType_2, NetType_3, SaveTrajectoriesVariableFolder, Save3rdRulesFolder) for i in range(iterations)])
#     log_memory("1.生成仿真数据集的内存占用情况: ")
#     Distributions_differentElements = read_all_defaultdictPickleFile(Save3rdRulesFolder)
#     log_memory("2.合并仿真数据集的内存占用情况: ")
#     # SaveVariablestoPickleFile(Distributions_differentElements,
#     #                           Save3rdRulesFolder+ 'mo4/' + 'Distributions_differentElements' + '_' + NetType_3 + '.pickle')
#     # 2. 获得每个依赖项的概率分布的mean, std, 95%CI, 99%CI, Z-score
#     # Distributions_differentElements = LoadVariablestoPickleFile(Save3rdRulesFolder+ 'mo4/' + 'Distributions_differentElements' + '_' + NetType_3 + '.pickle')
#     statisticsindex_of_different_dependecies = CalculateStatisticsOfDifferentDistribution(Distributions_differentElements)
#     log_memory("3.计算统计指标后的内存占用情况: ")
#     # 3. 获得每个真实转移概率的Z-score, p-value
#     Rules_3rd_order_mo4 = LoadVariablestoPickleFile(save_real_third_order_rule_variable_direcname + 'real/' + 'Rules_3rd_order_mo4.pickle')
#     # print(len(Rules_3rd_order_mo4)) #3阶依赖的个数*2
#
#     statisticsindex_of_different_dependecies, zscore_outliers, pval_outliers = CalculateZscoreofRealElements(
#         statisticsindex_of_different_dependecies, Rules_3rd_order_mo4)
#     log_memory("4.计算统计指标后zscore_outliers, pval_outliers的内存占用情况: ")
#     SaveVariablestoPickleFile(zscore_outliers,
#                               Save3rdRulesFolder+ 'mo4/' + 'zscore_outliers.pickle')
#     SaveVariablestoPickleFile(pval_outliers,
#                               Save3rdRulesFolder+ 'mo4/' + 'pval_outliers.pickle')
#     SaveVariablestoPickleFile(statisticsindex_of_different_dependecies,
#                               Save3rdRulesFolder+ 'mo4/' + 'statisticsindex_of_different_dependecies.pickle')
#     print("!")
#
#     # 4. 判断每个真实转移概率是否在置信区间内
#     CI_outliers = ConfidenceIntervalTest(statisticsindex_of_different_dependecies, Rules_3rd_order_mo4)
#     log_memory("5.计算统计指标后CI_outliers的内存占用情况: ")
#     # 保存CI_outliers_mo1变量
#     SaveVariablestoPickleFile(CI_outliers,
#                               Save3rdRulesFolder+ 'mo4/' + 'CI_outliers.pickle')
#     # 4. 输出99%置信区间外的依赖项输出到csv文件
#     OutputSigRulesFile = './data/rules/20231114/3rd_order_SignificantRules_mo4_95%CI.csv'
#     # OutputSigRulesFile = './data/rules/20231217/3rd_order_SignificantRules_mo4_95%CI.csv'
#     # OutputSigRulesFile = './data/rules/20231229/3rd_order_SignificantRules_mo4_95%CI.csv'
#
#     significant_3rd_order_rules_mo3 = DumpSignificantRules(statisticsindex_of_different_dependecies, zscore_outliers, Rules_3rd_order_mo4, Save3rdRulesFolder, OutputSigRulesFile)
#     log_memory("5.输出显著性高阶依赖关系的内存占用情况: ")
#     print("END!")
#-------------4.3 mo4轨迹数据中是否有四阶依赖(MaxOrder = 4)--------------------------
# 1. 根据真实数据的三阶转移概率，生成仿真轨迹。计算仿真轨迹数据的四阶转移概率。
# 创建一个进程池
# if __name__ == '__main__':
#     # 在主程序中
#     log_memory("0.开始前:")
#     # 记录开始时间
#     start_time = time.time()
#     with Pool(processes = 10) as pool:  # 根据需要调整进程数
#     # 使用 pool.map 来分配任务: 多进程生成仿真轨迹
#         pool.starmap(process_function, [(i, NetType_3, NetType_4, SaveTrajectoriesVariableFolder, Save4thRulesFolder) for i in range(iterations)])
#     log_memory("1.生成仿真数据集的内存占用情况: ")
#     Distributions_differentElements = read_all_defaultdictPickleFile(Save4thRulesFolder)
#     log_memory("2.合并仿真数据集的内存占用情况: ")
#     # SaveVariablestoPickleFile(Distributions_differentElements,
#     #                           Save4thRulesFolder+ 'mo4/' + 'Distributions_differentElements' + '_' + NetType_4 + '.pickle')
#
#     # 2. 获得每个依赖项的概率分布的mean, std, 95%CI, 99%CI, Z-score
#     # Distributions_differentElements = LoadVariablestoPickleFile(Save4thRulesFolder+ 'mo4/' + 'Distributions_differentElements' + '_' + NetType_4 + '.pickle')
#     statisticsindex_of_different_dependecies = CalculateStatisticsOfDifferentDistribution(Distributions_differentElements)
#     log_memory("3.计算统计指标后的内存占用情况: ")
#     # 3. 获得每个真实转移概率的Z-score, p-value
#     # save_real_fourth_order_rule_variable_direcname = './variable/rules/20231229/4th-order/'
#     # save_real_fourth_order_rule_variable_direcname = './variable/rules/20231217/4th-order/'
#     save_real_fourth_order_rule_variable_direcname = './variable/rules/20231114/4th-order/'
#     Rules_4th_order_mo4 = LoadVariablestoPickleFile(save_real_fourth_order_rule_variable_direcname + 'real/' + 'Rules_4th_order_mo4.pickle')
#     # print(len(Rules_4th_order_mo4)) #4阶依赖的个数*2
#
#     statisticsindex_of_different_dependecies, zscore_outliers, pval_outliers = CalculateZscoreofRealElements(
#             statisticsindex_of_different_dependecies, Rules_4th_order_mo4)
#     log_memory("4.计算统计指标后zscore_outliers, pval_outliers的内存占用情况: ")
#     SaveVariablestoPickleFile(zscore_outliers,
#                               Save4thRulesFolder+ 'mo4/' + 'zscore_outliers.pickle')
#     SaveVariablestoPickleFile(pval_outliers,
#                               Save4thRulesFolder+ 'mo4/' + 'pval_outliers.pickle')
#     SaveVariablestoPickleFile(statisticsindex_of_different_dependecies,
#                               Save4thRulesFolder+ 'mo4/' + 'statisticsindex_of_different_dependecies.pickle')
#
#     # 4. 判断每个真实转移概率是否在置信区间内
#     CI_outliers = ConfidenceIntervalTest(statisticsindex_of_different_dependecies, Rules_4th_order_mo4)
#     log_memory("5.计算统计指标后CI_outliers的内存占用情况: ")
#     # 保存CI_outliers_mo1变量
#     SaveVariablestoPickleFile(CI_outliers,
#                               Save4thRulesFolder+ 'mo4/' + 'CI_outliers.pickle')
#     # 记录结束时间
#     end_time = time.time()
#     # 计算并打印运行时间
#     elapsed_time = end_time - start_time
#     print(f"程序运行时间：{elapsed_time} 秒")
#
#     # 4. 输出99%置信区间外的依赖项输出到csv文件
#     OutputSigRulesFile = './data/rules/20231114/4th_order_SignificantRules_mo4_99%CI.csv'
#     # OutputSigRulesFile = './data/rules/20231217/4th_order_SignificantRules_mo4_99%CI.csv'
#     # OutputSigRulesFile = './data/rules/20231229/4th_order_SignificantRules_mo4_99%CI.csv'
#
#     significant_4th_order_rules_mo3 = DumpSignificantRules(statisticsindex_of_different_dependecies, zscore_outliers, Rules_4th_order_mo4, Save4thRulesFolder, OutputSigRulesFile)
#     print("END!")


