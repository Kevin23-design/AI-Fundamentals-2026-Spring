import sys


sys.setrecursionlimit(10**7)


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

    visited = [[False] * m for _ in range(n)]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best = [10**18]

    def dfs(x: int, y: int, step: int) -> None:
        if step >= best[0]:
            return

        if (x, y) == (gx, gy):
            best[0] = step
            return

        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m and maze[nx][ny] == 0 and not visited[nx][ny]:
                visited[nx][ny] = True
                dfs(nx, ny, step + 1)
                visited[nx][ny] = False

    visited[sx][sy] = True
    dfs(sx, sy, 0)

    ans = -1 if best[0] == 10**18 else best[0]
    sys.stdout.write(str(ans))


if __name__ == "__main__":
    solve()
