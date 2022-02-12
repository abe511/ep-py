
# task 2.1
def strlen(str):
    counter = 0
    for c in str:
        counter += 1
    return counter


# task 2.2
def charCount(str):
    res = {}
    c = ''
    for char in str:
        c = char.lower()
        res[c] = res[c] + 1 if c in res else 1
    return res


# task 2.3.1
def sortUnique(lst):
    res = []
    for word in lst:
        if word not in res:
            res.append(word)
    res.sort()
    print(res)


# task 2.3.2
def divisors(num):
    i = 1
    res = set()
    while i <= num:
        if num % i == 0:
            res.add(i)
        i += 1
    print(res)


# task 2.4
def sortByKey(dct):
    res = []
    for key in dct:
        res.append(key)
        print(key)


# task 2.5
# type 1
def uniqueDictValues(lst):
    res = set()
    for dct in lst:
        for k in dct:
            res.add(dct[k])
    print(res)

# type 2
# def uniqueDictValues(lst):
#     res = []    
#     for dct in lst:
#         for k in dct:
#             if dct[k] not in res:
#                 res.append(dct[k])
#     print(res)


# task 2.6
def converter(tup):
    ln = len(tup)
    order = 0
    res = 0
    while ln:
        # res += tup[ln - 1] * pow(10, order)
        res += tup[ln - 1] * (10 ** order)
        order += 1
        ln -= 1
    print(res)


# task 2.7
def prettyPrint(a, b, c, d):
    x = c
    y = 1
    while y <= b:
        if x == c and y == 1:
            print(" ", "\t", end="")
        elif x == c:
            print(y, "\t", end="")
        print(y * x, "\t", end="")
        x += 1
        if x > d:
            x = c
            if y == 1:
                y = a
            else:
                y += 1
            print("\r")