from collections import deque
import heapq

import matplotlib.pyplot as plt


def _valid_setup(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    sx, sy = start
    gx, gy = goal
    if not (0 <= sx < rows and 0 <= sy < cols and 0 <= gx < rows and 0 <= gy < cols):
        return False
    if maze[sx][sy] != 0 or maze[gx][gy] != 0:
        return False
    return True


def _build_path(parent, start, goal):
    if goal not in parent:
        return []
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    if not path or path[0] != start:
        return []
    return path


def bfs_search(maze, start, goal):
    if not _valid_setup(maze, start, goal):
        return [], []

    rows, cols = len(maze), len(maze[0])
    q = deque([start])
    visited = {start}
    parent = {start: None}
    searched = [start]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            break
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 0 and (nx, ny) not in visited:
                visited.add((nx, ny))
                parent[(nx, ny)] = (x, y)
                searched.append((nx, ny))
                q.append((nx, ny))

    return searched, _build_path(parent, start, goal)


def dfs_search(maze, start, goal):
    if not _valid_setup(maze, start, goal):
        return [], []

    rows, cols = len(maze), len(maze[0])
    visited = set()
    searched = []
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best_path = []

    def dfs(cur, cur_path):
        nonlocal best_path
        if best_path and len(cur_path) >= len(best_path):
            return

        visited.add(cur)
        searched.append(cur)
        cur_path.append(cur)

        if cur == goal:
            best_path = cur_path[:]
        else:
            x, y = cur
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                nxt = (nx, ny)
                if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 0 and nxt not in visited:
                    dfs(nxt, cur_path)

        cur_path.pop()
        visited.remove(cur)

    dfs(start, [])
    return searched, best_path


def dijkstra_search(maze, start, goal):
    if not _valid_setup(maze, start, goal):
        return [], []

    rows, cols = len(maze), len(maze[0])
    inf = 10**18
    dist = [[inf] * cols for _ in range(rows)]
    dist[start[0]][start[1]] = 0
    parent = {start: None}
    searched = []
    pq = [(0, start[0], start[1])]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while pq:
        d, x, y = heapq.heappop(pq)
        if d != dist[x][y]:
            continue
        searched.append((x, y))
        if (x, y) == goal:
            break

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 0:
                nd = d + 1
                if nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    parent[(nx, ny)] = (x, y)
                    heapq.heappush(pq, (nd, nx, ny))

    return searched, _build_path(parent, start, goal)


def a_star_search(maze, start, goal):
    if not _valid_setup(maze, start, goal):
        return [], []

    def h(pos):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    rows, cols = len(maze), len(maze[0])
    inf = 10**18
    g = [[inf] * cols for _ in range(rows)]
    g[start[0]][start[1]] = 0
    parent = {start: None}
    searched = []
    pq = [(h(start), 0, start[0], start[1])]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while pq:
        f, cur_g, x, y = heapq.heappop(pq)
        if cur_g != g[x][y]:
            continue
        searched.append((x, y))
        if (x, y) == goal:
            break

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 0:
                ng = cur_g + 1
                if ng < g[nx][ny]:
                    g[nx][ny] = ng
                    parent[(nx, ny)] = (x, y)
                    heapq.heappush(pq, (ng + h((nx, ny)), ng, nx, ny))

    return searched, _build_path(parent, start, goal)


def run_search(maze, start, goal, algorithm):
    algo = algorithm.strip().lower()
    if algo == "bfs":
        return bfs_search(maze, start, goal)
    if algo == "dfs":
        return dfs_search(maze, start, goal)
    if algo == "dijkstra":
        return dijkstra_search(maze, start, goal)
    if algo in ("a*", "astar", "a_star"):
        return a_star_search(maze, start, goal)
    raise ValueError(f"Unknown algorithm: {algorithm}")


def draw_maze(ax, maze, path, searched, start, goal, title):
    rows, cols = len(maze), len(maze[0])
    ax.imshow(maze, cmap="Greys", interpolation="nearest")

    if searched:
        s_x, s_y = zip(*searched)
        ax.scatter(s_y, s_x, s=170, c="#8ecae6", marker="s", edgecolors="none", alpha=0.75)

    if path:
        p_x, p_y = zip(*path)
        ax.plot(p_y, p_x, marker="o", markersize=5.5, color="red", linewidth=2)

    ax.scatter(start[1], start[0], s=120, c="#2a9d8f", marker="o", edgecolors="black", linewidths=0.8)
    ax.scatter(goal[1], goal[0], s=140, c="#f4a261", marker="*", edgecolors="black", linewidths=0.8)

    ax.set_xticks(range(cols))
    ax.set_yticks(range(rows))
    ax.set_xticks([x - 0.5 for x in range(1, cols)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, rows)], minor=True)
    ax.grid(which="minor", color="black", linestyle="-", linewidth=1.2)
    ax.set_title(title, fontsize=10)


def visualize_single(maze, start, goal, algorithm):
    searched, path = run_search(maze, start, goal, algorithm)
    path_len = len(path) - 1 if path else -1
    title = f"{algorithm.upper()} | searched={len(searched)} | dist={path_len}"

    fig, ax = plt.subplots(1, 1, figsize=(6, 6))
    draw_maze(ax, maze, path, searched, start, goal, title)
    fig.tight_layout()
    plt.show()


def visualize_compare_all(maze, start, goal):
    algorithms = ["BFS", "DFS", "Dijkstra", "A*"]
    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    axes = axes.flatten()

    for ax, algo in zip(axes, algorithms):
        searched, path = run_search(maze, start, goal, algo)
        path_len = len(path) - 1 if path else -1
        title = f"{algo} | searched={len(searched)} | dist={path_len}"
        draw_maze(ax, maze, path, searched, start, goal, title)

    fig.suptitle("Maze Search Algorithm Comparison", fontsize=14)
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    maze = [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0],
    ]
    start = (0, 0)
    goal = (4, 4)

    # mode 可选："single" 或 "compare"
    mode = "compare"
    # algorithm 在 mode="single" 时生效，可选："BFS" "DFS" "Dijkstra" "A*"
    algorithm = "A*"

    if mode == "single":
        visualize_single(maze, start, goal, algorithm)
    else:
        visualize_compare_all(maze, start, goal)
