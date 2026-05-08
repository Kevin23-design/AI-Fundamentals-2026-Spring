import sys


def solve() -> None:
	tokens = sys.stdin.buffer.read().split()
	if not tokens:
		return

	vals = []
	for t in tokens:
		s = t.decode()
		if s != "x":
			vals.append(int(s))

	inv = 0
	n = len(vals)
	for i in range(n):
		for j in range(i + 1, n):
			if vals[i] > vals[j]:
				inv += 1

	sys.stdout.write("1" if inv % 2 == 0 else "0")


if __name__ == "__main__":
	solve()
