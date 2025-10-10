InputFileDeliminator = ','#fig-example dataset
# InputFileDeliminator = ' '#enron dataset
# InputFileDeliminator = ','#APS dataset
MinimumLengthForTraining = 1
LastStepsHoldOutForTesting = 0
def ReadSequentialData(InputFileName):
    '''
    从csv文件中读取轨迹数据
    :param InputFileName: 文件名
    :return: RawTrajectories
    '''
    RawTrajectories = []
    with open(InputFileName, encoding="utf-8-sig") as f:
        LoopCounter = 0
        for line in f:
            #strip() 去除字符串首尾空格；split()通过指定分隔符对字符串进行切片,返回分割后的字符串列表
            movements = line.strip().split(InputFileDeliminator)
            ## In the context of global shipping, a ship sails among many ports
            ## and generate trajectories.
            ## Every line of record in the input file is in the format of:
            ## [Ship1] [Port1] [Port2] [Port3]...

            LoopCounter += 1
            if LoopCounter % 10000 == 0:# %模运算：返回余数
                print(LoopCounter) #print(LoopCounter)

            ## Other preprocessing or metadata processing can be added here

            ## Test for movement length
            MinMovementLength = MinimumLengthForTraining + LastStepsHoldOutForTesting #min-length-of-trajectory
            if len(movements) < MinMovementLength:#如果真实的轨迹长度<MinMovementLength,那么就抛弃该轨迹
                continue

            RawTrajectories.append(movements)#把满足条件的轨迹记录加入RawTrajectories列表


    return RawTrajectories
