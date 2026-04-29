import sys

# ------- Caesar encrypt and decrypt -------

# Decrypt Caesar shift +1 by shifting each letter back by 1.
def caesar_decrypt(text: str) -> str:
    result = ""

    for char in text:
        if "a" <= char <= "z":
            result += chr((ord(char) - ord("a") - 1) % 26 + ord("a"))
        elif "A" <= char <= "Z":
            result += chr((ord(char) - ord("A") - 1) % 26 + ord("A"))
        else:
            result += char
    return result

# Encrypt Caesar shift +1 by shifting each letter forward by 1.
def caesar_encrypt(text: str) -> str:
    result = ""
    for char in text:
        if "a" <= char <= "z":
            result += chr((ord(char) - ord("a") + 1) % 26 + ord("a"))
        elif "A" <= char <= "Z":
            result += chr((ord(char) - ord("A") + 1) % 26 + ord("A"))
        else:
            result += char
    return result

# ------- reverse words, works for encyption and decryption -------

# Reverse text. Same function works for encryption and decryption.
def reverse_text(text: str) -> str:
    return text[::-1]

# ------- x encrypt and decrypt -------

# Decrypt by removing all lowercase x characters.
def remove_x_decrypt(text: str) -> str:
    return text.replace("x", "")

# Encrypt by adding x after every character.
def add_x_encrypt(text: str) -> str:
    result = ""

    for char in text:
        result += char + "x"

    return result


# Add new algorithms here.
# Each number must exist in BOTH dictionaries.
DECRYPTORS = {
    "1": caesar_decrypt,
    "2": reverse_text,
    "3": remove_x_decrypt,
}

ENCRYPTORS = {
    "1": caesar_encrypt,
    "2": reverse_text,
    "3": add_x_encrypt,
}

# ============================================================
# FILE ENCRYPTION
# ============================================================
def encrypt_file(input_path: str, output_path: str, key_numbers: list[str]) -> None:

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

        encrypted_line = ENCRYPTORS[key](line)
        encrypted_lines.append(encrypted_line)
        key_index += 1

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("Key: " + " ".join(keys) + "\n\n")
        for line in encrypted_lines:
            file.write(line + "\n")

    print(f"Encrypted file created: {output_path}")


# ============================================================
# FILE DECRYPTION
# ============================================================
def load_and_decrypt_program(path: str) -> list[str]:

    with open(path, "r", encoding="utf-8") as file:
        all_lines = [line.rstrip("\n") for line in file]

    if not all_lines or not all_lines[0].startswith("Key:"):
        raise ValueError("Cryptcode programs must start with 'Key:'")

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

        decrypted_line = DECRYPTORS[key](line)
        decrypted_lines.append(decrypted_line)
        key_index += 1

    return decrypted_lines


# ============================================================
# INTERPRETER HELPERS
# ============================================================
def find_matching_end(lines: list[str], start_index: int) -> int:
    """
    Find the matching 'end' for a block command like count.

    This lets Cryptcode support:

        count i from 1 to 5
            print i
        end
    """

    depth = 0

    for index in range(start_index, len(lines)):
        line = lines[index].strip()

        if line.startswith("count "):
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


def condition_is_true(line: str, variables: dict[str, int]) -> bool:
    """
    Evaluate simple when conditions.

    Supported examples:
        when i is 3
        when i mod 3 is 0
    """

    parts = line.split()

    if len(parts) == 4 and parts[2] == "is":
        left = get_value(parts[1], variables)
        right = get_value(parts[3], variables)
        return left == right

    if len(parts) == 6 and parts[2] == "mod" and parts[4] == "is":
        left = get_value(parts[1], variables)
        divisor = get_value(parts[3], variables)
        expected = get_value(parts[5], variables)
        return left % divisor == expected

    raise ValueError(f"Invalid when condition: {line}")


def execute_when_chain(lines: list[str], start_index: int, variables: dict[str, int]) -> int:
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

            branches.append((condition, lines[block_start:i]))

        elif line == "else":
            block_start = i + 1
            i += 1

            while i < len(lines) and lines[i].strip() != "end":
                i += 1

            branches.append(("else", lines[block_start:i]))

        elif line == "end":
            break

        else:
            break

    for condition, block in branches:
        if condition == "else" or condition_is_true(condition, variables):
            execute_lines(block, variables)
            break

    return i


# ============================================================
# PROGRAM EXECUTION
# ============================================================
def execute_lines(lines: list[str], variables: dict[str, int] | None = None) -> None:
    """
    Execute decrypted Cryptcode lines.

    Supported commands:
        print Hello
        print i

        count i from 1 to 5
            print i
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
                execute_lines(block, variables)

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
            i = execute_when_chain(lines, i, variables)

        elif line == "end":
            i += 1

        else:
            raise ValueError(f"Unknown Cryptcode command: {line}")

# ============================================================
# MAIN PROGRAM
# ============================================================
def main() -> None:
    args = sys.argv[1:]

    if not args:
        print("Usage:")
        print("  python3 cryptcode.py program.crypt")
        print("  python3 cryptcode.py --encrypt input.ccode output.crypt 1 [2 3 ...]")
        sys.exit(1)

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