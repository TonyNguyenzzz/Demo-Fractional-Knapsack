# fractional_knapsack.py

from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Item:
    name: str
    value: float
    weight: float

def fractional_knapsack(items: List[Item], capacity: float) -> Tuple[float, List[Tuple[Item, float, float, float]], List[Item]]:
    """
    Thực hiện thuật toán Fractional Knapsack.

    Parameters:
        items (List[Item]): Danh sách các vật phẩm.
        capacity (float): Dung lượng tối đa của balo.

    Returns:
        Tuple containing:
            - Tổng giá trị của balo.
            - Danh sách các bước thực hiện (vật phẩm, phần trăm được thêm, tổng giá trị, dung lượng còn lại).
            - Danh sách các vật phẩm đã được sắp xếp theo tỷ lệ giá trị trên trọng lượng giảm dần.
    """
    # Sắp xếp các vật phẩm theo tỷ lệ giá trị trên trọng lượng giảm dần
    items_sorted = sorted(items, key=lambda item: item.value/item.weight, reverse=True)
    
    total_value = 0.0
    steps = []
    
    for item in items_sorted:
        if capacity <= 0:
            break
        if item.weight <= capacity:
            total_value += item.value
            capacity -= item.weight
            steps.append((item, 1, total_value, capacity))
        else:
            fraction = capacity / item.weight
            total_value += item.value * fraction
            steps.append((item, fraction, total_value, 0))
            capacity = 0
    return total_value, steps, items_sorted
