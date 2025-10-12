# 根据真实的低阶转移概率生成仿真轨迹
import numpy as np
import pandas as pd
from dependencies.variables_to_pickleFile import *
from collections import defaultdict, Counter
import random




#States of Markov chain
STATES = range(0, 100)
save_first_order_rule_variable_direcname = './variable/rules/20231114/1st-order/real/'# p=0.1
# save_first_order_rule_variable_direcname = './variable/rules/20231217/1st-order/real/'# p=0.2
# save_first_order_rule_variable_direcname = './variable/rules/20231229/1st-order/real/'# p=0.3

first_order_trans_pro = np.load(save_first_order_rule_variable_direcname + 'Rules_1st_order_mo4.npy')

save_second_order_rule_variable_direcname = './variable/rules/20231114/2nd-order/real/'# p=0.1
# save_second_order_rule_variable_direcname = './variable/rules/20231217/2nd-order/real/'# p=0.2
# save_second_order_rule_variable_direcname = './variable/rules/20231229/2nd-order/real/'# p=0.3

second_order_trans_pro = LoadVariablestoPickleFile(save_second_order_rule_variable_direcname + 'Rules_2nd_order_mo4.pickle')

save_third_order_rule_variable_direcname = './variable/rules/20231114/3rd-order/real/'# p=0.1
# save_third_order_rule_variable_direcname = './variable/rules/20231217/3rd-order/real/'# p=0.2
# save_third_order_rule_variable_direcname = './variable/rules/20231229/3rd-order/real/'# p=0.3

third_order_trans_pro = LoadVariablestoPickleFile(save_third_order_rule_variable_direcname + 'Rules_3rd_order_mo4'
                                                                                             '.pickle')

save_fourth_order_rule_variable_direcname = './variable/rules/20231114/4th-order/real/'# p=0.1
# save_fourth_order_rule_variable_direcname = './variable/rules/20231217/4th-order/real/'# p=0.2
# save_fourth_order_rule_variable_direcname = './variable/rules/20231229/4th-order/real/'# p=0.3

fourth_order_trans_pro = LoadVariablestoPickleFile(save_fourth_order_rule_variable_direcname + 'Rules_4th_order_mo4.pickle')
class Webclickstream:
    '''
    Webclickstream class that simulates a Markov chain for one clickstream based
    on Markov states defined above and a different-order transition probability matrix
    '''

    def __init__(self, clickstream_id, NetType):
        self.clickstream_id = clickstream_id #点击流轨迹的ID
        self.nettype = NetType
        self.state = np.random.choice(STATES, 1, replace=True)[0]  # 随机选择一个page作为轨迹的起点
        self.steps = 100  # 确定每条轨迹的长度
        self.nb_state = 1
        self.history = [self.state]
        if NetType == '1st-order':
            self.gen = self.first_markov()  # 返回一个生成器对象，赋值给类实例的属性
        elif NetType == '2nd-order':
            self.gen = self.second_markov()  # 返回一个生成器对象，赋值给类实例的属性
        elif NetType == '3rd-order':
            self.gen = self.third_markov()  # 返回一个生成器对象，赋值给类实例的属性
        elif NetType == '4th-order':
            self.gen = self.fourth_markov()  # 返回一个生成器对象，赋值给类实例的属性



    def __repr__(self):
        return f"The clickstream number {self.clickstream_id} is at {self.state}"

    def get_next_state(self):
        return next(self.gen)# 内置函数，返回迭代器的下一个项目

    def first_markov(self):#调用该函数，产生生成器对象
        step = 1
        while step != self.steps:
            p = first_order_trans_pro[self.state]
            if sum(p) != 1:
                p /= p.sum()  # normalize
            next_state = np.random.choice(STATES, 1, p=p)[0]#p定义了STATES中每个元素采样的概率
            step = step+1

            self.state = next_state
            self.history.append(self.state)
            self.nb_state += 1
            yield self.state #1. return 2. 暂停 3. 下次调用，会从暂停的地方执行，执行暂停的地方的下一句
    def second_markov(self):
        for _ in range(self.steps-1):
            sequence = self.history
            current_state = self.state
            if len(sequence) == 1:#当序列长度<=1时，根据一阶转移概率矩阵生成序列
                p = first_order_trans_pro[current_state]
                next_state = np.random.choice(STATES, 1, p=p)[0]
            else:#当序列长度>1时，根据二阶转移概率矩阵生成序列
                previous_state = sequence[-2]
                state_pair = (previous_state, current_state)
                if state_pair in second_order_trans_pro:
                    next_states = list(second_order_trans_pro[state_pair].keys())
                    probabilities = list(second_order_trans_pro[state_pair].values())
                    next_state = np.random.choice(next_states, 1, p=probabilities)[0]
                else:
                    # Fall back to first order if no second order data is available
                    p = first_order_trans_pro[current_state]
                    next_state = np.random.choice(STATES, 1, p=p)[0]  # p定义了STATES中每个元素采样的概率

            # 更新变量
            self.state = next_state
            self.history.append(self.state)
            self.nb_state += 1
            yield self.state  # 1. return 2. 暂停 3. 下次调用，会从暂停的地方执行，执行暂停的地方的下一句

    def third_markov(self):
        for _ in range(self.steps-1):
            sequence = self.history
            current_state = self.state
            if len(sequence) == 1:#当序列长度<=1时，根据一阶转移概率矩阵生成序列
                p = first_order_trans_pro[current_state]
                next_state = np.random.choice(STATES, 1, p=p)[0]
            elif len(sequence) == 2:#当序列长度==2时，根据二阶转移概率矩阵生成序列
                previous_state = sequence[-2]
                state_pair = (previous_state, current_state)
                if state_pair in second_order_trans_pro:
                    next_states = list(second_order_trans_pro[state_pair].keys())
                    probabilities = list(second_order_trans_pro[state_pair].values())
                    next_state = np.random.choice(next_states, 1, p=probabilities)[0]
                else:
                    # Fall back to first order if no second order data is available
                    p = first_order_trans_pro[current_state]
                    next_state = np.random.choice(STATES, 1, p=p)[0]  # p定义了STATES中每个元素采样的概率

            else:#当序列长度>2时，根据三阶转移概率矩阵生成序列
                p_p_state = sequence[-3]
                previous_state = sequence[-2]
                state_pair = (p_p_state, previous_state, current_state)
                if state_pair in third_order_trans_pro:
                    next_states = list(third_order_trans_pro[state_pair].keys())
                    probabilities = list(third_order_trans_pro[state_pair].values())
                    next_state = np.random.choice(next_states, 1, p=probabilities)[0]
                else:
                    # Fall back to second order if no third order data is available
                    state_pair = (previous_state, current_state)
                    if state_pair in second_order_trans_pro:
                        next_states = list(second_order_trans_pro[state_pair].keys())
                        probabilities = list(second_order_trans_pro[state_pair].values())
                        next_state = np.random.choice(next_states, 1, p=probabilities)[0]
                    else:# Fall back to first order if no second order data is available
                        p = first_order_trans_pro[current_state]
                        next_state = np.random.choice(STATES, 1, p=p)[0]  # p定义了STATES中每个元素采样的概率

            # 更新变量
            self.state = next_state
            self.history.append(self.state)
            self.nb_state += 1
            yield self.state  # 1. return 2. 暂停 3. 下次调用，会从暂停的地方执行，执行暂停的地方的下一句

    def fourth_markov(self):
        for _ in range(self.steps-1):
            sequence = self.history
            current_state = self.state
            if len(sequence) == 1:#当序列长度<=1时，根据一阶转移概率矩阵生成序列
                p = first_order_trans_pro[current_state]
                next_state = np.random.choice(STATES, 1, p=p)[0]
            elif len(sequence) == 2:#当序列长度==2时，根据二阶转移概率矩阵生成序列
                previous_state = sequence[-2]
                state_pair = (previous_state, current_state)
                if state_pair in second_order_trans_pro:
                    next_states = list(second_order_trans_pro[state_pair].keys())
                    probabilities = list(second_order_trans_pro[state_pair].values())
                    next_state = np.random.choice(next_states, 1, p=probabilities)[0]
                else:
                    # Fall back to first order if no second order data is available
                    p = first_order_trans_pro[current_state]
                    next_state = np.random.choice(STATES, 1, p=p)[0]  # p定义了STATES中每个元素采样的概率
            elif len(sequence) == 3:#当序列长度==3时，根据三阶转移概率矩阵生成序列
                p_p_state = sequence[-3]
                previous_state = sequence[-2]
                state_pair = (p_p_state, previous_state, current_state)
                if state_pair in third_order_trans_pro:
                    next_states = list(third_order_trans_pro[state_pair].keys())
                    probabilities = list(third_order_trans_pro[state_pair].values())
                    next_state = np.random.choice(next_states, 1, p=probabilities)[0]
                else:
                    # Fall back to second order if no third order data is available
                    state_pair = (previous_state, current_state)
                    if state_pair in second_order_trans_pro:
                        next_states = list(second_order_trans_pro[state_pair].keys())
                        probabilities = list(second_order_trans_pro[state_pair].values())
                        next_state = np.random.choice(next_states, 1, p=probabilities)[0]
                    else:# Fall back to first order if no second order data is available
                        p = first_order_trans_pro[current_state]
                        next_state = np.random.choice(STATES, 1, p=p)[0]  # p定义了STATES中每个元素采样的概率
            else:#当序列长度>=4时，根据四阶转移概率矩阵生成序列
                p_p_p_state = sequence[-4]
                p_p_state = sequence[-3]
                previous_state = sequence[-2]
                state_pair = (p_p_p_state, p_p_state, previous_state, current_state)
                if state_pair in fourth_order_trans_pro:
                    next_states = list(fourth_order_trans_pro[state_pair].keys())
                    probabilities = list(fourth_order_trans_pro[state_pair].values())
                    next_state = np.random.choice(next_states, 1, p=probabilities)[0]
                else:
                    # Fall back to third order if no fourth order data is available
                    state_pair = (p_p_state, previous_state, current_state)
                    if state_pair in third_order_trans_pro:
                        next_states = list(third_order_trans_pro[state_pair].keys())
                        probabilities = list(third_order_trans_pro[state_pair].values())
                        next_state = np.random.choice(next_states, 1, p=probabilities)[0]
                    else:
                        # Fall back to second order if no third order data is available
                        state_pair = (previous_state, current_state)
                        if state_pair in second_order_trans_pro:
                            next_states = list(second_order_trans_pro[state_pair].keys())
                            probabilities = list(second_order_trans_pro[state_pair].values())
                            next_state = np.random.choice(next_states, 1, p=probabilities)[0]
                        else:
                            # Fall back to first order if no second order data is available
                            p = first_order_trans_pro[current_state]
                            next_state = np.random.choice(STATES, 1, p=p)[0]  # p定义了STATES中每个元素采样的概率

            # 更新变量
            self.state = next_state
            self.history.append(self.state)
            self.nb_state += 1
            yield self.state  # 1. return 2. 暂停 3. 下次调用，会从暂停的地方执行，执行暂停的地方的下一句

