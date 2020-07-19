class Expr:
    pass


class Value(Expr):
    pass


def Bool(v):
    return stdlib["t"] if v else stdlib["f"]


class Number(Value):
    def __eq__(self, other):
        assert isinstance(other, Number)
        return self.value == other.value

    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value

    def __repr__(self):
        return f"{self.value}"

    def add(self, other):
        assert isinstance(other, Number)
        return Number(self.value + other.value)

    def lt(self, other):
        assert isinstance(other, Number)
        return Bool(self.value < other.value)

    def mul(self, other):
        assert isinstance(other, Number)
        return Number(self.value * other.value)

    def neg(self):
        return Number(-self.value)

    def div(self, other):
        assert isinstance(other, Number)
        return Number(self.value // other.value)


class Function(Value):
    def __init__(self, name, code, nargs, args=()):
        self.name = name
        self.code = code
        self.nargs = nargs
        self.args = args

    def __repr__(self):
        return f"<Function {self.name!r} nargs={self.nargs} args={self.args!r}>"


class Apply(Expr):
    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg

    def __repr__(self):
        return f"({self.fn} {self.arg})"


class Var(Expr):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        assert isinstance(other, Var)
        return self.name == other.name

    def __repr__(self):
        return self.name


def parse_int(token):
    try:
        return int(token)
    except ValueError:
        return None


def parse_name(token):
    if token.isidentifier() or (len(token) > 1 and token.startswith(":")):
        return token
    return None


def parse_atom(tokens):
    if not tokens:
        return None
    token = tokens[0]
    if token == "ap":
        return None
    result = parse_int(token)
    if result is not None:
        tokens.pop(0)
        return Number(result)
    result = parse_name(token)
    if result is not None:
        tokens.pop(0)
        return Var(result)


def parse(tokens):
    if tokens and tokens[0] == "ap":
        tokens.pop(0)
        lhs = parse(tokens)
        rhs = parse(tokens)
        return Apply(lhs, rhs)
    return parse_atom(tokens)


# It's a little gross to call back into eval from a combinator, but that might
# be the right thing to do here.


stdlib = {
    "add": Function("add", lambda x, y: x.add(y), 2),
    "dec": Function("dec", lambda x: x.add(Number(-1)), 1),
    "div": Function("div", lambda x, y: x.div(y), 2),
    "eq": Function("eq", lambda x, y: Bool(x == y), 2),
    "lt": Function("lt", lambda x, y: x.lt(y), 2),
    "inc": Function("inc", lambda x: x.add(Number(1)), 1),
    "mul": Function("mul", lambda x, y: x.mul(y), 2),
    "neg": Function("neg", lambda x: x.neg(), 1),
    "c": Function("c", lambda x, y, z: eval(Apply(Apply(x, z), y)), 3),
    "s": Function("s", lambda x, y, z: eval(Apply(Apply(x, z), Apply(y, z))), 3),
    "b": Function("b", lambda x, y, z: eval(Apply(x, Apply(y, z))), 3),
    "t": Function("t", lambda x, y: x, 2),
    "f": Function("f", lambda x, y: y, 2),
}


def eval(exp, env=None):
    if env is None:
        env = stdlib
    if isinstance(exp, Value):
        # Values are self-evaluating
        return exp
    if isinstance(exp, Var):
        return env[exp.name]
    if isinstance(exp, Apply):
        fn = eval(exp.fn, env)
        arg = eval(exp.arg, env)
        if fn.nargs == 1:
            return fn.code(*fn.args, arg)
        return Function(fn.name, fn.code, fn.nargs - 1, fn.args + (arg,))
    raise RuntimeError("Unsupported exp")


# TODO: Support recursive functions
def evaldef(name, exp, env):
    env[name] = eval(exp, env)


def show_parse(s):
    print(s)
    ls = s.split()
    print(parse(ls))
    # Must have consumed every token
    assert len(ls) == 0


if __name__ == "__main__":
    env = stdlib.copy()
    while True:
        try:
            line = input("> ")
        except EOFError:
            print("Quit.")
            break
        if "=" in line:
            assert line.count("=") == 1
            name, _, body = line.partition("=")
            evaldef(name.strip(), parse(body.split()), env)
            continue
        tokens = line.split()
        ast = parse(tokens)
        if tokens:
            raise RuntimeError("Did not consume all tokens. Remaining:", tokens)
        print(";", ast)
        print(eval(ast, env))
