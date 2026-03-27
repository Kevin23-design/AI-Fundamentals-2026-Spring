import heapq
import sys


TARGET = "12345678x"
GOAL_POS = {TARGET[i]: (i // 3, i % 3) for i in range(9) if TARGET[i] != "x"}
DIRS = [(-1, 0, "u"), (1, 0, "d"), (0, -1, "l"), (0, 1, "r")]


def is_solvable(state: str) -> bool:
    vals = [c for c in state if c != "x"]
    inv = 0
    n = len(vals)
    for i in range(n):
        for j in range(i + 1, n):
            if vals[i] > vals[j]:
                inv += 1
    return inv % 2 == 0


def h(state: str) -> int:
    s = 0
    for i, ch in enumerate(state):
        if ch == "x":
            continue
        r, c = divmod(i, 3)
        gr, gc = GOAL_POS[ch]
        s += abs(r - gr) + abs(c - gc)
    return s


def solve() -> None:
    tokens = sys.stdin.buffer.read().split()
    if not tokens:
        return

    start = "".join(t.decode() for t in tokens)

    if not is_solvable(start):
        sys.stdout.write("unsolvable")
        return

    if start == TARGET:
        sys.stdout.write("")
        return

    g = {start: 0}
    prev = {start: (None, "")}
    pq = [(h(start), 0, start)]

    while pq:
        f, dist, state = heapq.heappop(pq)
        if dist != g.get(state, 10**18):
            continue
        if state == TARGET:
            break

        x = state.index("x")
        x_r, x_c = divmod(x, 3)

        for dr, dc, op in DIRS:
            nr, nc = x_r + dr, x_c + dc
            if not (0 <= nr < 3 and 0 <= nc < 3):
                continue

            y = nr * 3 + nc
            arr = list(state)
            arr[x], arr[y] = arr[y], arr[x]
            nxt = "".join(arr)
            nd = dist + 1

            if nd < g.get(nxt, 10**18):
                g[nxt] = nd
                prev[nxt] = (state, op)
                heapq.heappush(pq, (nd + h(nxt), nd, nxt))

    if TARGET not in prev:
        sys.stdout.write("unsolvable")
        return

    path = []
    cur = TARGET
    while cur != start:
        p, op = prev[cur]
        path.append(op)
        cur = p
    path.reverse()
    sys.stdout.write("".join(path))


if __name__ == "__main__":
    solve()
