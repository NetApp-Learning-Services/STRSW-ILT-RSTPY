### Python script to display the first ten Fibonacci numbers ###

a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
for value in range (0, 10):
    a[value] = value
print (a[0])
print (a[1])
for value in range (1, 9):
    fib = a[value-1] + a[value]
    print (fib)
    if value < 9:
        a[value+1] = fib
