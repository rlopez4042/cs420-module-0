# CryptCode
_Built for a CS 420 class project._

CryptCode is an interpreted programming language where programs are stored in an encrypted format.

A plain source file uses the `.ccode` extension.  
An encrypted executable file uses the `.crypt` extension.

Every encrypted `.crypt` file must start with:

```text
Key: <numbers>
```

Each number chooses which decryptor to use for one encrypted non-empty line.

## Current algorithm keys

```text
1 = Caesar
2 = Reverse
3 = AddX
```

CryptCode also uses public and private key files for the Caesar algorithm:

```text
keys/public.key
keys/private.key
```

The public key is used during encryption.  
The private key is used during decryption.

For Caesar, the public and private keys must be different numbers that add up to `26`.

Example:

```text
public.key:
3

private.key:
23
```

This means encryption shifts letters forward by `3`, and decryption shifts letters forward by `23` to wrap back to the original text.

## Supported plain CryptCode commands

```text
print <message or variable>

set <variable> to <number or expression>

count <var> from <start> to <end>
    <commands>
end

repeat <number>
    <commands>
end

when <var> is <number>
    <commands>
else
    <commands>
end

when <var> is not <number>
    <commands>
else
    <commands>
end

when <var> greater <number>
    <commands>
else
    <commands>
end

when <var> less <number>
    <commands>
else
    <commands>
end

when <var> mod <number> is <number>
    <commands>
else
    <commands>
end

fizzbuzz <start> to <end>
```

## Supported operators

```text
+     addition
-     subtraction
*     multiplication
/     integer division
mod   remainder
```

Important: expressions need spaces between values and operators.

Works:

```text
set total to total + i
```

Does not work:

```text
set total to total+i
```

## Run an encrypted program

```bash
python3 cryptcode.py examples/hello.crypt
```

On Windows:

```bash
python cryptcode.py examples/hello.crypt
```

## Create your own program

1. Make a plain file ending in `.ccode`:

```text
print Hello
count i from 1 to 3
    print i
end
```

2. Make sure the key files exist:

```bash
mkdir -p keys
echo 3 > keys/public.key
echo 23 > keys/private.key
```

3. Encrypt it using one algorithm for every line:

```bash
python3 cryptcode.py --encrypt examples/my_program.ccode examples/my_program.crypt 1
```

4. Run it:

```bash
python3 cryptcode.py examples/my_program.crypt
```

## Use different algorithms on different lines

If your program has 4 non-empty lines, pass 4 keys:

```bash
python3 cryptcode.py --encrypt examples/my_program.ccode examples/my_program.crypt 1 2 3 1
```

The key count must match the number of non-empty lines in the program.

## Example programs

Encrypt and run hello world with Caesar:

```bash
python3 cryptcode.py --encrypt examples/hello.ccode examples/hello.crypt 1
python3 cryptcode.py examples/hello.crypt
```

Encrypt and run hello world with Reverse:

```bash
python3 cryptcode.py --encrypt examples/hello.ccode examples/hello_reverse.crypt 2
python3 cryptcode.py examples/hello_reverse.crypt
```

Encrypt and run hello world with AddX:

```bash
python3 cryptcode.py --encrypt examples/hello.ccode examples/hello_addx.crypt 3
python3 cryptcode.py examples/hello_addx.crypt
```

## Test public/private key behavior

This should work:

```bash
echo 3 > keys/public.key
echo 23 > keys/private.key
python3 cryptcode.py --encrypt examples/hello.ccode examples/hello.crypt 1
python3 cryptcode.py examples/hello.crypt
```

This should fail or decrypt incorrectly because the keys do not match:

```bash
echo 3 > keys/public.key
echo 1 > keys/private.key
python3 cryptcode.py examples/hello.crypt
```

## Adding your own encryption

Each algorithm lives in the `algorithms` folder.

To add a new algorithm:

1. Create a new folder inside `algorithms`.
2. Add one encryption file.
3. Add one decryption file.
4. Import both functions in `cryptcode.py`.
5. Register both functions in `ENCRYPTORS` and `DECRYPTORS` with the same number.

Example:

```python
ENCRYPTORS = {
    "1": caesar_encrypt,
    "2": reverse_encrypt,
    "3": addx_encrypt,
    "4": your_new_encrypt,
}

DECRYPTORS = {
    "1": caesar_decrypt,
    "2": reverse_decrypt,
    "3": addx_decrypt,
    "4": your_new_decrypt,
}
```

Note: you can also write a `.crypt` file manually. As long as the `Key:` line matches the encryption used on each non-empty line, the interpreter can decrypt and run it.

## Web demo

Also made a small web demo for this project:

https://rlopez4042.github.io/cryptcode-web/
