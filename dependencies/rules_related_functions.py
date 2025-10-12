from collections import defaultdict, Counter
import numpy as np
from dependencies.variables_to_pickleFile import *
import math

def DumpSignificantRules(statisticsindex_of_different_dependecies, CI_outliers, Rules, SaveRulesFolder, OutputRulesFile):
    '''
    输出显著的高阶依赖项以及对应的高阶转移、低阶概率值到csv文件
    :param statisticsindex_of_different_dependecies: 包含每个dependency的统计量
    :param Rules: x-order Rules的概率分布
    :param SaveRulesFolder: 显著的高阶依赖模式的存储地址
    :param OutputRulesFile:
    :return:
    '''
    significant_rules = defaultdict(dict)  # {A1:{},..., An:{}}
    significant_rules_stat = defaultdict(dict)
    # for source in zscore_outliers:
    #     for target in zscore_outliers[source]:
    #         flag = zscore_outliers[source][target]
    #         if (flag == 99)|(flag == -99):#把99%CI显著的高阶依赖模式保存
    #             significant_rules[source][target] = Rules[source][target]
    #             significant_rules_stat[source][target] = statisticsindex_of_different_dependecies[source][target]
    for source in CI_outliers:
        for target in CI_outliers[source]:
            flag = CI_outliers[source][target]
            if (flag == 99)|(flag == -99):
                significant_rules[source][target] = Rules[source][target]

    # 2. 把significant_rules的概率分布和低阶概率分别作比较，如果(Rules-Rules_lower_order)<0.1就认为不是显著的rules了，不输出了

    print('Dumping significant rules to file')
    with open(OutputRulesFile, 'w') as f:
        for source in significant_rules:
            for target in significant_rules[source]:
                f.write(' '.join([' '.join([str(x) for x in source]), '=>', str(target), str(Rules[source][target])]) + '\n')
    SaveVariablestoPickleFile(significant_rules,
                              SaveRulesFolder+ '/mo4/' + 'significant_rules_99%CI.pickle')
    SaveVariablestoPickleFile(significant_rules_stat,
                              SaveRulesFolder+ '/mo4/' + 'significant_rules_stat_99%CI.pickle')

    return significant_rules, significant_rules_stat




