# Synthesizes simulation synthetic web click stream data measure the significance of higher-order dependencies.
# There are 1000 users navigating through 100 web pages which are organized as a 10x10 grid
# Every user clicks through 100 pages by going either up/down/left/right.
# Basic case (1st-order dependency): a user will visit a next page either down/right with the same probability.
# Here we will generate 3 datasets: only 1st-order & no 2nd-order, 1st-order & 2nd-order, 1st-order & 2nd-order & 3rd-order.


import random
import pandas as pd
import numpy as np
from dependencies.variables_to_pickleFile import *




def NextStep(page):
    '''
    Basic case (only 1st-order dependency): a user will visit a next page
    only down/right with the same probability.
    :param page: the current page # of the walker
    :return: the next page # of the walker
    '''
    random.seed()
    down = (page + 10) % 100
    right = (page + 1) % 10 + 10 * int(page / 10)
    return random.choice([down, right]) # 从参数列表中随机选择一个元素

def SynthesizeAddFirstOrderDependency(NetType):
    '''
    生成包含一阶依赖的轨迹
    :param NetType: 网络阶数
    :return:
    '''
    random.seed()  # 设定好种子
    trajectories = []
    for user in range(users):  # 1000条轨迹
        trajectory = []  # 初始化每条轨迹
        for step in range(steps):  # 每条轨迹的长度=100
            page = -1
            random.seed()
            if len(trajectory) == 0:
                page = random.randint(0, 99)  # 从0-99中选取一个页面
            else:
                prev = trajectory[-1]  # 取列表中的最后一个元素
                page = NextStep(prev)

            trajectory.append(page)
        trajectories.append(trajectory)

    # SaveVariablestoPickleFile(trajectories,
    #                           SaveVariableDirecName + '20231229/' + 'clickstream-simulated-' + NetType + '.pickle')
    SaveVariablestoPickleFile(trajectories,
                              SaveVariableDirecName + '20240111/' + 'clickstream-simulated-' + NetType + '.pickle')
    # 将嵌套列表转换为NumPy数组
    trajectories_array = np.array(trajectories)
    # np.save(SaveVariableDirecName + '20231114/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)#嵌套列表中的每个子列表必须具有相同的长度，否则将引发ValueError异常
    # np.save(SaveVariableDirecName + '20231229/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)
    np.save(SaveVariableDirecName + '20240111/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)

    WriteTrajectories(trajectories, 'clickstream-simulated-', NetType)

def BiasedNextStep(page):
    '''
    2nd order rule: if user goes right from 24, 50 to @node 25, 51 correspondingly,
    then the next step will go right with probability 10%, go down 90%.
    :param page: the current page # of the walker
    :return: the next page # of the walker
    '''
    random.seed()
    down = (page + 10) % 100
    right = (page + 1) % 10 + 10 * int(page / 10)
    rnd = random.random() #返回 [0.0, 1.0) 范围内的一个随机浮点数
    # if rnd >= .9:#10%的概率向右
    # if rnd >= .8:
    # if rnd >= .7:
    if rnd >= .6:
        return right
    else:#90%的概率向下
        return down
def AltBiasedNextStep(page):
    '''
    Alt 2nd order rule: if user goes right from 15, 41 to node @25, 51 correspondingly,
    then the next step will go right with probability 90%, go down 10%.
    :param page: the current page # of the walker
    :return: the next page # of the walker
    '''
    random.seed()
    down = (page + 10) % 100
    right = (page + 1) % 10 + 10 * int(page / 10)
    rnd = random.random() #返回 [0.0, 1.0) 范围内的一个随机浮点数
    # if rnd < .9:#90%的概率向右
    # if rnd < .8:
    # if rnd < .7:
    if rnd < .6:
        return right
    else:
        return down

def SynthesizeAddSecondOrderDependency(NetType):
    '''
    生成同时包含一阶&二阶(page 25&51)依赖的轨迹
    :param NetType: 2nd-order
    :return:
    '''
    random.seed()  # 设定好种子
    trajectories = []
    for user in range(users):  # 1000条轨迹
        trajectory = []  # 初始化每条轨迹
        for step in range(steps):  # 每条轨迹的长度=100
            page = -1
            random.seed()
            if len(trajectory) == 0:
                page = random.randint(0, 99)  # 从0-99中选取一个页面
            else:
                if len(trajectory) == 1:
                    prev = trajectory[-1]  # 取列表中的最后一个元素
                    page = NextStep(prev)
                else:
                    prev = trajectory[-1]
                    p_prev = trajectory[-2]
                    if (p_prev, prev) in [(24, 25), (50, 51)]:
                        page = BiasedNextStep(prev)  # 增加二阶依赖
                    elif (p_prev, prev) in [(15, 25), (41, 51)]:
                        page = AltBiasedNextStep(prev)  # 增加二阶依赖
                    else:
                        page = NextStep(prev)
            trajectory.append(page)
        trajectories.append(trajectory)

    # SaveVariablestoPickleFile(trajectories,
    #                           SaveVariableDirecName + '20231229/' + 'clickstream-simulated-' + NetType + '.pickle')
    SaveVariablestoPickleFile(trajectories,
                              SaveVariableDirecName + '20240111/' + 'clickstream-simulated-' + NetType + '.pickle')
    # 将嵌套列表转换为NumPy数组
    trajectories_array = np.array(trajectories)
    # np.save(SaveVariableDirecName + '20231114/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)
    # np.save(SaveVariableDirecName + '20231229/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)
    np.save(SaveVariableDirecName + '20240111/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)
    WriteTrajectories(trajectories, 'clickstream-simulated-', NetType)

def SynthesizeAddThirdOrderDependency(NetType):
    '''
    3rd order rule: if user goes right from 64 through 74 to 84 (and 67 through 77 to 87),
    then the user's next step will go right with probability 90%, go down 10%.
    if user goes right from 73 through 74 to 84 (and 76 through 77 to 87),
    then the user's next step will go right with probability 10%, go down 90%.
    :param NetType: 3rd-order
    :return:
    '''
    random.seed()  # 设定好种子
    trajectories = []
    for user in range(users):  # 1000 users, 1000条轨迹
        trajectory = []  # 初始化每条轨迹
        for step in range(steps):  # 每条轨迹的长度=100
            random.seed()
            if len(trajectory) == 0:
                page = random.randint(0, 99)
            else:
                if len(trajectory) == 1:
                    prev = trajectory[-1]#获取用户当前停留的page
                    page = NextStep(prev)
                else:
                    if len(trajectory) == 2:
                        prev = trajectory[-1]
                        p_prev = trajectory[-2]
                        if (p_prev, prev) in [(24, 25), (50, 51)]:
                            page = BiasedNextStep(prev)# 增加二阶依赖
                        elif (p_prev, prev) in [(15, 25), (41, 51)]:
                            page = AltBiasedNextStep(prev)# 增加二阶依赖
                        else:
                            page = NextStep(prev)
                    else:#len(trajectory) >= 3
                        prev = trajectory[-1]
                        p_prev = trajectory[-2]
                        pp_prev = trajectory[-3]
                        if (p_prev, prev) in [(24, 25), (50, 51)]:# 增加二阶依赖
                            page = BiasedNextStep(prev)
                        elif (p_prev, prev) in [(15, 25), (41, 51)]:# 增加二阶依赖
                            page = AltBiasedNextStep(prev)
                        elif (pp_prev, p_prev, prev) in [(73, 74, 84), (76, 77, 87)]:# 增加三阶依赖
                            page = BiasedNextStep(prev)
                        elif (pp_prev, p_prev, prev) in [(64, 74, 84), (67, 77, 87)]:
                            page = AltBiasedNextStep(prev)
                        else:
                            page = NextStep(prev)
            trajectory.append(page)
        trajectories.append(trajectory)

    # SaveVariablestoPickleFile(trajectories,
    #                           SaveVariableDirecName + '20231229/' + 'clickstream-simulated-' + NetType + '.pickle')
    SaveVariablestoPickleFile(trajectories,
                              SaveVariableDirecName + '20240111/' + 'clickstream-simulated-' + NetType + '.pickle')
    # 将嵌套列表转换为NumPy数组
    trajectories_array = np.array(trajectories)
    # np.save(SaveVariableDirecName + '20231114/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)
    # np.save(SaveVariableDirecName + '20231229/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)
    np.save(SaveVariableDirecName + '20240111/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)

    WriteTrajectories(trajectories, 'clickstream-simulated-', NetType)

def SynthesizeAddFourthOrderDependency(NetType):
    '''
    4th-order rule: if user comes from 8 through 18 and 28 to 38,
    then the user's next step will go right with probability 90%, go down 10%.
    if user comes right from 17 through 18 and 28 to 38,
    then the user's next step will go right with probability 10%, go down 90%.
    :param NetType: 4th-order
    :return:
    '''
    random.seed()  # 设定好种子
    trajectories = []
    for user in range(users):  # 1000 users, 1000条轨迹
        trajectory = []  # 初始化每条轨迹
        for step in range(steps):  # 每条轨迹的长度=100
            random.seed()
            if len(trajectory) == 0:
                page = random.randint(0, 99)
            else:
                if len(trajectory) == 1:
                    prev = trajectory[-1]#获取用户当前停留的page
                    page = NextStep(prev)
                else:
                    if len(trajectory) == 2:
                        prev = trajectory[-1]
                        p_prev = trajectory[-2]
                        if (p_prev, prev) in [(24, 25), (50, 51)]:
                            page = BiasedNextStep(prev)# 增加二阶依赖
                        elif (p_prev, prev) in [(15, 25), (41, 51)]:
                            page = AltBiasedNextStep(prev)# 增加二阶依赖
                        else:
                            page = NextStep(prev)
                    else:#len(trajectory) >= 3
                        if len(trajectory) == 3:
                            prev = trajectory[-1]
                            p_prev = trajectory[-2]
                            pp_prev = trajectory[-3]
                            if (p_prev, prev) in [(24, 25), (50, 51)]:# 增加二阶依赖
                                page = BiasedNextStep(prev)
                            elif (p_prev, prev) in [(15, 25), (41, 51)]:# 增加二阶依赖
                                page = AltBiasedNextStep(prev)
                            elif (pp_prev, p_prev, prev) in [(73, 74, 84), (76, 77, 87)]:# 增加三阶依赖
                                page = BiasedNextStep(prev)
                            elif (pp_prev, p_prev, prev) in [(64, 74, 84), (67, 77, 87)]:
                                page = AltBiasedNextStep(prev)
                            else:
                                page = NextStep(prev)
                        else:#len(trajectory) >= 4
                            prev = trajectory[-1]
                            p_prev = trajectory[-2]
                            pp_prev = trajectory[-3]
                            ppp_prev = trajectory[-4]
                            if (p_prev, prev) in [(24, 25), (50, 51)]:  # 增加二阶依赖
                                page = BiasedNextStep(prev)
                            elif (p_prev, prev) in [(15, 25), (41, 51)]:  # 增加二阶依赖
                                page = AltBiasedNextStep(prev)
                            elif (pp_prev, p_prev, prev) in [(73, 74, 84), (76, 77, 87)]:  # 增加三阶依赖
                                page = BiasedNextStep(prev)
                            elif (pp_prev, p_prev, prev) in [(64, 74, 84), (67, 77, 87)]: # 增加三阶依赖
                                page = AltBiasedNextStep(prev)
                            elif (ppp_prev, pp_prev, p_prev, prev) in [(8, 18, 28, 38)]: # 增加四阶依赖
                                page = AltBiasedNextStep(prev)
                            elif (ppp_prev, pp_prev, p_prev, prev) in [(17, 18, 28, 38)]: # 增加四阶依赖
                                page = BiasedNextStep(prev)
                            else:
                                page = NextStep(prev)
            trajectory.append(page)
        trajectories.append(trajectory)
    # SaveVariablestoPickleFile(trajectories,
    #                           SaveVariableDirecName + '20231229/' + 'clickstream-simulated-' + NetType + '.pickle')
    SaveVariablestoPickleFile(trajectories,
                              SaveVariableDirecName + '20240111/' + 'clickstream-simulated-' + NetType + '.pickle')
    # 将嵌套列表转换为NumPy数组
    trajectories_array = np.array(trajectories)
    # np.save(SaveVariableDirecName + '20231114/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)
    # np.save(SaveVariableDirecName + '20231229/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)
    np.save(SaveVariableDirecName + '20240111/' + 'clickstream-simulated-' + NetType + '.npy', trajectories_array)

    WriteTrajectories(trajectories, 'clickstream-simulated-', NetType)
def WriteTrajectories(trajectories, subfilename, NetType):
    '''
    把合成的仿真轨迹数据输出为CSV文件
    :param trajectories: 轨迹数据(嵌套列表)
    :param subfilename:
    :param NetType:
    :return:
    '''
    trajectories_list = []
    for trajectory in trajectories:
        trajectories_list.append(' '.join(map(str, trajectory)))
    d1 = {'trajectory_id': range(1, users + 1), 'trajectory': trajectories_list}
    df_trajectories = pd.DataFrame(d1)
    # df_trajectories.to_csv(OutputCSVFolder + '20231114/' + subfilename + NetType + '.csv', index=False)
    # df_trajectories.to_csv(OutputCSVFolder + '20231229/' + subfilename + NetType + '.csv', index=False)
    df_trajectories.to_csv(OutputCSVFolder + '20240111/' + subfilename + NetType + '.csv', index=False)

#------------------------------------------------------------------------------------------------------------
# 100*1000 clicks
OutputCSVFolder = './data/trajectories/' # ./代表目前所在目录
users = 1000 # 1000 users
steps = 100
SaveVariableDirecName = './variable/trajectories/'



if __name__ == '__main__':
    # 生成满足条件的1000条web点击流轨迹
    NetType = input("Input the type of simulation dataset: 1st-order, 2nd-order, 3rd-order or 4th-order:");

    if NetType == '1st-order':
        SynthesizeAddFirstOrderDependency(NetType)
    elif NetType == '2nd-order':# 增加二阶依赖
        SynthesizeAddSecondOrderDependency(NetType)
    elif NetType == '3rd-order':# 增加三阶依赖
        SynthesizeAddThirdOrderDependency(NetType)
    else:
        SynthesizeAddFourthOrderDependency(NetType)
    # loaded_array = np.load(SaveVariableDirecName + '20231114/' +'clickstream-simulated-1st-order.npy')
    print("!")

