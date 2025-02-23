#!//usr//bin//python
import heapq
import sys
import numpy as np
import random

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


def dijkstra(adj, start):
    n = len(adj[0])
    distances = [float('inf')] * n
    distances[start] = 0
    visited = [False] * n
    heap = [(0, start)]

    while heap:
        current_distance, u = heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u] = True

        for v in range(n):
            if adj[u][v] != 0 and not visited[v]:
                if distances[v] > current_distance + 1:
                    distances[v] = current_distance + 1
                    heapq.heappush(heap, (distances[v], v))
    return distances

def transform_graph(old, depot_list):
    print("")
    new_node_num = len(old) + len(depot_list)
    none_depot_nodes = []
    copied_depot_nodes = []
    for i in range(len(depot_list)):
        copied_depot_nodes.append(len(old)+i)
    for i in range(len(old)):
        if i not in depot_list:
            none_depot_nodes.append(i)
    print("none_depot_nodes: ", none_depot_nodes)
    print("copied_depot_nodes: ", copied_depot_nodes)
    print("depot_nodes: ", depot_list)
    expanded_array = [[100 for _ in range(new_node_num)] for _ in range(new_node_num)]

    for i in range(len(old)):
        for j in range(len(old)):
            expanded_array[i][j] = old[i][j]

    for common_node in none_depot_nodes:
        depot_index = 0
        for copy_depot_node in copied_depot_nodes:

            expanded_array[common_node][copy_depot_node] = expanded_array[common_node][depot_list[depot_index]]
            expanded_array[copy_depot_node][common_node] = expanded_array[depot_list[depot_index]][common_node]
            depot_index += 1

    depot_index = 0
    for copy_depot_node in copied_depot_nodes:
        expanded_array[copy_depot_node][depot_list[depot_index]] = 0
        expanded_array[depot_list[depot_index]][copy_depot_node] = 0
        if depot_index < len(depot_list)-1:
            expanded_array[copy_depot_node][depot_list[depot_index+1]] = 0
            expanded_array[depot_list[depot_index+1]][copy_depot_node] = 0
        if depot_index == len(depot_list) - 1:
            expanded_array[copy_depot_node][depot_list[0]] = 0
            expanded_array[depot_list[0]][copy_depot_node] = 0
        depot_index += 1

    for i in copied_depot_nodes:
        expanded_array[i][i] = 0

    # print("new distance matrix：")
    # for row in expanded_array:
    #     print(row)
    return expanded_array

def adjacency_matrix_to_paths(adj_matrix):
    """
    Convert an adjacency matrix to a list of direct paths.

    Parameters:
        adj_matrix (list of list of int): The adjacency matrix of the graph.
                                          A value of 1 indicates a connection.
    Returns:
        list of tuple: A list of tuples representing direct paths (i, j).
    """
    paths = []
    for i in range(len(adj_matrix)):
        for j in range(i + 1, len(adj_matrix)):  # Avoid duplicate paths (i, j) and (j, i)
            if adj_matrix[i][j] == 1:  # Check if there is a direct connection
                paths.append((i+1, j+1))  # Add the path (i, j)
    return paths


def generate_uncovered_edges_matrix(adj_matrix, path_list):
    """
    Generate a new adjacency matrix representing edges not covered by the given path list.

    Parameters:
        adj_matrix (list of list of int): The original adjacency matrix.
        path_list (list of list of int): The list of paths, where each path is a sequence of nodes (1-based index).

    Returns:
        list of list of int: A new adjacency matrix representing uncovered edges.
    """
    n = len(adj_matrix)
    uncovered_matrix = np.array(adj_matrix, dtype=int)

    # Mark edges in the path list as covered (0 in the new matrix)
    for path in path_list:
        for i in range(len(path) - 1):
            u, v = path[i] - 1, path[i + 1] - 1  # Convert 1-based index to 0-based
            uncovered_matrix[u][v] = 0
            uncovered_matrix[v][u] = 0  # Since the graph is undirected

    return uncovered_matrix.tolist()





if __name__ == '__main__':
    topo, host, sNum = genFatTree(4)  # podsNum must be larger than 2, and must be even number
    print("topo:")
    for i in topo:
        for j in i:
            print(j, end=' ')
        print("")
    print("probe depot:")
    for i in host:
        print(i, end=' ')
    print("")
    print("total switch nums:")
    print(sNum)

    distance_matrix = []
    for node in range(len(topo[0])):
        distance = dijkstra(topo, node)
        distance_matrix.append(distance)
    print("distance matrix:")
    for i in distance_matrix:
        for j in i:
            print(j, end=' ')
        print("")

    depot_nodes = [12,14,16,18]
    new_matrix = transform_graph(distance_matrix, depot_nodes)
    print("transformed distance matrix:")
    for i in new_matrix:
        for j in i:
            print(j, end=' ')
        print("")

    path_list = adjacency_matrix_to_paths(topo)
    print("path list:", path_list)

    # Example path list (1-based index)
    path_list = [
        [16, 7, 2, 5, 13],
        [20, 12, 3, 8, 15],
        [18, 10, 4, 6, 14],
        [19, 11, 1, 9, 17]
    ]

    # Generate the new adjacency matrix
    new_adj_matrix = generate_uncovered_edges_matrix(topo, path_list)

    # Print the new adjacency matrix
    print("new adj matrix:")
    for row in new_adj_matrix:
        print(row)
    path_list = adjacency_matrix_to_paths(new_adj_matrix)
    print("path list:", path_list)