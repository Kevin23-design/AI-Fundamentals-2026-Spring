from collections import deque
import sys


def parse_input():
    tokens = sys.stdin.buffer.read().split()
    if not tokens:
        return None

    data = [t.decode() for t in tokens]
    n = int(data[0])
    m = int(data[1])
    idx = 2

    maze = []
    for _ in range(n):
        if idx >= len(data):
            return None

        token = data[idx]
        if len(token) == m and all(ch in "01.#" for ch in token):
            row = [1 if ch in "1#" else 0 for ch in token]
            idx += 1
        else:
            if idx + m > len(data):
                return None
            vals = data[idx: idx + m]
            idx += m
            row = []
            for v in vals:
                if v in ("0", "."):
                    row.append(0)
                elif v in ("1", "#"):
                    row.append(1)
                else:
                    row.append(int(v))

        maze.append(row)

    if idx + 3 < len(data):
        sx, sy, gx, gy = map(int, data[idx: idx + 4])
    else:
        sx, sy = 0, 0
        gx, gy = n - 1, m - 1

    return maze, (sx, sy), (gx, gy)


def solve() -> None:
    parsed = parse_input()
    if parsed is None:
        return

    maze, start, goal = parsed
    n, m = len(maze), len(maze[0])
    sx, sy = start
    gx, gy = goal

    if not (0 <= sx < n and 0 <= sy < m and 0 <= gx < n and 0 <= gy < m):
        sys.stdout.write("-1")
        return

    if maze[sx][sy] != 0 or maze[gx][gy] != 0:
        sys.stdout.write("-1")
        return

    q = deque([(sx, sy)])
    dist = [[-1] * m for _ in range(n)]
    dist[sx][sy] = 0
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while q:
        x, y = q.popleft()
        if (x, y) == (gx, gy):
            break

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m and maze[nx][ny] == 0 and dist[nx][ny] == -1:
                dist[nx][ny] = dist[x][y] + 1
                q.append((nx, ny))

    sys.stdout.write(str(dist[gx][gy]))


if __name__ == "__main__":
    solve()
