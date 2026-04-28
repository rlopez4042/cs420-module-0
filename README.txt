Cryptcode Clean Version
=======================
Cryptcode is a language where programs are stored encrypted.
The first non-empty line must be:

Key: <numbers>

Each number chooses which decryptor to use for one encrypted line.

Supported plain Cryptcode commands
----------------------------------
print <message or variable>
count <var> from <start> to <end>
when <var> mod <number> is <number>
else
end

Run an encrypted program
------------------------
python3 cryptcode.py examples/hello.crypt

On Windows:
python cryptcode.py examples/hello.crypt

Create your own program
-----------------------
1. Make a plain file ending in .ccode:

print Hello
count i from 1 to 3
    print i
end

2. Encrypt it using one algorithm for every line:

python3 cryptcode.py --encrypt examples/my_program.ccode examples/my_program.crypt 1

3. Run it:

python3 cryptcode.py my_program.crypt

Use different algorithms on different lines
------------------------------------------
If your program has 4 non-empty lines, pass 4 keys:

python3 cryptcode.py --encrypt examples/my_program.ccode examples/my_program.crypt 1 2 3 1

Adding your own encryption
--------------------------
Open cryptcode.py and find the ENCRYPTION / DECRYPTION ALGORITHMS section.
Add one encrypt function and one decrypt function.
Then register them in ENCRYPTORS and DECRYPTORS with the same number.

ie 

DECRYPTORS = {
    "1": caesar_decrypt,
    "2": reverse_text,
    "3": remove_x_decrypt,
    "4": <--- Your new decryption
}

ENCRYPTORS = {
    "1": caesar_encrypt,
    "2": reverse_text,
    "3": add_x_encrypt,
    "4": <--- Your new encryption
}

Note:

You can also just write a sample.crypt file manually. As long as you have the proper key designation and write the code with the encryption properly it should work
