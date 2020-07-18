class Expr:
    pass


class Value(Expr):
    pass


class Number(Value):
    def __eq__(self, other):
        assert isinstance(other, Number)
        return self.value == other.value

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"<Number {self.value}>"

    def add(self, other):
        assert isinstance(other, Number)
        return Number(self.value + other.value)


class Function(Value):
    def __init__(self, name, code, nargs, args=()):
        self.name = name
        self.code = code
        self.nargs = nargs
        self.args = args

    def __repr__(self):
        return f"<Function {self.name!r} code={self.code} nargs={self.nargs} args={self.args!r}>"


class Apply(Expr):
    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg


class Var(Expr):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        assert isinstance(other, Var)
        return self.name == other.name


# exp:
#  number
#  :name or name
#  ap exp exp
# statement:
#  :name = exp
#  :1029 = ap ap cons 7 ap ap cons 123229502148636 nil
#  :1155 = ap ap c ap ap b :1153 ap ap c :1152 lt lt


stdlib = {
    "inc": Function("inc", lambda x: x.add(Number(1)), 1),
    "add": Function("add", lambda x, y: x.add(y), 2),
}


def parse_int(token):
    try:
        return int(token)
    except ValueError:
        return None


def parse_name(token):
    if token.isidentifier() or (len(token) > 1 and token.startswith(":")):
        return token
    return None


# ap ap ap add add 1 2 3
# ap(ap, ap add add 1 2 3)
# ap(ap, ap(add, add 1 2 3))
# ap(ap, ap(baz, galaxy 1 2 3))


def parse(tokens):
    token = tokens[0]
    result = parse_int(token)
    if result is not None:
        return Number(result)
    result = parse_name(token)
    if result is not None:
        return Var(result)
    raise SyntaxError("Cannot parse", tokens)


class VM:
    def eval(self, exp, env=None):
        if env is None:
            env = stdlib
        if isinstance(exp, Value):
            # Values are self-evaluating
            return exp
        if isinstance(exp, Var):
            return env[exp.name]
        if isinstance(exp, Apply):
            fn = self.eval(exp.fn, env)
            arg = self.eval(exp.arg, env)
            if fn.nargs == 1:
                return fn.code(*fn.args, arg)
            return Function(fn.name, fn.code, fn.nargs - 1, fn.args + (arg,))
        raise RuntimeError("Unsupported exp")
