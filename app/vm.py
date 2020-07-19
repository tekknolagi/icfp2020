class Expr:
    evaluated = None


class Value(Expr):
    pass


def Bool(v):
    return stdlib["t"] if v else stdlib["f"]


class Number(Value):
    def __eq__(self, other):
        if isinstance(other, Number):
            assert isinstance(self.value, int)
            assert isinstance(other.value, int)
            return self.value == other.value
        return False

    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value

    def __repr__(self):
        return f"{self.value}"

    def add(self, other):
        assert isinstance(other, Number)
        return Number(self.value + other.value)

    def sub(self, other):
        assert isinstance(other, Number)
        return Number(self.value - other.value)

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
        if isinstance(other, Var):
            return self.name == other.name
        return NotImplemented

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
    assert token != "ap"
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

t = Var("t")
f = Var("f")


def eval1(exp, env):
    if exp.evaluated:
        return exp.evaluated
    if isinstance(exp, Var):
        result = env.get(exp.name)
        if result:
            return result
    if isinstance(exp, Apply):
        fn = eval(exp.fn, env)
        x = exp.arg
        if isinstance(fn, Var):
            # neg = ap sub 0
            # if fn.name == "neg": return eval(x, env).neg()
            # inc = ap add 1
            if fn.name == "inc":
                return eval(x, env).add(Number(1))
            if fn.name == "dec":
                return eval(x, env).sub(Number(1))
            if fn.name == "i":
                return x
            if fn.name == "nil":
                return t
            if fn.name == "isnil":
                return Apply(x, Apply(t, Apply(t, f)))
            if fn.name == "car":
                return Apply(x, t)
            if fn.name == "cdr":
                return Apply(x, f)
        if isinstance(fn, Apply):
            fn2 = eval(fn.fn, env)
            y = fn.arg
            if isinstance(fn2, Var):
                if fn2.name == "t":
                    return y
                if fn2.name == "f":
                    return x
                if fn2.name == "add":
                    return eval(x, env).add(eval(y, env))
                if fn2.name == "sub":
                    return eval(y, env).sub(eval(x, env))
                if fn2.name == "mul":
                    return eval(x, env).mul(eval(y, env))
                if fn2.name == "div":
                    return eval(y, env).div(eval(x, env))
                if fn2.name == "lt":
                    return eval(y, env).lt(eval(x, env))
                if fn2.name == "eq":
                    return t if eval(x, env) == eval(y, env) else f
                if fn2.name == "cons":
                    result = Apply(Apply(cons, eval(y, env)), eval(x, env))
                    result.evaluated = result
                    return result
            if isinstance(fn2, Apply):
                fn3 = eval(fn2.fn, env)
                z = fn2.arg
                if isinstance(fn3, Var):
                    if fn3.name == "s":
                        return Apply(Apply(z, x), Apply(y, x))
                    if fn3.name == "c":
                        return Apply(Apply(z, x), y)
                    if fn3.name == "b":
                        return Apply(z, Apply(y, x))
                    if fn3.name == "cons":
                        return Apply(Apply(x, z), y)
    return exp


stdlib = {"t": t, "f": f}


def eval(exp, env=None):
    if env is None:
        env = stdlib
    if exp.evaluated:
        return exp.evaluated
    initial = exp
    # Eval to fixpoint
    while True:
        result = eval1(exp, env)
        if result == exp:
            initial.evaluted = result
            return result
        exp = result


def evaldef(line, env):
    assert line.count("=") == 1
    name, _, body = line.partition("=")
    tokens = body.split()
    exp = parse(tokens)
    assert len(tokens) == 0
    env[name.strip()] = eval(exp, env)


evaldef("neg = ap sub 0", stdlib)


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
            evaldef(line, env)
            continue
        tokens = line.split()
        ast = parse(tokens)
        if tokens:
            raise RuntimeError("Did not consume all tokens. Remaining:", tokens)
        print(";", ast)
        print(eval(ast, env))
