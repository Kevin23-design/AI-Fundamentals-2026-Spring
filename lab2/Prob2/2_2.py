import sys


def solve() -> None:
	data = sys.stdin.buffer.read().split()
	if not data:
		return

	it = iter(map(int, data))
	n = next(it)
	m = next(it)

	inf = 10**18
	dist = [inf] * (n + 1)
	st = [False] * (n + 1)

	graph = [[] for _ in range(n + 1)]
	for _ in range(m):
		u = next(it)
		v = next(it)
		w = next(it)
		graph[u].append((v, w))

	dist[1] = 0

	for _ in range(n):
		t = -1
		for i in range(1, n + 1):
			if not st[i] and (t == -1 or dist[i] < dist[t]):
				t = i

		if t == -1 or dist[t] == inf:
			break

		st[t] = True
		for v, w in graph[t]:
			nd = dist[t] + w
			if nd < dist[v]:
				dist[v] = nd

	ans = -1 if dist[n] == inf else dist[n]
	sys.stdout.write(str(ans))


if __name__ == "__main__":
	solve()
