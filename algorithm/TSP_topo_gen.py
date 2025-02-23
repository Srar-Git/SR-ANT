import heapq
import sys


def dijkstra(matrix, start_node, n):
    # 计算从 start_node 到其他所有节点的最短路径
    distances = [float('inf')] * n
    distances[start_node] = 0
    pq = [(0, start_node)]  # (距离, 节点)

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        # 如果当前节点的距离已经更大了，不需要继续
        if current_dist > distances[current_node]:
            continue

        # 遍历所有相邻的节点
        for neighbor in range(n):
            if matrix[current_node][neighbor] != float('inf'):
                distance = matrix[current_node][neighbor]
                new_dist = current_dist + distance

                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))

    return distances


def genFatTree(podsNum):
    sys.setrecursionlimit(1000000)

    L1 = (podsNum // 2) * (podsNum // 2)
    L2 = (podsNum // 2) * podsNum
    L3 = L2
    swSum = L1 + L2 + L3
    topoList = [[float('inf')] * (swSum + 1) for _ in range(swSum + 1)]  # 新增虚拟节点
    hostList = [0 for _ in range(swSum + 1)]  # 新增虚拟节点
    linkNum = 0

    core = [0 for _ in range(L1)]
    agg = [0 for _ in range(L2)]
    edg = [0 for _ in range(L3)]

    # add core switches
    for i in range(L1):
        core[i] = i
    # add aggregation switches
    for i in range(L2):
        agg[i] = L1 + i
    # add edge switches
    for i in range(L3):
        edg[i] = L1 + L2 + i

    # 初始化顶点之间的连接（每对直接连接为 1）
    for i in range(podsNum // 2):
        for j in range(podsNum):
            # add links between aggregation and core switches
            for k in range(podsNum // 2 * i, podsNum // 2 * (i + 1)):
                topoList[agg[podsNum // 2 * j + i]][core[k]] = 1
                topoList[core[k]][agg[podsNum // 2 * j + i]] = 1
                linkNum += 2
            # add links between aggregation and edge switches
            for m in range(podsNum // 2):
                topoList[agg[podsNum // 2 * j + i]][edg[podsNum // 2 * j + m]] = 1
                topoList[edg[podsNum // 2 * j + m]][agg[podsNum // 2 * j + i]] = 1
                linkNum += 2

    # 计算最短路径
    for i in range(swSum):
        # 从每个节点出发，计算到其他所有节点的最短路径
        shortest_distances = dijkstra(topoList, i, swSum)
        # 更新邻接矩阵中的值为最短路径
        for j in range(swSum):
            if shortest_distances[j] == float('inf'):
                topoList[i][j] = 0  # 无连接的节点之间设为 0
            else:
                topoList[i][j] = shortest_distances[j]

    # 添加虚拟节点（21号节点）
    virtual_node = swSum  # 虚拟节点的编号为 21（即索引为 20）



    # 虚拟节点到其他节点的距离设为 9
    for i in range(swSum):
        if i != virtual_node:  # 不与自己连接
            topoList[virtual_node][i] = 9
            topoList[i][virtual_node] = 9

        # 虚拟节点到 ToR 节点的距离设为 0
    for i in range(swSum - L3, swSum):  # ToR 节点的编号是从 L1+L2 到 swSum-1
        topoList[virtual_node][i] = 0
        topoList[i][virtual_node] = 0

    topoList[len(topoList) - 1][len(topoList)-1] = 0
    # 更新 hostList
    for i in range(L1 + L2, swSum):
        hostList[i] = 1

    return topoList, hostList, swSum + 1  # 返回的交换机总数为 21


# ----------------------------
# 以下是一个示例，演示如何使用上述函数：
if __name__ == "__main__":
    # 示例：创建 FatTree 拓扑，设定 podsNum
    podsNum = 14  # 设置 pod 数量
    matrix, host, swSum = genFatTree(podsNum)

    # 输出最短路径邻接矩阵（包含虚拟节点）
    for row in matrix:
        for col in row:
            print(col, end=" ")
        print("")
    print(len(matrix))