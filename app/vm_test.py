from vm import VM, Apply, Number, Var, parse, stdlib


def test_number_add_returns_sum():
    assert Number(5).add(Number(6)) == Number(11)


def test_eval_with_positive_number_returns_number():
    vm = VM()
    program = Number(5)
    assert vm.eval(program) == program


def test_eval_with_negative_number_returns_number():
    vm = VM()
    program = Number(-5)
    assert vm.eval(program) == program


def test_eval_with_var_looks_up_value():
    vm = VM()
    assert vm.eval(Var("x"), {"x": Number(5)}) == Number(5)


def test_inc_with_number_returns_next_number():
    vm = VM()
    assert vm.eval(Apply(stdlib["inc"], Number(5))) == Number(6)


def test_add_with_two_numbers_returns_result():
    vm = VM()
    # ap (ap add 5) 6
    assert vm.eval(Apply(Apply(stdlib["add"], Number(5)), Number(6))) == Number(11)


def test_parse_number_returns_number():
    assert parse(["-123"]) == Number(-123)
    assert parse(["123"]) == Number(123)


def test_parse_id_returns_id():
    assert parse(["a"]) == Var("a")


def test_parse_app():
    exp = parse(["ap", "ap", "add", "1", "2"])
    vm = VM()
    assert vm.eval(exp) == Number(3)


def test_parse_app2():
    # From the video
    exp = parse("ap dec ap ap add 1 2".split())
    vm = VM()
    assert vm.eval(exp) == Number(2)


def test_mul_with_two_numbers_returns_result():
    vm = VM()
    assert vm.eval(parse("ap ap mul 3 4".split())) == Number(12)


def test_div_with_two_numbers_returns_result():
    vm = VM()
    assert vm.eval(parse("ap ap div 12 4".split())) == Number(3)


def test_div_returns_integer():
    vm = VM()
    assert vm.eval(parse("ap ap div 10 4".split())) == Number(2)
