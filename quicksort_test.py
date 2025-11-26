"""
快速排序算法实现和测试
"""


def quicksort(arr):
    """
    快速排序算法实现
    
    参数:
        arr: 待排序的列表
    
    返回:
        排序后的列表
    """
    # 基本情况：如果列表长度小于等于1，直接返回
    if len(arr) <= 1:
        return arr
    
    # 选择基准元素（这里选择中间元素）
    pivot = arr[len(arr) // 2]
    
    # 分割数组
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    # 递归排序并合并
    return quicksort(left) + middle + quicksort(right)


def test_quicksort():
    """测试快速排序函数"""
    
    # 测试用例1：普通整数列表
    test1 = [64, 34, 25, 12, 22, 11, 90]
    result1 = quicksort(test1)
    expected1 = [11, 12, 22, 25, 34, 64, 90]
    assert result1 == expected1, f"测试1失败: 期望 {expected1}, 得到 {result1}"
    print("✓ 测试1通过: 普通整数列表排序")
    
    # 测试用例2：已排序的列表
    test2 = [1, 2, 3, 4, 5]
    result2 = quicksort(test2)
    expected2 = [1, 2, 3, 4, 5]
    assert result2 == expected2, f"测试2失败: 期望 {expected2}, 得到 {result2}"
    print("✓ 测试2通过: 已排序列表")
    
    # 测试用例3：逆序列表
    test3 = [5, 4, 3, 2, 1]
    result3 = quicksort(test3)
    expected3 = [1, 2, 3, 4, 5]
    assert result3 == expected3, f"测试3失败: 期望 {expected3}, 得到 {result3}"
    print("✓ 测试3通过: 逆序列表排序")
    
    # 测试用例4：包含重复元素的列表
    test4 = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    result4 = quicksort(test4)
    expected4 = [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]
    assert result4 == expected4, f"测试4失败: 期望 {expected4}, 得到 {result4}"
    print("✓ 测试4通过: 包含重复元素的列表")
    
    # 测试用例5：单个元素
    test5 = [42]
    result5 = quicksort(test5)
    expected5 = [42]
    assert result5 == expected5, f"测试5失败: 期望 {expected5}, 得到 {result5}"
    print("✓ 测试5通过: 单个元素")
    
    # 测试用例6：空列表
    test6 = []
    result6 = quicksort(test6)
    expected6 = []
    assert result6 == expected6, f"测试6失败: 期望 {expected6}, 得到 {result6}"
    print("✓ 测试6通过: 空列表")
    
    # 测试用例7：负数列表
    test7 = [-5, -2, -8, -1, -9]
    result7 = quicksort(test7)
    expected7 = [-9, -8, -5, -2, -1]
    assert result7 == expected7, f"测试7失败: 期望 {expected7}, 得到 {result7}"
    print("✓ 测试7通过: 负数列表排序")
    
    # 测试用例8：混合正负数列表
    test8 = [-3, 5, -1, 0, 2, -4, 1]
    result8 = quicksort(test8)
    expected8 = [-4, -3, -1, 0, 1, 2, 5]
    assert result8 == expected8, f"测试8失败: 期望 {expected8}, 得到 {result8}"
    print("✓ 测试8通过: 混合正负数列表")
    
    print("\n所有测试通过！✓")


if __name__ == "__main__":
    print("开始测试快速排序算法...\n")
    test_quicksort()
    
    # 演示使用
    print("\n" + "="*50)
    print("演示示例:")
    print("="*50)
    demo_list = [64, 34, 25, 12, 22, 11, 90, 5]
    print(f"原始列表: {demo_list}")
    sorted_list = quicksort(demo_list)
    print(f"排序后:   {sorted_list}")
