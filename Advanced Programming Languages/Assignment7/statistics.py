class StatisticsCalculator:
    def __init__(self, data: list[int]):
        self.data = list(data)

    def mean(self) -> float:
        if not self.data:
            return 0.0
        return sum(self.data) / len(self.data)

    def median(self) -> float:
        if not self.data:
            return 0.0
        sorted_data = sorted(self.data)
        n = len(sorted_data)
        mid = n // 2
        if n % 2 == 1:
            return float(sorted_data[mid])
        return (sorted_data[mid - 1] + sorted_data[mid]) / 2.0

    def mode(self) -> list[int]:
        if not self.data:
            return []
        freq: dict[int, int] = {}
        for x in self.data:
            freq[x] = freq.get(x, 0) + 1
        max_count = max(freq.values())
        return sorted(k for k, c in freq.items() if c == max_count)


if __name__ == "__main__":
    data = [4, 2, 3, 2, 5, 2, 4]
    calc = StatisticsCalculator(data)
    print("Data:", " ".join(map(str, data)))
    print("Mean:", f"{calc.mean():.2f}")
    print("Median:", f"{calc.median():.2f}")
    print("Mode:", " ".join(map(str, calc.mode())))
