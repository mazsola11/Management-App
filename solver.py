import math

def solve_mpm(tasks, dependencies, result_df):

    # task read
    taskID = dict()
    taskVertex = [0 for _ in tasks]
    taskDuration = [0 for _ in tasks]
    edge_in = [[] for _ in range(2 * len(tasks))]
    edge_out = [[] for _ in range(2 * len(tasks))]
    for i, task in enumerate(tasks):
        taskID[task[0]] = i
        taskVertex[i] = (2 * i, 2 * i + 1)
        taskDuration[i] = task[1]
        edge_in[2 * i + 1].append((2 * i, taskDuration[i]))
        edge_out[2 * i].append((2 * i + 1, taskDuration[i]))

    del tasks, i, task

    # dependency read
    for dependency in dependencies:
        fromID = taskID[dependency[0]]
        toID = taskID[dependency[1]]
        # dependency[2] is dependency type
        duration = dependency[3]
        if dependency[2] == 'Start-start':
            fromVertex = taskVertex[fromID][0]
            toVertex = taskVertex[toID][0]
        elif dependency[2] == 'Start-finish':
            fromVertex = taskVertex[fromID][0]
            toVertex = taskVertex[toID][1]
        elif dependency[2] == 'Finish-start':
            fromVertex = taskVertex[fromID][1]
            toVertex = taskVertex[toID][0]
        elif dependency[2] == 'Finish-finish':
            fromVertex = taskVertex[fromID][1]
            toVertex = taskVertex[toID][1]
        else:
            raise ValueError('invalid dependency type')
        edge_in[toVertex].append((fromVertex, duration))
        edge_out[fromVertex].append((toVertex, duration))
    del dependencies, fromID, toID, dependency, fromVertex, toVertex

    queue = list()
    # forward run (width-first)for i, task in enumerate(edge_in):
    for i, task in enumerate(edge_in):
        if len(task) == 0:
            queue.append(i)
    earliest = [0 for _ in edge_in]
    visitCount = [0 for _ in edge_in]
    while len(queue) != 0:
        # queue.pop()
        vertex = queue[0]
        del queue[0]

        for edge in edge_out[vertex]:
            nextVertex = edge[0]
            duration = edge[1]
            visitCount[nextVertex] += 1
            earliest[nextVertex] = max(earliest[nextVertex],
                                       earliest[vertex] + duration)
            if visitCount[nextVertex] == len(edge_in[nextVertex]):
                queue.append(nextVertex)
    # backward run (width-first)
    for i, task in enumerate(edge_out):
        if len(task) == 0:
            queue.append(i)
    latest = [max(earliest) for _ in edge_in]
    visitCount = [0 for _ in edge_in]
    while len(queue) != 0:
        # queue.pop()
        vertex = queue[0]
        del queue[0]

        for edge in edge_in[vertex]:
            nextVertex = edge[0]
            duration = edge[1]
            visitCount[nextVertex] += 1
            latest[nextVertex] = min(latest[nextVertex],
                                     latest[vertex] - duration)
            if visitCount[nextVertex] == len(edge_out[nextVertex]):
                queue.append(nextVertex)

    EST = []
    EFT = []
    LST = []
    LFT = []
    TF = []
    Crit = []

    for task, ID in taskID.items():
        EST.append(earliest[taskVertex[ID][1]] - taskDuration[ID])
        EFT.append(earliest[taskVertex[ID][1]])
        LST.append(latest[taskVertex[ID][0]])
        LFT.append(latest[taskVertex[ID][0]] + taskDuration[ID])

        TF.append(latest[taskVertex[ID][0]] - (earliest[taskVertex[ID][1]] - taskDuration[ID]))

        if (earliest[taskVertex[ID][1]] - taskDuration[ID] - latest[taskVertex[ID][0]]) == 0:
            Crit.append(True)
        else:
            Crit.append(False)

    result_df['EST'] = EST
    result_df['EFT'] = EFT
    result_df['LST'] = LST
    result_df['LFT'] = LFT
    result_df['TF'] = TF
    result_df['Crit'] = Crit

    return result_df

