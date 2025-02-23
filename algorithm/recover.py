import sys
import time
import random

import numpy as np


def nearest_insertion_tsp(matrix, nodes):
    """
    使用最近邻插入算法构造 TSP 路径。

    参数:
        matrix: 2D numpy 数组，图的邻接矩阵，其中 matrix[i, j] 表示节点 i 到节点 j 的距离。
        nodes: 可用节点列表（编号列表）。

    返回:
        tour: 根据最近邻插入算法构造的 TSP 路径（循环路径）。
    """
    if not nodes:
        return []

    # 选择第一个节点作为起点
    start = nodes[0]
    tour = [start]
    remaining = nodes.copy()
    remaining.remove(start)

    # 如果还有其他节点，则选择距离起点最近的节点构成初始子环
    if remaining:
        nearest = min(remaining, key=lambda x: matrix[start, x])
        tour.append(nearest)
        remaining.remove(nearest)
    else:
        return tour

    # 循环：当还有未加入路径的节点时
    while remaining:
        best_node = None  # 待插入的节点
        best_cost_increase = float('inf')  # 插入该节点产生的最小额外成本
        best_insert_position = None  # 插入位置（在 tour 中两个相邻节点之间插入）

        # 对于每个未加入的节点
        for node in remaining:
            # 尝试将该节点插入到当前路径的每一条边上，计算额外的距离增量
            for i in range(len(tour)):
                j = (i + 1) % len(tour)  # 因为 TSP 路径是循环的，最后一个节点的下一个为第一个节点
                cost_increase = matrix[tour[i], node] + matrix[node, tour[j]] - matrix[tour[i], tour[j]]
                if cost_increase < best_cost_increase:
                    best_cost_increase = cost_increase
                    best_node = node
                    best_insert_position = j  # 插入到位置 j 前面（即在 tour[i] 与 tour[j]之间插入）
        # 将选定的节点按最佳位置插入当前路径
        tour.insert(best_insert_position, best_node)
        remaining.remove(best_node)

    return tour


def update_tsp_path(matrix, original_path, missing_nodes):
    """
    移除缺失节点后，利用最近邻插入算法重新构造 TSP 路径。

    参数:
        matrix: 图的邻接矩阵（应包含所有节点的编号信息，但仅会使用剩余节点）。
        original_path: 原始完整的 TSP 路径（包含所有节点）。
        missing_nodes: 缺失节点的列表（例如：[2, 4]）。

    返回:
        new_path: 更新后的 TSP 路径，不包含缺失节点。
    """
    # 从原始路径中移除所有缺失节点，得到剩余节点列表
    updated_nodes = [node for node in original_path if node not in missing_nodes]

    # 使用最近邻插入算法计算新的 TSP 路径
    new_path = nearest_insertion_tsp(matrix, updated_nodes)
    return new_path
def genFatTree(podsNum):
    sys.setrecursionlimit(1000000)
    L1 = (podsNum//2)*(podsNum//2)
    L2 = (podsNum//2)*podsNum
    L3 = L2
    swSum = L1 + L2 + L3
    topoList = [[0 for i in range(swSum)] for i in range(swSum)]
    hostList = [0 for i in range(swSum)]
    linkNum = 0

    core = [0 for i in range(L1)]
    agg = [0 for i in range(L2)]
    edg = [0 for i in range(L3)]

    # add core switches
    for i in range(L1):
        core[i] = i
    # add aggregation switches
    for i in range(L2):
        agg[i] = L1 + i
    # add edge switches
    for i in range(L3):
        edg[i] = L1 + L2 + i

    for i in range(podsNum//2):
        for j in range(podsNum):
            # add links between aggregation and core switches
            for k in range(podsNum//2*i, podsNum//2*(i+1)):
                topoList[agg[podsNum//2*j+i]][core[k]] = 1
                topoList[core[k]][agg[podsNum//2*j+i]] = 1
                linkNum += 2
            # add links between aggregation and edge switches
            for m in range(podsNum//2):
                topoList[agg[podsNum//2*j+i]][edg[podsNum//2*j+m]] = 1
                topoList[edg[podsNum//2*j+m]][agg[podsNum//2*j+i]] = 1
                linkNum += 2

    # hostList
    for i in range((L1+L2), swSum):
        hostList[i] = 1

    return topoList, hostList,swSum


# ----------------------------
# 以下是一个示例，演示如何使用上述函数：
if __name__ == "__main__":
    # 构造示例邻接矩阵（例如：5个节点，节点编号 0~4）
    # matrix = np.array([
    #     [0, 10, 15, 20, 25],
    #     [10, 0, 35, 25, 30],
    #     [15, 35, 0, 30, 5],
    #     [20, 25, 30, 0, 15],
    #     [25, 30, 5, 15, 0]
    # ])
    matrix, host, sNum = genFatTree(4)
    print(sNum)
    matrix = np.array(matrix)

    # 原始 TSP 路径（完整的节点序列）
    original_path = [
3,
10,
17,
9,
18,
1,
11,
20,
2,
5,
14,
6,
13,
4,
12,
19,
15,
7,
16,
8]
    p = []
    for i in original_path:
        p.append(i - 1)
    # 假设缺失节点为 2 和 4
    miss_count =10

    missing_nodes = []
    for i in range(miss_count):
        value = random.randint(0, sNum - 1)
        missing_nodes.append(value)
    # print(missing_nodes)

    # 计算更新后的 TSP 路径
    time1 = time.time()
    new_path = update_tsp_path(matrix, p, missing_nodes)
    time2 = time.time()
    print("新的 TSP 路径:", new_path)
    print("耗时:", (time2 - time1) * 1000)
    print("========")
    matrix, host, sNum = genFatTree(6)
    print(sNum)
    matrix = np.array(matrix)

    # 原始 TSP 路径（完整的节点序列）
    original_path = [41, 40, 24, 7, 21, 37, 38, 19, 2, 22, 1, 10, 28, 11, 30, 12, 29, 8, 18, 9, 34, 16, 35, 17, 5, 14, 32, 15, 33, 13, 31, 4, 20, 39, 3, 25, 45, 27, 44, 26, 43, 36, 6, 42, 23]
    p = []
    for i in original_path:
        p.append(i-1)
    # 假设缺失节点为 2 和 4
    miss_count =10

    missing_nodes = []
    for i in range(miss_count):
        value = random.randint(0, sNum-1)
        missing_nodes.append(value)
    # print(missing_nodes)

    # 计算更新后的 TSP 路径
    time1 = time.time()
    new_path = update_tsp_path(matrix, p, missing_nodes)
    time2 = time.time()
    print("新的 TSP 路径:", new_path)
    print("耗时:", (time2 - time1)*1000)
    print("========")
    matrix, host, sNum = genFatTree(8)
    print(sNum)
    matrix = np.array(matrix)

    # 原始 TSP 路径（完整的节点序列）
    original_path = [51, 15, 49, 18, 52, 50, 11, 23, 56, 53, 21, 3, 58, 28, 59, 27, 60, 25, 57, 26, 7, 80, 46, 77, 47, 79, 45, 78, 48, 14, 40, 69, 38, 71, 37, 70, 39, 10, 19, 12, 43, 9, 31, 62, 32, 64, 29, 63, 8, 72, 16, 20, 13, 61, 30, 5, 34, 66, 36, 67, 33, 68, 35, 65, 2, 17, 4, 41, 1, 76, 74, 75, 44, 73, 42, 6, 22, 55, 24, 54]
    p = []
    for i in original_path:
        p.append(i-1)
    # 假设缺失节点为 2 和 4
    miss_count =10

    missing_nodes = []
    for i in range(miss_count):
        value = random.randint(0, sNum-1)
        missing_nodes.append(value)
    # print(missing_nodes)

    # 计算更新后的 TSP 路径
    time1 = time.time()
    new_path = update_tsp_path(matrix, p, missing_nodes)
    time2 = time.time()
    print("新的 TSP 路径:", new_path)
    print("耗时:", (time2 - time1)*1000)
    print("========")
    matrix, host, sNum = genFatTree(14)
    print(sNum)
    matrix = np.array(matrix)

    # 原始 TSP 路径（完整的节点序列）
    original_path = [204, 109, 210, 112, 205, 108, 206, 45, 63, 44, 91, 184, 86, 188, 87, 186, 88, 25, 160, 26, 130, 22, 159, 29, 181, 180, 78, 182, 84, 48, 126, 223, 125, 224, 219, 149, 51, 151, 50, 1, 57, 6, 127, 230, 2, 134, 7, 141, 245, 145, 244, 143, 240, 144, 243, 146, 241, 147, 242, 239, 142, 11, 65, 14, 107, 9, 135, 238, 137, 234, 136, 236, 139, 232, 138, 237, 140, 233, 235, 4, 183, 89, 185, 90, 189, 85, 187, 38, 201, 3, 177, 80, 19, 216, 116, 214, 119, 211, 113, 217, 115, 213, 15, 59, 20, 73, 16, 52, 150, 54, 153, 56, 148, 152, 55, 154, 53, 27, 81, 28, 231, 227, 32, 117, 31, 75, 30, 82, 34, 161, 62, 36, 76, 173, 24, 74, 172, 169, 175, 72, 170, 77, 174, 71, 171, 12, 58, 158, 61, 156, 157, 60, 23, 95, 191, 93, 196, 92, 190, 98, 194, 94, 193, 96, 192, 97, 195, 39, 118, 37, 229, 35, 131, 33, 178, 79, 176, 83, 179, 49, 47, 46, 133, 43, 105, 197, 103, 203, 100, 10, 114, 215, 212, 8, 128, 13, 121, 220, 120, 222, 123, 218, 124, 221, 122, 21, 155, 42, 132, 226, 18, 168, 162, 64, 164, 70, 166, 68, 165, 69, 167, 67, 163, 66, 17, 202, 102, 198, 101, 199, 104, 200, 99, 5, 225, 129, 228, 41, 40, 207, 111, 208, 106, 209, 110]
    p = []
    for i in original_path:
        p.append(i-1)
    # 假设缺失节点为 2 和 4
    miss_count =10

    missing_nodes = []
    for i in range(miss_count):
        value = random.randint(0, sNum-1)
        missing_nodes.append(value)
    # print(missing_nodes)

    # 计算更新后的 TSP 路径
    time1 = time.time()
    new_path = update_tsp_path(matrix, p, missing_nodes)
    time2 = time.time()
    print("新的 TSP 路径:", new_path)
    print("耗时:", (time2 - time1)*1000)
    print("========")