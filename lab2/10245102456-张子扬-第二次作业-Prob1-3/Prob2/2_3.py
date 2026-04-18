import heapq
import sys


def solve() -> None:
	data = sys.stdin.buffer.read().split()
	if not data:
		return

	it = iter(map(int, data))
	n = next(it)
	m = next(it)

	graph = [[] for _ in range(n + 1)]
	for _ in range(m):
		u = next(it)
		v = next(it)
		w = next(it)
		graph[u].append((v, w))

	inf = 10**18
	dist = [inf] * (n + 1)
	dist[1] = 0

	pq = [(0, 1)]
	while pq:
		d, u = heapq.heappop(pq)
		if d != dist[u]:
			continue
		if u == n:
			break

		for v, w in graph[u]:
			nd = d + w
			if nd < dist[v]:
				dist[v] = nd
				heapq.heappush(pq, (nd, v))

	ans = -1 if dist[n] == inf else dist[n]
	sys.stdout.write(str(ans))


if __name__ == "__main__":
	solve()
