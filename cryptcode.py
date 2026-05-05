import sys

from algorithms.caesar.caesar_decryption import caesar_decrypt
from algorithms.caesar.caesar_encryption import caesar_encrypt
from algorithms.reverse.reverse_decryption import reverse_decrypt
from algorithms.reverse.reverse_encryption import reverse_encrypt
from algorithms.addx.addx_decryption import addx_decrypt
from algorithms.addx.addx_encryption import addx_encrypt

# =================================== Algorithms ===================================
# Add new algorithms here.
# Each number must exist in both dictionaries.

ENCRYPTORS = {
    "1": caesar_encrypt,
    "2": reverse_encrypt,
    "3": addx_encrypt,
}

DECRYPTORS = {
    "1": caesar_decrypt,
    "2": reverse_decrypt,
    "3": addx_decrypt,
}

# =================================== Public/Private Key Loader ===================================
    
def load_key_value(key_path: str) -> int:
    with open(key_path, "r", encoding="utf-8") as file:
        key_text = file.read().strip()

    if not key_text.isdigit():
        raise ValueError("Key file must contain a number.")

    return int(key_text)

def validate_key_pair(public_key: int, private_key: int) -> None:
    if public_key == private_key:
        raise ValueError("Public and private keys must be different.")

    if (public_key + private_key) % 26 != 0:
        raise ValueError(
            "Invalid key pair. For Caesar, public_key + private_key must equal 26."
        )

# =================================== File Encryption ===================================

def encrypt_file(input_path: str, output_path: str, key_numbers: list[str], public_key_path: str = "keys/public.key") -> None:
    public_key = load_key_value(public_key_path)
    private_key = load_key_value("keys/private.key")
    validate_key_pair(public_key, private_key)

    with open(input_path, "r", encoding="utf-8") as file:
        plain_lines = [line.rstrip("\n") for line in file]

    code_lines = [line for line in plain_lines if line.strip() != ""]

    if len(key_numbers) == 1:
        keys = key_numbers * len(code_lines)
    else:
        keys = key_numbers

    if len(keys) != len(code_lines):
        raise ValueError("Number of keys must match number of non-empty code lines.")

    encrypted_lines = []
    key_index = 0

    for line in plain_lines:
        if line.strip() == "":
            encrypted_lines.append("")
            continue

        key = keys[key_index]

        if key not in ENCRYPTORS:
            raise ValueError(f"Unknown encryptor key: {key}")

        if key == "1":
            encrypted_line = ENCRYPTORS[key](line, public_key)
        else:
            encrypted_line = ENCRYPTORS[key](line)

        encrypted_lines.append(encrypted_line)
        key_index += 1

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("Key: " + " ".join(keys) + "\n\n")
        for line in encrypted_lines:
            file.write(line + "\n")

    print(f"Encrypted file created: {output_path}")

# =================================== File Decryption ===================================

def load_and_decrypt_program(path: str, private_key_path: str = "keys/private.key") -> list[str]:
    public_key = load_key_value("keys/public.key")
    private_key = load_key_value(private_key_path)
    validate_key_pair(public_key, private_key)

    with open(path, "r", encoding="utf-8") as file:
        all_lines = [line.rstrip("\n") for line in file]

    if not all_lines or not all_lines[0].startswith("Key:"):
        raise ValueError("CryptCode programs must start with 'Key:'")

    keys = all_lines[0].replace("Key:", "").strip().split()
    encrypted_lines = all_lines[1:]

    encrypted_code_lines = [line for line in encrypted_lines if line.strip() != ""]

    if len(keys) != len(encrypted_code_lines):
        raise ValueError("Number of keys must match number of non-empty encrypted lines.")

    decrypted_lines = []
    key_index = 0

    for line in encrypted_lines:
        if line.strip() == "":
            decrypted_lines.append("")
            continue

        key = keys[key_index]

        if key not in DECRYPTORS:
            raise ValueError(f"Unknown decryptor key: {key}")

        if key == "1":
            decrypted_line = DECRYPTORS[key](line, private_key)
        else:
            decrypted_line = DECRYPTORS[key](line)

        decrypted_lines.append(decrypted_line)
        key_index += 1

    return decrypted_lines

# =================================== Interpreter Utility Functions ===================================

def find_matching_end(lines: list[str], start_index: int) -> int:
    """
    Find the matching 'end' for a block command like count or repeat.

    This lets CryptCode support:

        count i from 1 to 5
            print i
        end

        repeat 3
            print Hello
        end
    """

    depth = 0

    for index in range(start_index, len(lines)):
        line = lines[index].strip()

        if line.startswith("count ") or line.startswith("repeat ") or line.startswith("when "):
            depth += 1
        elif line == "end":
            if depth == 0:
                return index
            depth -= 1

    raise ValueError("Missing 'end'.")

def get_value(token: str, variables: dict[str, int]) -> int:
    """Return a number directly, or look up a variable value."""
    if token in variables:
        return variables[token]

    return int(token)

def eval_expression(expr: str, variables: dict[str, int]) -> int:
    """
    Evaluate simple arithmetic expressions.

    Important:
        requires spaces between values and operators.
        Example: x + 2 works, but x+2 does not.
    """

    parts = expr.split()

    # Single value, like:
    # 5
    # x
    if len(parts) == 1:
        return get_value(parts[0], variables)

    # Simple binary expression, like:
    # x + 2
    # i mod 3
    if len(parts) == 3:
        left = get_value(parts[0], variables)
        operator = parts[1]
        right = get_value(parts[2], variables)

        if operator == "+":
            return left + right
        elif operator == "-":
            return left - right
        elif operator == "*":
            return left * right
        elif operator == "/":
            return left // right
        elif operator == "mod":
            return left % right
        else:
            raise ValueError(f"Unknown operator: {operator}")

    raise ValueError(f"Invalid expression: {expr}")

def condition_is_true(line: str, variables: dict[str, int]) -> bool:
    """
    Evaluate simple when conditions.

    Supported examples:
        when i is 3
        when i is not 3
        when i greater 3
        when i less 10
        when i mod 3 is 0
    """

    parts = line.split()

    if len(parts) == 4 and parts[2] == "is":
        left = get_value(parts[1], variables)
        right = get_value(parts[3], variables)
        return left == right

    if len(parts) == 5 and parts[2] == "is" and parts[3] == "not":
        left = get_value(parts[1], variables)
        right = get_value(parts[4], variables)
        return left != right

    if len(parts) == 4 and parts[2] == "greater":
        left = get_value(parts[1], variables)
        right = get_value(parts[3], variables)
        return left > right

    if len(parts) == 4 and parts[2] == "less":
        left = get_value(parts[1], variables)
        right = get_value(parts[3], variables)
        return left < right

    if len(parts) == 6 and parts[2] == "mod" and parts[4] == "is":
        left = get_value(parts[1], variables)
        divisor = get_value(parts[3], variables)
        expected = get_value(parts[5], variables)
        return left % divisor == expected

    raise ValueError(f"Invalid when condition: {line}")

def execute_when_chain(
    lines: list[str],
    start_index: int,
    variables: dict[str, int],
    line_offset: int = 0
) -> int:
    """
    Execute a when / else chain.

    Example:

        when i mod 3 is 0
            print Fizz
        else
            print i
    """

    branches = []
    i = start_index

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("when "):
            condition = line
            block_start = i + 1
            i += 1

            while i < len(lines):
                next_line = lines[i].strip()
                if next_line.startswith("when ") or next_line == "else" or next_line == "end":
                    break
                i += 1

            branches.append((condition, lines[block_start:i], block_start))

        elif line == "else":
            block_start = i + 1
            i += 1

            while i < len(lines) and lines[i].strip() != "end":
                i += 1

            branches.append(("else", lines[block_start:i], block_start))

        elif line == "end":
            break

        else:
            break

    for condition, block, block_start in branches:
        if condition == "else" or condition_is_true(condition, variables):
            execute_lines(block, variables, line_offset + block_start)
            break

    return i

# =================================== Core Interpreter ===================================

def execute_lines(lines: list[str], variables: dict[str, int] | None = None, line_offset: int = 0) -> None:
    """
    Execute decrypted CryptCode lines.

    Supported commands:
        print Hello
        print i

        count i from 1 to 5
            print i
        end

        repeat 3
            print Hello
        end

        when i mod 3 is 0
            print Fizz
        else
            print i
        end
    """

    if variables is None:
        variables = {}

    i = 0

    while i < len(lines):
        line = lines[i].strip()
        current_line_number = line_offset + i + 1

        try:
            if line == "":
                i += 1
                continue

            if line.startswith("print "):
                message = line[len("print "):]

                if message in variables:
                    print(variables[message])
                else:
                    print(message)

                i += 1

            elif line.startswith("set "):
                parts = line.split()

                if len(parts) < 4 or parts[2] != "to":
                    raise ValueError(f"Invalid set syntax: {line}")

                variable_name = parts[1]
                expression = " ".join(parts[3:])

                variables[variable_name] = eval_expression(expression, variables)

                i += 1

            elif line.startswith("count "):
                parts = line.split()

                if len(parts) != 6 or parts[2] != "from" or parts[4] != "to":
                    raise ValueError(f"Invalid count syntax: {line}")

                variable_name = parts[1]
                start = int(parts[3])
                end = int(parts[5])

                block_start = i + 1
                block_end = find_matching_end(lines, block_start)

                block = lines[block_start:block_end]

                for value in range(start, end + 1):
                    variables[variable_name] = value
                    execute_lines(block, variables, line_offset + block_start)

                i = block_end + 1

            elif line.startswith("repeat "):
                parts = line.split()

                if len(parts) != 2:
                    raise ValueError(f"Invalid repeat syntax: {line}")

                repeat_count = get_value(parts[1], variables)

                block_start = i + 1
                block_end = find_matching_end(lines, block_start)

                block = lines[block_start:block_end]

                for _ in range(repeat_count):
                    execute_lines(block, variables, line_offset + block_start)

                i = block_end + 1

            # fizzbuzz command
            elif line.startswith("fizzbuzz "):
                parts = line.split()

                if len(parts) != 4 or parts[2] != "to":
                    raise ValueError(f"Invalid fizzbuzz syntax: {line}")

                start = int(parts[1])
                end = int(parts[3])

                for number in range(start, end + 1):
                    if number % 15 == 0:
                        print("FizzBuzz")
                    elif number % 3 == 0:
                        print("Fizz")
                    elif number % 5 == 0:
                        print("Buzz")
                    else:
                        print(number)

                i += 1

            elif line.startswith("when "):
                i = execute_when_chain(lines, i, variables, line_offset)

            elif line == "end":
                i += 1

            else:
                raise ValueError(f"Unknown CryptCode command: {line}")

        except ValueError as error:
            if str(error).startswith("Line "):
                raise

            raise ValueError(f"Line {current_line_number}: {error}")
        
# =================================== Help ===================================
        
def print_help() -> None:
    print("CryptCode Interpreter")
    print()
    print("Usage:")
    print("  Run an encrypted program:")
    print("    python3 cryptcode.py program.crypt")
    print()
    print("  Encrypt a .ccode file:")
    print("    python3 cryptcode.py --encrypt input.ccode output.crypt key(s)")
    print()
    print("Examples:")
    print("  python3 cryptcode.py examples/class_demo_hello_world.crypt")
    print("  python3 cryptcode.py --encrypt examples/class_demo_hello_world.ccode examples/class_demo_hello_world.crypt 1")
    print("  python3 cryptcode.py --encrypt examples/class_demo_complex_logic.ccode examples/class_demo_complex_logic.crypt 1 2 3 1 2 3")
    print()
    print("Encryption keys:")
    print("  1 = Caesar encryption")
    print("  2 = Reverse line encryption")
    print("  3 = AddX encryption")
        
# =================================== Command Line Entry Point ===================================

def main() -> None:
    args = sys.argv[1:]

    if not args or args[0] in ["--help", "-h"]:
        print_help()
        sys.exit(0)

    if args[0] == "--encrypt":
        if len(args) < 4:
            raise ValueError("Usage: python3 cryptcode.py --encrypt input.ccode output.crypt key(s)")

        input_path = args[1]
        output_path = args[2]
        keys = args[3:]

        encrypt_file(input_path, output_path, keys)

    else:
        program_path = args[0]
        decrypted_lines = load_and_decrypt_program(program_path)
        execute_lines(decrypted_lines)


if __name__ == "__main__":
    main()