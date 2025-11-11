import sys
import re

# -------- Lexer ---------
TOKENS = [
    (r'//.*',              None),     # ignore comments
    (r'int',               'INT'),
    (r'if',                'IF'),
    (r'\d+',               'NUMBER'),
    (r'[a-zA-Z_]\w*',      'ID'),
    (r'\+',                'PLUS'),
    (r'-',                 'MINUS'),
    (r'==',                'EQ'),
    (r'=',                 'ASSIGN'),
    (r'\(',                'LPAREN'),   # ✅ added (
    (r'\)',                'RPAREN'),   # ✅ added )
    (r'\{',                'LBRACE'),
    (r'\}',                'RBRACE'),
    (r';',                 'SEMI'),
    (r'\s+',               None)
]

def tokenize(code):
    pos = 0
    while pos < len(code):
        match = None
        for pattern, tag in TOKENS:
            regex = re.compile(pattern)
            match = regex.match(code, pos)
            if match:
                text = match.group(0)
                if tag:
                    yield (tag, text)
                pos = match.end(0)
                break
        if not match:
            raise SyntaxError(f"Unexpected: {code[pos]!r} at {pos}")


# -------- Parser & Assembly Generator ---------
def compile_code(code):
    tokens = list(tokenize(code))
    asm = []
    i = 0

    while i < len(tokens):
        t, v = tokens[i]

        # int a;
        if t == "INT":
            i += 1
            var = tokens[i][1]
            asm.append(f"{var.upper()} DB 0")
            i += 2

        # a = 10;
        elif t == "ID" and i + 1 < len(tokens) and tokens[i+1][0] == "ASSIGN":
            var = v
            i += 2
            val = tokens[i][1]

            if tokens[i][0] == "NUMBER":
                asm.append(f"LD A, {val}")
            else:
                asm.append(f"LD A, [{val.upper()}]")

            asm.append(f"ST [{var.upper()}], A")
            i += 2

        # if (a == b) { a = a + 1; }
        elif t == "IF":
            i += 1
            if tokens[i][0] == "LPAREN":  # skip '('
                i += 1

            left = tokens[i][1]
            i += 2  # skip ID and ==
            right = tokens[i][1]

            i += 1
            if tokens[i][0] == "RPAREN":  # skip ')'
                i += 1

            asm.append(f"LD A, [{left.upper()}]")
            asm.append(f"SUB A, [{right.upper()}]")
            asm.append("JNZ END_IF")

            if tokens[i][0] == "LBRACE":
                i += 1

            var = tokens[i][1]
            i += 2  # skip ID and =
            left2 = tokens[i][1]
            i += 2  # skip ID and +
            num = tokens[i][1]

            asm.append(f"LD A, [{left2.upper()}]")
            asm.append(f"ADD A, {num}")
            asm.append(f"ST [{var.upper()}], A")
            asm.append("END_IF:")

            i += 4

        else:
            i += 1

    return asm


# -------- Main Runner ---------
def main():
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <file.slang>")
        exit()

    with open(sys.argv[1]) as f:
        src = f.read()

    asm = compile_code(src)
    print("\n".join(asm))


if __name__ == "__main__":
    main()
