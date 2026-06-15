import argparse
import sys

from passgen_core import generate_password, score_password


def ask_yes_no(prompt, default=True):
    hint = "Y/n" if default else "y/N"
    while True:
        ans = input(f"{prompt} [{hint}]: ").strip().lower()
        if ans == "":
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("  just type y or n")


def run_interactive():
    print()
    print("  Random Password Generator")
    print("  -------------------------")
    print()

    while True:
        raw = input("  password length (8-128): ").strip()
        try:
            length = int(raw)
            if 8 <= length <= 128:
                break
            print("  keep it between 8 and 128")
        except ValueError:
            print("  that's not a number")

    use_lower = ask_yes_no("  include lowercase letters?", True)
    use_upper = ask_yes_no("  include uppercase letters?", True)
    use_digits = ask_yes_no("  include numbers?", True)
    use_symbols = ask_yes_no("  include symbols?", False)

    if not any([use_lower, use_upper, use_digits, use_symbols]):
        print("  you need at least one character type, using all letters + numbers")
        use_lower = use_upper = use_digits = True

    exclude_ambiguous = ask_yes_no("  skip confusing chars like 0/O and l/1?", False)
    require_each = ask_yes_no("  force at least one of each selected type?", True)
    no_repeat = ask_yes_no("  avoid back-to-back duplicate characters?", False)

    count_raw = input("  how many passwords? [1]: ").strip()
    count = 1
    if count_raw:
        try:
            count = max(1, min(20, int(count_raw)))
        except ValueError:
            count = 1

    print()
    for i in range(count):
        try:
            pwd = generate_password(
                length,
                use_lower=use_lower,
                use_upper=use_upper,
                use_digits=use_digits,
                use_symbols=use_symbols,
                exclude_ambiguous=exclude_ambiguous,
                require_each_type=require_each,
                no_adjacent_repeat=no_repeat,
            )
        except ValueError as e:
            print(f"  error: {e}")
            return

        _, strength = score_password(pwd, use_lower, use_upper, use_digits, use_symbols)
        prefix = f"  [{i + 1}]" if count > 1 else " "
        print(f"{prefix} {pwd}  ({strength})")

    print()


def main():
    parser = argparse.ArgumentParser(description="generate random passwords from the terminal")
    parser.add_argument("-l", "--length", type=int, default=16, help="password length")
    parser.add_argument("-n", "--count", type=int, default=1, help="how many to generate")
    parser.add_argument("--no-lower", action="store_true")
    parser.add_argument("--no-upper", action="store_true")
    parser.add_argument("--no-digits", action="store_true")
    parser.add_argument("-s", "--symbols", action="store_true", help="include symbols")
    parser.add_argument("--ambiguous", action="store_true", help="allow 0/O/l/1 etc")
    parser.add_argument("--loose", action="store_true", help="don't require each char type")
    parser.add_argument("--repeat", action="store_true", help="allow adjacent duplicates")
    parser.add_argument("-i", "--interactive", action="store_true", help="guided mode")

    args = parser.parse_args()

    if args.interactive or len(sys.argv) == 1:
        run_interactive()
        return

    use_lower = not args.no_lower
    use_upper = not args.no_upper
    use_digits = not args.no_digits
    use_symbols = args.symbols

    if not any([use_lower, use_upper, use_digits, use_symbols]):
        print("error: enable at least one character type", file=sys.stderr)
        sys.exit(1)

    length = max(1, min(256, args.length))
    count = max(1, min(50, args.count))

    for _ in range(count):
        try:
            pwd = generate_password(
                length,
                use_lower=use_lower,
                use_upper=use_upper,
                use_digits=use_digits,
                use_symbols=use_symbols,
                exclude_ambiguous=not args.ambiguous,
                require_each_type=not args.loose,
                no_adjacent_repeat=not args.repeat,
            )
            print(pwd)
        except ValueError as e:
            print(f"error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
