# -*- coding: UTF-8 -*-
import matplotlib.pyplot as plt
import copy
import random
import networkx as nx
import numpy as np
import time
import sys

class Graph(object):
    def __init__(self, *args, **kwargs):
        self.node_neighbors = {}
        self.visited = {}
        self.A = []  # 为现存节点数组
        self.degree = []  # 为度数组

    def add_nodes(self, nodelist):
        for node in nodelist:
            self.add_node(node)

    def add_node(self, node):
        if node not in self.nodes():
            self.node_neighbors[node] = []

    def add_edge(self, edge):
        u, v = edge
        if (v not in self.node_neighbors[u]) and (u not in self.node_neighbors[v]):
            self.node_neighbors[u].append(v)
            if (u != v):
                self.node_neighbors[v].append(u)

    def nodes(self):
        return self.node_neighbors.keys()

    def not_null_node(self):
        self.A.clear()
        for node in self.nodes():
            if len(self.node_neighbors[node]) > 0:
                self.A.append(node)

    def degrees(self):
        self.degree.clear()
        Node = self.nodes()
        for node in Node:
            self.degree.append(len(self.node_neighbors[node]))

    def set_diff(self, nodes):
        others = []
        for node in self.A:
            if node not in nodes:
                others.append(node)
        return others

    def F1(self):  # 求所有连通子图
        nodes = []
        visited = []
        subgraph = {}
        i = 1
        temp = self.set_diff(nodes)
        while len(temp) > 0:
            order = self.depth_first_search(temp[0])
            subgraph[i] = order
            i += 1
            visited.extend(order)
            temp = self.set_diff(visited)
        return subgraph

    def judge(self, subgraph):
        for i in subgraph:
            t = 0
            temp = subgraph[i]
            for node in temp:
                if self.degree[node - 1] % 2 != 0:
                    t = 1  # t=1说明有奇顶点
                    break
            if t == 0:
                return i
        return 0

    def F2(self, gt):
        num = 0
        for node in gt:
            if self.degree[node - 1] % 2 != 0:
                num += 1
        return num

    def F3(self, path):
        for i in range(len(path) - 1):
            self.node_neighbors[path[i]].remove(path[i + 1])
            self.node_neighbors[path[i + 1]].remove(path[i])
        self.not_null_node()

    def depth_first_search(self, root=None):  # 在连通的前提下进行深度优先搜索
        order = []
        def dfs(node):
            self.visited[node] = True
            order.append(node)
            for n in self.node_neighbors[node]:
                if n not in self.visited:
                    dfs(n)
        if root:
            dfs(root)
        for node in self.nodes():
            if node not in self.visited:
                for v_node in self.visited:
                    if node in self.node_neighbors[v_node]:
                        dfs(node)
        self.visited.clear()
        return order

    def my_path(self, subgraph):
        odd_node = []
        path_len = {}
        for node in subgraph:
            if self.degree[node - 1] % 2 != 0:
                odd_node.append(node)
        distances = {}
        g_temp = dict_copy(self.node_neighbors, subgraph)
        for i in list(g_temp.keys()):
            temp = []
            for j in g_temp[i]:
                temp.append((j, 1))
            distances[i] = temp
        for node in odd_node:
            current = node
            dis=copy.deepcopy(distances)
            d, paths = dijkstra(dis, current)
            use_dict = dict_copy(paths, odd_node)
            d = dict_copy(d, odd_node)
            n_max = max(d.items(), key=lambda x: x[1])[0]
            path_len[d[n_max]] = use_dict[n_max]
        return max(path_len.items(), key=lambda x: x[0])[1]

def dijkstra(G, s):
    d = {}  # node distances from source
    predecessor = {}  # node predecessor on the shortest path

    # init
    for v in G:
        if v == s:
            d[v] = 0
        else:
            d[v] = float("inf")
        predecessor[v] = None

    Q = list(G.keys())
    while Q:
        u = min(Q, key=d.get)
        Q.remove(u)
        for v in G[u]:
            relax(u, v, d, predecessor)

    paths = {}
    for v in predecessor:
        paths[v] = [v]
        p = predecessor[v]
        while p is not None:
            paths[v].append(p)
            p = predecessor[p]
    return d, paths

def relax(u, v, d, predecessor):
    weight = v[1]
    v = v[0]
    if d[v] > d[u] + weight:
        d[v] = d[u] + weight
        predecessor[v] = u

def add_path(p1, p2):
    # 将路径 p2 嵌入到 p1 所在的序列里
    k = 1
    for i in range(len(p2)-1):
        p1.insert(p1.index(p2[0])+k, p2[i+1])
        k += 1
    return p1

def dict_copy(dct, nodes):
    temp = {}
    for i in nodes:
        temp[i] = dct[i]
    return temp

def is_connected(G):
    start_node = list(G)[0]
    color = {v: 'white' for v in G}
    color[start_node] = 'gray'
    S = [start_node]
    while len(S) != 0:
        u = S.pop()
        for v in G[u]:
            if color[v] == 'white':
                color[v] = 'gray'
                S.append(v)
            color[u] = 'black'
    return list(color.values()).count('black') == len(G)

def odd_degree_nodes(G):
    odd_degree_nodes = []
    for u in G:
        if len(G[u]) % 2 != 0:
            odd_degree_nodes.append(u)
    return odd_degree_nodes

def from_dict(G):
    links = []
    for u in G:
        for v in G[u]:
            links.append((u, v))
    return links

def fleury(G):
    odn = odd_degree_nodes(G)
    if len(odn) > 2 or len(odn) == 1:
        return 'Not Eulerian Graph'
    else:
        g = copy.deepcopy(G)
        trail = []
        if len(odn) == 2:
            u = odn[0]
        else:
            u = list(g)[0]
        while len(from_dict(g)) > 0:
            current_vertex = u
            for u in g[current_vertex]:
                g[current_vertex].remove(u)
                g[u].remove(current_vertex)
                bridge = not is_connected(g)
                if bridge:
                    g[current_vertex].append(u)
                    g[u].append(current_vertex)
                else:
                    break
            if bridge:
                g[current_vertex].remove(u)
                g[u].remove(current_vertex)
                g.pop(current_vertex)
            if (len(trail) == 0):
                trail.append(current_vertex)
                trail.append(u)
            else:
                trail.append(u)
        return trail

def euler(G, start=None):
    path = []
    g = copy.deepcopy(G)
    def hierholzer(node):
        if len(g[node]) == 0:
            path.append(node)
            return
        for n in g[node]:
            g[node].remove(n)
            g[n].remove(node)
            hierholzer(n)
            if len(g[node]) == 0:
                path.append(node)
                return

    odn = odd_degree_nodes(g)
    if len(odn) > 2 or len(odn) == 1:
        return 'Not Eulerian Graph'
    else:
        if start:
            u = start
        else:
            if len(odn) == 2:
                u = odn[0]
            else:
                u = list(g)[0]
        hierholzer(u)
    path.reverse()
    return path

def path_iden(Queue, g):
    # 找出 Queue 中哪条路径应该与 g 相连
    for n in g:
        for path in Queue:
            if (n in path):
                Queue.remove(path)
                return path, n
    return None, None

def verification(Queue, testG):
    for path in Queue:
        for i in range(len(path) - 1):
            testG[path[i]].remove(path[i + 1])
            testG[path[i + 1]].remove(path[i])
            i += 1

def find_path(MATRIX):
    """
    MATRIX: 传入的网络拓扑邻接矩阵 (numpy数组, 0/1 表示无/有连接)
    返回值: (num_fleury, num_path, Queue)
    """
    g = Graph()
    num_nodes = len(MATRIX)
    # 建立节点
    g.add_nodes([i + 1 for i in range(num_nodes)])
    # 建立边
    for i in range(num_nodes):
        for j in range(num_nodes):
            if MATRIX[i][j] != 0:
                g.add_edge((i + 1, j + 1))

    g.not_null_node()
    testG = copy.deepcopy(g.node_neighbors)
    Queue = []
    num_fleury = 0

    while len(g.A) > 0:
        g.degrees()
        subgraph = g.F1()
        n = len(subgraph)
        T = g.judge(subgraph)
        if (T > 0):
            # 说明该连通子图所有顶点度数都为偶数，直接找欧拉回路
            if (len(Queue) > 0):
                t_path, start = path_iden(Queue, subgraph[T])
                g_temp = dict_copy(g.node_neighbors, subgraph[T])
                result = euler(g_temp, start)
                if result != 'Not Eulerian Graph':
                    num_fleury += 1
                    g.F3(result)
                    result = add_path(t_path, result)  # 合并路径
                    Queue.append(result)
            else:
                g_temp = dict_copy(g.node_neighbors, subgraph[T])
                t_path = euler(g_temp)
                if t_path != 'Not Eulerian Graph':
                    num_fleury += 1
                    Queue.append(t_path)
                    g.F3(t_path)
            continue
        # 否则，找奇数度顶点进行匹配/拼接
        for i in range(1, n + 1):
            odd_num = g.F2(subgraph[i])
            if odd_num == 2:
                g_temp = dict_copy(g.node_neighbors, subgraph[i])
                path = euler(g_temp)
                if path != 'Not Eulerian Graph':
                    num_fleury += 1
            elif odd_num > 2:
                path = g.my_path(subgraph[i])
            else:
                # 没有奇数度顶点时直接跳过
                break
            Queue.append(path)
            g.F3(path)

    num_path = len(Queue)
    # 验证下是否所有边都被用到了(不一定必须)
    verification(Queue, testG)
    return num_fleury, num_path, Queue


# ============================================================
#      生成 FatTree(k) 的邻接矩阵（仅交换机，不含服务器）
# ============================================================
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


# ============================================================
#        生成 Spine-Leaf(k) 的邻接矩阵（仅 Leaf/Spine）
# ============================================================
def generate_spineleaf(k):
    """
    仅交换机, 不含服务器
    简单定义: 前 k 台为 Leaf, 后 k 台为 Spine, 共 2k。
    Leaf 与所有 Spine 全连接, 无 Spine-Spine 或 Leaf-Leaf 直连
    """
    total_switches = 2 * k
    matrix = np.zeros((total_switches, total_switches), dtype=int)

    # Leaf: [0..k-1], Spine: [k..2k-1]
    for leaf in range(k):
        for spine in range(k, 2*k):
            matrix[leaf][spine] = 1
            matrix[spine][leaf] = 1

    return matrix

def genSpineLeaf(swSum):  #SNum must be 3,6,9,12,15...
    L1 = int(swSum/3)
    L2 = L1*2

    topoList = [[0 for i in range(swSum)] for i in range(swSum)]

    for i in range(L1):
        for j in range(L1, swSum):
            topoList[i][j] = 1
            topoList[j][i] = 1

    return topoList
# ================
#      主程序
# ================
if __name__ == '__main__':
    i=10
    fattree = generate_fattree(i)
    print(fattree)
    swnum = i*i/4*5
    num_fleury, num_path, queue_paths = find_path(fattree)
    # end_time = time.clock()

    print(f"FatTree (k={i}, {swnum} 交换机) 拓扑测试结果：")
    print("  欧拉/费雷路径数量 =", num_fleury)
    print("  最终路径分段数 =", num_path)
    # print("  耗时(s) =", end_time - start_time)
    print("  路径队列 =", queue_paths)
    length = 0
    for path in queue_paths:
        print("  单条长度", len(path))
        length += len(path)
    print("  总长度", length)
    # for i in range(4, 15, 2):
    #     fattree = generate_fattree(i)
    #     swnum = i*i/4*5
    #     num_fleury, num_path, queue_paths = find_path(fattree)
    #     # end_time = time.clock()
    #
    #     print(f"FatTree (k={i}, {swnum} 交换机) 拓扑测试结果：")
    #     print("  欧拉/费雷路径数量 =", num_fleury)
    #     print("  最终路径分段数 =", num_path)
    #     # print("  耗时(s) =", end_time - start_time)
    #     print("  路径队列 =", queue_paths)
    #     length = 0
    #     for path in queue_paths:
    #         length += len(path)
    #     print("  长度", length)


    # sys.setrecursionlimit(20000)
    # for i in [21,45,90,120,180,240]:
    #     sp = genSpineLeaf(i)
    #     num_fleury, num_path, queue_paths = find_path(sp)
    #
    #
    #     print(f"FatTree ({i}交换机) 拓扑测试结果：")
    #     print("  欧拉/费雷路径数量 =", num_fleury)
    #     print("  最终路径分段数 =", num_path)
    #         # print("  耗时(s) =", end_time - start_time)
    #     print("  路径队列 =", queue_paths)
    #     length = 0
    #     for path in queue_paths:
    #         length += len(path)
    #     print("  长度", length)