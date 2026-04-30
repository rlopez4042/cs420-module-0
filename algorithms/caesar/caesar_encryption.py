def caesar_encrypt(text: str, shift: int = 1) -> str:
    result = ""

    for char in text:
        if "a" <= char <= "z":
            result += chr((ord(char) - ord("a") + shift) % 26 + ord("a"))
        elif "A" <= char <= "Z":
            result += chr((ord(char) - ord("A") + shift) % 26 + ord("A"))
        else:
            result += char

    return result