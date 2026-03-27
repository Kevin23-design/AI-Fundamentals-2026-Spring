from collections import deque
import sys


TARGET = "12345678x"
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def is_solvable(state: str) -> bool:
    vals = [c for c in state if c != "x"]
    inv = 0
    n = len(vals)
    for i in range(n):
        for j in range(i + 1, n):
            if vals[i] > vals[j]:
                inv += 1
    return inv % 2 == 0


def solve() -> None:
    tokens = sys.stdin.buffer.read().split()
    if not tokens:
        return

    start = "".join(t.decode() for t in tokens)
    if start == TARGET:
        sys.stdout.write("0")
        return

    if not is_solvable(start):
        sys.stdout.write("-1")
        return

    q = deque([start])
    dist = {start: 0}

    while q:
        state = q.popleft()
        d = dist[state]
        x = state.index("x")
        x_r, x_c = divmod(x, 3)

        for dr, dc in DIRS:
            nr, nc = x_r + dr, x_c + dc
            if not (0 <= nr < 3 and 0 <= nc < 3):
                continue

            y = nr * 3 + nc
            arr = list(state)
            arr[x], arr[y] = arr[y], arr[x]
            nxt = "".join(arr)

            if nxt in dist:
                continue

            dist[nxt] = d + 1
            if nxt == TARGET:
                sys.stdout.write(str(d + 1))
                return
            q.append(nxt)

    sys.stdout.write("-1")


if __name__ == "__main__":
    solve()
