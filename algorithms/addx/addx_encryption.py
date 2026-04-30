def addx_encrypt(text: str) -> str:
    result = ""

    for char in text:
        result += char + "x"

    return result