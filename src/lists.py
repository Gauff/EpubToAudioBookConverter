def find_difference(list1, list2):
    set1 = set(list1)
    set2 = set(list2)

    # Find elements in set1 but not in set2
    difference1 = list(set1 - set2)

    # Find elements in set2 but not in set1
    difference2 = list(set2 - set1)

    return difference1, difference2