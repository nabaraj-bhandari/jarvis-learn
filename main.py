# main.py

import sys
from core.dispatcher import run


def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py "your command"')
        sys.exit(1)

    # Join all args in case user didn't quote the string
    user_input = " ".join(sys.argv[1:])
    response = run(user_input)
    print(response)


if __name__ == "__main__":
    main()
