from heapq import heappush, heappop

def heuristic(node, goal):
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

def astar(matrix, start, goal):
    start = (start.x, start.y)
    goal = (goal.x, goal.y)
    rows, cols = len(matrix), len(matrix[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    open_list = []
    heappush(open_list, (0, start))
    parent = dict()
    parent[start] = None
    g_score = {start: 0}

    while open_list:
        current_cost, current_node = heappop(open_list)

        if current_node == goal:
            path = []
            while current_node:
                path.append(current_node)
                current_node = parent[current_node]
            return path[::-1]

        for dx, dy in directions:
            neighbor = (current_node[0] + dx, current_node[1] + dy)

            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                tentative_g_score = g_score[current_node] + (1 if matrix[neighbor[0]][neighbor[1]] == 1 else 0)

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor, goal)
                    heappush(open_list, (f_score, neighbor))
                    parent[neighbor] = current_node

    return None