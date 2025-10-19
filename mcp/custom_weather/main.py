def test(num=0):
    print("test...")
    def test_decorator(func):
        print("test_decorator...")
        def wrapper(*args, **kwargs):
            nonlocal num
            num += 1
            print("Before the function call, num: " + str(num))
            result = func(*args, **kwargs)
            print("After the function call")
            return result
        return wrapper
    return test_decorator

@test()
def main():
    print("Hello from weather!")

if __name__ == "__main__":
    print("This is main.py")
    main()
    main()
    main()