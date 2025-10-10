import statistics
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import csv
from statistics import stdev
import scipy.stats as stats
from fractions import Fraction as fr
from collections import defaultdict, Counter
from scipy.stats import norm
from dependencies.variables_to_pickleFile import *

statisticsindex_of_different_dependecies = defaultdict(lambda: defaultdict(dict))#{('PhysRevA', 'PhysRevA'):{'PhysRevA':{'mean': X, 'standard_deviation': X}, 'PhysRevLett':[0.126, …, X],...,'PhysRevSTAB':[0.004, …, X], 'Physics': [0, …, X]},…,}




def CalculateStatisticsOfDifferentDistribution(Distributions_differentElements):
    '''
    计算每个元素的概率分布的统计指标，mean, standard_deviation, confidence intervals
    :param Distributions_differentElements:
    :return: statisticsindex_of_different_dependecies
    '''

    for dependency in Distributions_differentElements:
        for target in Distributions_differentElements[dependency].keys():
            # 1. 计算mean, standard_deviation
            mean_edepen = statistics.mean(Distributions_differentElements[dependency][target])
            mean_edepen = round(mean_edepen, 2)
            if len(Distributions_differentElements[dependency][target]) == 1:#当元素个数为1时
                stdev_edepen = 0
                statisticsindex_of_different_dependecies[dependency][target]['mean'] = mean_edepen
                statisticsindex_of_different_dependecies[dependency][target]['standard_deviation'] = stdev_edepen

            else:
                stdev_edepen = statistics.stdev(Distributions_differentElements[dependency][target])#计算样本标准差
                stdev_edepen = round(stdev_edepen, 2)
                statisticsindex_of_different_dependecies[dependency][target]['mean'] = mean_edepen
                statisticsindex_of_different_dependecies[dependency][target]['standard_deviation'] = stdev_edepen


            stde = statisticsindex_of_different_dependecies[dependency][target]['standard_deviation']



            # 2. 计算95%置信区间的上下界
            # specified_proba = Rules_x_order[dependency][target]  # 真实的转移概率
            low_CI_95 = mean_edepen - 1.96 * stde #95%CI下界
            up_CI_95 = mean_edepen + 1.96 * stde #95%CI上界
            # low_CI_95 = round(low_CI_95, 3)
            # up_CI_95 = round(up_CI_95, 3)
            confidence_interval_95 = (low_CI_95, up_CI_95)
            statisticsindex_of_different_dependecies[dependency][target]['95%CI'] = confidence_interval_95
            # 3. 计算99%CI的上下界
            low_CI_99 = mean_edepen - 2.58 * stde  # 99%CI下界
            up_CI_99 = mean_edepen + 2.58 * stde  # 99%CI上界
            # low_CI_99 = round(low_CI_99, 3)
            # up_CI_99 = round(up_CI_99, 3)
            confidence_interval_99 = (low_CI_99, up_CI_99)
            statisticsindex_of_different_dependecies[dependency][target]['99%CI'] = confidence_interval_99

            # 4.计算90%CI的上下界
            low_CI_90 = mean_edepen - 1.65 * stde  # 95%CI下界
            up_CI_90 = mean_edepen + 1.65 * stde  # 95%CI上界
            # low_CI_90 = round(low_CI_90, 3)
            # up_CI_90 = round(up_CI_90, 3)
            confidence_interval_90 = (low_CI_90, up_CI_90)
            statisticsindex_of_different_dependecies[dependency][target]['90%CI'] = confidence_interval_90
    return statisticsindex_of_different_dependecies


def CalculateZscoreofRealElements(statisticsindex_of_different_dependecies, Rules_x_order):
    '''
    计算每个真实依赖项的Z-score和p-value, 并判断abs(Z-score)>threshold
    :param statisticsindex_of_different_dependecies:存储每个转移概率元素的统计特性，mean, stdev, Z-score
    :param threshold: Z-score的阈值
    :return:输出outliers和更新后的statisticsindex_of_different_dependecies
    '''
    zscore_outliers = defaultdict(lambda: defaultdict(int))  # 指示某转移概率的Z-score是否大于threshold{('PhysRevA', 'PhysRevA'):{'PhysRevA':0, B2:0, ...,Bn:0}, A2:{B1:0, B2:0, ...,Bn:0}, ...,An:{B1:0, B2:0, ...,Bn:0}}
    pval_outliers = defaultdict(lambda: defaultdict(int))  # 指示某转移概率的p-value是否大于0.05, 0.01

    # 1. 根据statisticsindex_of_different_dependecies存储的各个依赖的mean和stdev，计算真实转移概率的z-score
    for dependency in statisticsindex_of_different_dependecies:#dependency元组中的元素是int
        for target in statisticsindex_of_different_dependecies[dependency].keys():#target是int
            mean_edepen = statisticsindex_of_different_dependecies[dependency][target]['mean']
            stdev_edepen = statisticsindex_of_different_dependecies[dependency][target]['standard_deviation']
            if (mean_edepen != 'na') & (stdev_edepen != 'na') & (stdev_edepen != 0):
                if dependency in Rules_x_order and target in Rules_x_order[dependency]:
                    specified_proba = Rules_x_order[dependency][target] #真实的转移概率
                    # 计算z-score
                    # len_samples = len(Distributions_differentElements[dependency][target])
                    # z_score = (len_samples*mean_edepen - len_samples*specified_proba) / ((len_samples**0.5)*stdev_edepen)

                    z_score = (specified_proba - mean_edepen) / stdev_edepen  # 计算每个element的z-score
                    z_score = round(z_score, 2)
                    statisticsindex_of_different_dependecies[dependency][target]['z_score'] = z_score
                    if z_score > 2.58:#99%CI
                        zscore_outliers[dependency][target] = 99
                    elif z_score > 1.96:
                        zscore_outliers[dependency][target] = 95
                    elif z_score > 1.65:
                        zscore_outliers[dependency][target] = 90
                    elif z_score < -2.58:
                        zscore_outliers[dependency][target] = -99
                    elif z_score < -1.96:
                        zscore_outliers[dependency][target] = -95
                    elif z_score < -1.65:
                        zscore_outliers[dependency][target] = -90
                    else:
                        zscore_outliers[dependency][target] = 0

                    # 2.计算p-value
                    pval = stats.norm.sf(abs(z_score)) * 2# 双尾检验
                    # tt = (specified_proba - mean_edependecies) / np.sqrt(stdev_edependecies / float(sample_size))  # t-statistic for mean
                    # pval = stats.t.sf(np.abs(tt), sample_size - 1) * 2  # two-sided pvalue = Prob(abs(t)>tt)
                    # print('t-statistic = %6.3f pvalue = %6.4f' % (tt, pval))
                    statisticsindex_of_different_dependecies[dependency][target]['p-val'] = pval

                    if pval < 0.1:
                        pval_outliers[dependency][target] = 90
                        if pval < 0.05:
                            pval_outliers[dependency][target] = 95
                            if pval < 0.01:
                                pval_outliers[dependency][target] = 99
                    else:
                        pval_outliers[dependency][target] = 0
    return statisticsindex_of_different_dependecies, zscore_outliers, pval_outliers

def ConfidenceIntervalTest(statisticsindex_of_different_dependecies, Rules_x_order):
    '''
    对元素进行90%, 95%, 99%confidence interval test
    :param statisticsindex_of_different_dependecies: 统计学指标
    :param df_SecondOrderTransitionProbability: real second-order transition probability
    :return: CI_outliers
    '''
    CI_outliers = defaultdict(lambda: defaultdict(int))  # 指示某转移概率是否在置信区间(CI)中{('PhysRevA', 'PhysRevA'):{'PhysRevA':0, B2:0, ...,Bn:0}, A2:{B1:0, B2:0, ...,Bn:0}, ...,An:{B1:0, B2:0, ...,Bn:0}}
    for dependency in statisticsindex_of_different_dependecies:  # (int 1, int 1)
        for target in statisticsindex_of_different_dependecies[dependency].keys():  # int 1
            # mean_edepen = statisticsindex_of_different_dependecies[dependency][target]['mean']
            confidence_interval_90 = statisticsindex_of_different_dependecies[dependency][target]['90%CI']
            LowerLimitingValue_90 = confidence_interval_90[0]
            UpperLimitingValue_90 = confidence_interval_90[1]

            confidence_interval_95 = statisticsindex_of_different_dependecies[dependency][target]['95%CI']
            LowerLimitingValue_95 = confidence_interval_95[0]
            UpperLimitingValue_95 = confidence_interval_95[1]

            confidence_interval_99 = statisticsindex_of_different_dependecies[dependency][target]['99%CI']
            LowerLimitingValue_99 = confidence_interval_99[0]
            UpperLimitingValue_99 = confidence_interval_99[1]
            if dependency in Rules_x_order and target in Rules_x_order[dependency]:
                specified_proba = Rules_x_order[dependency][target]  # 真实的转移概率

                if specified_proba > UpperLimitingValue_90:
                    CI_outliers[dependency][target] = 90
                    if specified_proba == 0:
                        CI_outliers[dependency][target] = 2
                    if specified_proba > UpperLimitingValue_95:
                        CI_outliers[dependency][target] = 95
                        if specified_proba == 0:
                            CI_outliers[dependency][target] = 22
                        if specified_proba > UpperLimitingValue_99:
                            CI_outliers[dependency][target] = 99
                            if specified_proba == 0:
                                CI_outliers[dependency][target] = 222
                elif specified_proba < LowerLimitingValue_90:
                    CI_outliers[dependency][target] = -90
                    if specified_proba == 0:
                        CI_outliers[dependency][target] = 2
                    if specified_proba < LowerLimitingValue_95:
                        CI_outliers[dependency][target] = -95
                        if specified_proba == 0:
                            CI_outliers[dependency][target] = 22
                        if specified_proba < LowerLimitingValue_99:
                            CI_outliers[dependency][target] = -99
                            if specified_proba == 0:
                                CI_outliers[dependency][target] = 222
                else:
                    CI_outliers[dependency][target] = 0
    return CI_outliers




