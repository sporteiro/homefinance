from collections import Counter
from decimal import Decimal


class StatisticsCalculator:
    QUANTIZE = Decimal("0.01")

    @classmethod
    def mean(cls, values: list[Decimal]) -> Decimal:
        if not values:
            return Decimal("0")
        total = sum(values, Decimal("0"))
        return (total / Decimal(len(values))).quantize(cls.QUANTIZE)

    @classmethod
    def median(cls, values: list[Decimal]) -> Decimal:
        if not values:
            return Decimal("0")
        ordered = sorted(values)
        size = len(ordered)
        middle = size // 2
        if size % 2 == 1:
            return ordered[middle].quantize(cls.QUANTIZE)
        left = ordered[middle - 1]
        right = ordered[middle]
        return ((left + right) / Decimal("2")).quantize(cls.QUANTIZE)

    @classmethod
    def mode(cls, values: list[Decimal]) -> Decimal:
        if not values:
            return Decimal("0")
        counter = Counter(values)
        most_common = counter.most_common()
        highest_count = most_common[0][1]

        if highest_count == 1:
            return Decimal("0")

        modes = [value for value, count in most_common if count == highest_count]
        return min(modes).quantize(cls.QUANTIZE)
