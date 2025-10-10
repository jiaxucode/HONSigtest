from collections import defaultdict, Counter
import numpy as np
#from concurrent import futures

import math
import json
import codecs

#Count: 全局变量，字典—记录order阶pattern出现的次数
#StartingPoints: 全局变量，字典—存储source node在数据中的位置索引

Count = defaultdict(lambda: defaultdict(int))#{A1:{B1:0, B2:0, ...,Bn:0}, A2:{B1:0, B2:0, ...,Bn:0}, ...,An:{B1:0, B2:0, ...,Bn:0}}
Rules = defaultdict(dict)#{A1:{},..., An:{}}
Distribution = defaultdict(dict)#{('33',):{'34':0.495, '43': 0.505},('34',):{'35':0.496, '44': 0.504},('35',):{'45':0.520, '36': 0.480},..., ('92',):{'93':0.499, '2': 0.501}}
SourceToExtSource = defaultdict(set)#SourceToExtSource[Curr]#返回低阶节点Source对应的满足条件(MinSupport)的高阶节点SourceToExtSource[Curr]#返回低阶节点Source对应的满足条件(MinSupport)的高阶节点 {Source:set(ExtSource1, ExtSource2, ...,ExtSourcen),..., An:set()}
StartingPoints = defaultdict(set)
Trajectory = []
MinSupport = 5 # 每个pattern出现的最少次数
def Initialize():
    '''
    初始化参数
    :return:
    '''
    global Count # global在函数内部声明后，在函数内部就可以对函数外的对象进行操作了（改变值）
    global Rules
    global Distribution
    global SourceToExtSource
    global StartingPoints #字典：存储source node在数据中的位置索引

    Count = defaultdict(lambda: defaultdict(int))#记录order阶pattern出现的次数
    Rules = defaultdict(dict)
    Distribution = defaultdict(dict)#记录order阶下每个source node的转移概率分布
    SourceToExtSource = defaultdict(set)
    StartingPoints = defaultdict(set)#字典：存储source node在数据中的位置索引

def ExtractRules(T, MaxOrder, MS):
    '''
    The rule extraction algorithm.
    :param T: the sequential data
    :param MaxOrder: 网络中节点的最高阶数 99
    :param MS: 每个pattern出现的最少次数
    :return: higher-order dependency rules set-Rules
    '''
    Initialize()#初始化参数
    global Trajectory
    global MinSupport
    Trajectory = T
    MinSupport = MS
    BuildOrder(1, Trajectory, MinSupport)# order==1
    GenerateAllRules(MaxOrder, Trajectory, MinSupport)
    return Distribution #返回概率

    # return Rules #返回计数

def BuildOrder(order, Trajectory, MinSupport):
    '''
    计算轨迹数据Trajectory中阶数为order（1 ~ MaxOrder==99）的patterns/subsequences出现的次数，结果保存在变量Count中。
    :param order: 阶数
    :param Trajectory: the sequential data
    :param MinSupport: 每个pattern出现的最少次数
    :return:
    '''
    BuildObservations(Trajectory, order)#只计算了一阶pattern出现的次数
    BuildDistributions(MinSupport, order)#计算阶数为order的情况下，每个source node的转移概率分布.

def BuildObservations(Trajectory, order):
    '''
    计算轨迹数据Trajectory中阶数为order（1 ~ MaxOrder==99）
    的patterns/subsequences出现的次数,结果保存在变量Count中
    :param Trajectory: the sequential data
    :param order:
    :return: Count: 全局变量，字典—记录order阶pattern出现的次数；
     StartingPoints: 全局变量，字典—存储source node在数据中的位置索引
    '''
    # print('building observations for order ' + str(order))
    LoopCounter = 0
    for Tindex in range(len(Trajectory)):#Tindex: 第Tindex条数据
        LoopCounter += 1
        if LoopCounter % 1000 == 0:
            print(LoopCounter)
        # remove metadata stored in the first element
        # this step can be extended to incorporate richer information
        trajectory = Trajectory[Tindex]

        #l=len(trajectory) - order#100-1=99
        for index in range(len(trajectory) - order):#index:0-98
            Source = tuple(trajectory[index:index+order])#Source是包含一个元素的元组: ('33',)
            Target = trajectory[index+order]
            #Count: {('33',):{'34':1, B2:0, ...,Bn:0}, ('34',):{'35': 1, B2:0, ...,Bn:0},('35',):{'45': 1, B2:0, ...,Bn:0}}记录order阶pattern出现的次数
            Count[Source][Target] += 1
            #print(Count)
            StartingPoints[Source].add((Tindex, index))#给集合添加元素，如果添加的元素在集合中已存在，则不执行任何操作。
            #print(StartingPoints[Source])#{(0, 0)}
            #print(StartingPoints)#{('33',): {(0, 0)}, ('34',): {(0, 1)}, ('35',): {(0, 2)}, ('45',): {(0, 3)}}记录每个patter的Source节点在Trajectory中的位置
    # print('BuildObservations for 1st order end!')

def BuildDistributions(MinSupport, order):
    '''
    根据Count的值，计算每个source node的转移概率分布
    :param MinSupport: 每个pattern出现的最少次数,eg.1.只有出现次数大于MinSupport的pattern才有可能成为高阶节点
    :param order: 阶数
    :return: Distribution: 全局变量，字典结构—记录order阶下每个source node的转移概率分布
    '''
    # print('building distributions with MinSupport ' + str(MinSupport))
    for Source in Count:#Source:('33',)
        if len(Source) == order:#如果Source的长度等于pattern的阶数
            for Target in Count[Source].keys():
                if Count[Source][Target] < MinSupport:
                    Count[Source][Target] = 0#如果某个pattern的长度小于MinSupport，那么就清除这个pattern（该Source也就不可能成为高阶节点了）
            for Target in Count[Source]:
                if Count[Source][Target] > 0:
                    #print(Count[Source].values())
                    Distribution[Source][Target] = 1.0 * Count[Source][Target] / sum(Count[Source].values())#Distribution: {('33',):{'34':0.495, '43': 0.505},('34',):{'35:0.496, '44': 0.504},..., An:{}}
    # print('BuildDistributions for 1st order end!')
def GenerateAllRules(MaxOrder, Trajectory, MinSupport):
    '''
    根据传统网络的Distribution，生成Rules
    :param MaxOrder: 3
    :param Trajectory: sequential data
    :param MinSupport: 1
    '''
    # print('generating rules')
    progress = len(Distribution)#local variable 字典Distribution的长度=100
    # print('初始source node的个数: ', progress)#输出初始source node的个数
    # print('初始Distribution的长度为', progress)
    # print('初始的source node个数为', progress)
    LoopCounter = 0
    for Source in tuple(Distribution.keys()):#Source: tuple:('33',);('34',)
        AddToRules(Source)
        ExtendRule(Source, Source, 1, MaxOrder, Trajectory, MinSupport)
        LoopCounter += 1
        #if LoopCounter % 10 == 0:
        #print('generating rules ' + str(LoopCounter) + ' ' + str(progress))
def ExtendRule(Valid, Curr, order, MaxOrder, Trajectory, MinSupport):
    if order >= MaxOrder:#节点阶数高于阈值，终止递归
        AddToRules(Valid)#Valid==Curr
    else:
        Distr = Distribution[Valid]#Distr: 节点Valid的概率分布{'34':0.495, '43': 0.505}
        NewOrder = order + 1

        Extended = ExtendSourceFast(Curr)#找到(阶数=NewOrder)&(以Curr结尾的)Extended节点, eg. {('32','33'),('23','33')}
        if len(Extended) == 0:#Extended不满足条件时，Valid被保存在Rules，递归结束
            AddToRules(Valid)
        else:
            for ExtSource in Extended:
                ExtendRule(ExtSource, ExtSource, NewOrder, MaxOrder, Trajectory, MinSupport)



def AddToRules(Source):#Source: ('33',)
    '''
    创建Rules
    :param Source:
    :return:Rules
    '''
    for order in range(1, len(Source)+1):#左闭右开 order=1~len(Source)
        s = Source[0:order]#s是元组，eg. ('33',) pattern的第一个节点
        #print(s, Source)
        if (not s in Distribution) or len(Distribution[s]) == 0:#当s不在Distribution中，或者s没有目标节点
            ExtendSourceFast(s[1:])#如果s不在Distribution中，那么先扩展低阶节点s[1:]，这样s就在Distribution中存在了！eg.s:('67','77'), s[1:]:('77')-->('76','77'),('67','77')存在于Distribution中了
        # Rules[s] = Distribution[s]# pattern s 赋给Distribution字典

        # 输出频数
        for t in Count[s]:
            if Count[s][t] > 0:
                Rules[s][t] = Count[s][t]



###########################################
# Auxiliary functions
###########################################



def ExtendSourceFast(Curr):#Curr:('33',)
    '''
    更新字典SourceToExtSource，找到(阶数=NewOrder)&(以Curr结尾的)Extended节点。eg.Curr: Singapore, Extend:Singapore|Shanghai
    :param Curr: eg.('33',)
    :return:SourceToExtSource[Curr]#返回低阶节点Source对应的满足条件(MinSupport)的高阶节点
    '''
    if Curr in SourceToExtSource:#SourceToExtSource: {A1:set(),..., An:set()}
        return SourceToExtSource[Curr]
    else:
        ExtendObservation(Curr)#根据低阶节点Curr，产生高阶节点。更新SourceToExtSource, C, StartingPoints, Distribution, Count
        if Curr in SourceToExtSource:
            return SourceToExtSource[Curr]#返回低阶节点Source对应的满足条件(MinSupport)的高阶节点
        else:
            return []


def ExtendObservation(Source):#Source:('33',)
    '''
    根据低阶节点Source，产生高阶节点。更新SourceToExtSource, C, StartingPoints, Distribution, Count
    :param Source: the current source node
    :return:
    '''

    if len(Source) > 1:#Source: ('33',)/ ('32','33')/('31','32','33')
        if (not Source[1:] in Count) or (len(Count[Source]) == 0):
            ExtendObservation(Source[1:])
    order = len(Source)#当前Source节点的阶数
    C = defaultdict(lambda: defaultdict(int))#高阶节点的pattern频数

    for Tindex, index in StartingPoints[Source]:#Tindex: Source节点所在的记录的索引 index:Source节点在记录中的位置
        if index - 1 >= 0 and index + order < len(Trajectory[Tindex]):#Source不在轨迹的起始位置（可以取其前一个节点，形成高阶节点），且其位置可以扩展
            #print('Trajectory[Tindex][1][index - 1:index + order]', Trajectory[Tindex][1][index - 1:index + order])
            ExtSource = tuple(Trajectory[Tindex][index - 1:index + order])#左闭右开 ExtSource: 一阶节点扩展得到的高阶节点 ('23','33')
            Target = Trajectory[Tindex][index + order]#Target:从ExtSource转移到的目标节点 '34'
            C[ExtSource][Target] += 1#高阶节点的pattern频数分布 {('23','33'):{'34':1, B2:0, ...,Bn:0}, A2:{B1:0, B2:0, ...,Bn:0}, ...,An:{B1:0, B2:0, ...,Bn:0}}
            StartingPoints[ExtSource].add((Tindex, index - 1))#更新StartingPoints: 把ExtSource高阶节点的位置加入StartingPoints(纵向位置记录的是PreSource,即Soure前一个实体的index)

    if len(C) == 0:
        return
    for s in C:#eg. C: {('23','33'):{'34':2724, '43':2767}, ('32','33'):{'34':2470, '43':2508}}
        for t in C[s]:#t: the target node in a pattern
            if C[s][t] < MinSupport:#如果某个pattern的长度小于MinSupport，那么就清除这个pattern（该Source也就不可能成为高阶节点了）
                C[s][t] = 0
            Count[s][t] += C[s][t]#把满足条件的pattern加入Count
        CsSupport = sum(C[s].values())#概率的分母
        for t in C[s]:
            if C[s][t] > 0:
                Distribution[s][t] = 1.0 * C[s][t] / CsSupport #更新Distribution（加入高阶节点的概率分布）
                SourceToExtSource[s[1:]].add(s)#将元素s添加到集合中，如果元素已存在，则不进行任何操作


