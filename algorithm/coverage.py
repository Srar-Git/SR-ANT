import sys
import numpy as np


def generate_fattree(k):
    """
    仅适用于 k 为偶数。总交换机数 = 5 * (k^2) / 4。
    索引区间:
      - Pod 内: 0 ~ k^2 - 1 (分成 k 个 Pod, 每个 k 台交换机)
          对于第 p 个 Pod:
            Aggregation 范围: [p*k, p*k + (k/2) - 1]
            Edge 范围:        [p*k + (k/2), p*k + k - 1]
      - Core 层: k^2 ~ (5k^2/4) - 1, 共 (k/2)^2 个
    聚合 <-> 边缘: 完全互连 (同一 Pod 内)
    聚合 a <-> 核心: 连 (k/2) 个 Core, 索引对应区间 (a*(k/2)) ~ (a*(k/2) + (k/2) - 1)
    """
    if k % 2 != 0:
        raise ValueError("当前示例的FatTree需要k为偶数！")

    total_switches = (5 * k * k) // 4  # 5k^2/4, 整数
    matrix = np.zeros((total_switches, total_switches), dtype=int)

    core_start = k * k  # 核心层起始索引

    # 对每个 Pod
    for p in range(k):
        # 该Pod的起始索引
        pod_base = p * k
        # Aggregation, Edge 的索引区间
        agg_start = pod_base
        agg_end   = pod_base + (k // 2) - 1
        edge_start= pod_base + (k // 2)
        edge_end  = pod_base + k - 1

        # 1) Aggregation <-> Edge (同Pod内完全互连)
        for agg in range(agg_start, agg_end + 1):
            for edg in range(edge_start, edge_end + 1):
                matrix[agg][edg] = 1
                matrix[edg][agg] = 1

        # 2) Aggregation <-> Core
        #    对该Pod的每个 Aggregation，在 Pod 内的相对序号 a = [0..(k/2)-1]
        for agg in range(agg_start, agg_end + 1):
            a = agg - agg_start  # a 的取值范围 0..(k/2 -1)
            # 连 core 层中 [core_start + a*(k/2) .. core_start + a*(k/2)+(k/2)-1]
            for c in range(a*(k//2), a*(k//2) + (k//2)):
                core_index = core_start + c
                matrix[agg][core_index] = 1
                matrix[core_index][agg] = 1

    return matrix


def calculate_port_coverage(fattree, tour):
    total_ports = 0
    covered_ports = set()

    # 遍历路径中的每一对相邻交换机
    for i in range(len(fattree) - 1):
        for j in range(len(fattree) - 1):
            if fattree[i][j] == 1:
                total_ports += 2
    print("total_ports: ",total_ports)
    # 计算端口覆盖率
    # total_ports_in_fattree = np.sum(fattree) // 2  # 每条边有两个端口
    coverage = len(tour*2) / total_ports * 100  # 端口覆盖率
    return coverage


if __name__ == '__main__':
    k = 10
    fattree = generate_fattree(k)

    tour = [3, 10, 17, 9, 18, 1, 11, 20, 2, 5, 14, 6, 13, 4, 12, 19, 15, 7, 16, 8]

    # 计算端口覆盖率
    coverage = calculate_port_coverage(fattree, tour)
    print(f"Port coverage: {coverage:.2f}%")
