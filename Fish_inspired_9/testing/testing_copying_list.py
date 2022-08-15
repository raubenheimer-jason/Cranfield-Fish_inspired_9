
l1 = [[1, 1, 11], [2, 2, 22]]
l2 = [[0, 0, 0], [0, 0, 0]]

print(f"l1: {l1}")
print(f"l2: {l2}")
print()

# l2[:] = l1[:]
l2 = l1[:]
# l2 = l1 #! this doesnt work

l1[0] = [3, 3, 33]
l1[1] = [4, 4, 44]

print(f"l1: {l1}")
print(f"l2: {l2}")
