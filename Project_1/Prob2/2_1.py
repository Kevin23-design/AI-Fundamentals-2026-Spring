from collections import deque
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
		graph[u].append(v)

	dist = [-1] * (n + 1)
	dist[1] = 0
	q = deque([1])

	while q:
		u = q.popleft()
		if u == n:
			break
		for v in graph[u]:
			if dist[v] == -1:
				dist[v] = dist[u] + 1
				q.append(v)

	sys.stdout.write(str(dist[n]))


if __name__ == "__main__":
	solve()
