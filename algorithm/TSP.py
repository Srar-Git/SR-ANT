def tsp(adj):
    """
    求解标准 TSP 问题（从 0 开始）

    参数:
        adj: 邻接矩阵（二维列表），adj[i][j] 表示从 i 到 j 的距离

    返回:
        path: 最优路径的节点列表，例如 [0, 2, 1, 3, 0]
    """
    n = len(adj)
    # dp[(mask, j)] 表示从起点 0 出发，经过 mask 中的所有节点，最后停在 j 的最小路径长度
    dp = {}
    # 用于记录路径恢复：parent[(mask, j)] = 前驱节点
    parent = {}

    # 初始化：只有起点 0 被访问，且当前在 0 的状态
    dp[(1 << 0, 0)] = 0

    # 枚举所有的状态（mask 表示已访问的节点集合）
    for mask in range(1 << n):
        for j in range(n):
            # 如果 j 不在 mask 中，跳过
            if not (mask & (1 << j)):
                continue
            # 如果 (mask, j) 状态不存在，也跳过
            if (mask, j) not in dp:
                continue
            # 尝试从 j 走到未访问过的节点 k
            for k in range(n):
                if mask & (1 << k):  # k 已经在 mask 中，跳过
                    continue
                next_mask = mask | (1 << k)
                new_cost = dp[(mask, j)] + adj[j][k]
                # 更新 (next_mask, k) 状态
                if (next_mask, k) not in dp or new_cost < dp[(next_mask, k)]:
                    dp[(next_mask, k)] = new_cost
                    parent[(next_mask, k)] = j

    # 所有节点均被访问的状态
    full_mask = (1 << n) - 1
    best_cost = float('inf')
    last = -1
    # 最后从各个结尾节点回到起点 0，选择最小的方案
    for i in range(n):
        if i == 0:
            continue  # 起点 0 不作为中间的结束点
        if (full_mask, i) in dp:
            cost_with_return = dp[(full_mask, i)] + adj[i][0]
            if cost_with_return < best_cost:
                best_cost = cost_with_return
                last = i

    if last == -1:
        return None  # 不可能的情况

    # 根据 parent 恢复路径（逆序恢复）
    path = []
    mask = full_mask
    cur = last
    while True:
        path.append(cur)
        # 当 mask 中只剩下一个节点（起点 0）时结束
        if mask == (1 << cur):
            break
        prev = parent[(mask, cur)]
        mask = mask & ~(1 << cur)
        cur = prev
    path.reverse()  # 此时 path 从起点开始，结束于最后一个中间节点
    path.append(0)  # 回到起点，构成环路

    return path


# 示例测试
if __name__ == '__main__':
    # 邻接矩阵示例（4个节点）
    adj_matrix = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]
    ]

    best_path = tsp(adj_matrix)
    print("最优路径：", best_path)
