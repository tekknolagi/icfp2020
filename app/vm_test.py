from vm import Apply, Bool, Number, Var, eval, parse, stdlib


def test_number_add_returns_sum():
    assert Number(5).add(Number(6)) == Number(11)


def test_eval_with_positive_number_returns_number():
    program = Number(5)
    assert eval(program) == program


def test_eval_with_negative_number_returns_number():
    program = Number(-5)
    assert eval(program) == program


def test_eval_with_var_looks_up_value():
    assert eval(Var("x"), {"x": Number(5)}) == Number(5)


def test_inc_with_number_returns_next_number():
    assert eval(Apply(stdlib["inc"], Number(5))) == Number(6)


def test_add_with_two_numbers_returns_result():
    # ap (ap add 5) 6
    assert eval(Apply(Apply(stdlib["add"], Number(5)), Number(6))) == Number(11)


def test_parse_number_returns_number():
    assert parse(["-123"]) == Number(-123)
    assert parse(["123"]) == Number(123)


def test_parse_id_returns_id():
    assert parse(["a"]) == Var("a")


def test_parse_app():
    exp = parse(["ap", "ap", "add", "1", "2"])
    assert eval(exp) == Number(3)


def test_parse_app2():
    # From the video
    exp = parse("ap dec ap ap add 1 2".split())
    assert eval(exp) == Number(2)


def test_mul_with_two_numbers_returns_result():
    assert eval(parse("ap ap mul 3 4".split())) == Number(12)


def test_div_with_two_numbers_returns_result():
    assert eval(parse("ap ap div 12 4".split())) == Number(3)


def test_div_returns_integer():
    assert eval(parse("ap ap div 10 4".split())) == Number(2)


def test_true_returns_bool():
    assert eval(parse("t".split())) == Bool(True)


def test_false_returns_bool():
    assert eval(parse("f".split())) == Bool(False)


def test_eq_with_numbers():
    assert eval(parse("ap ap eq 1 1".split())) == Bool(True)
    assert eval(parse("ap ap eq 1 2".split())) == Bool(False)


def test_eq_with_bool():
    assert eval(parse("ap ap eq t t".split())) == Bool(True)
    assert eval(parse("ap ap eq t f".split())) == Bool(False)


def test_lt_with_equal_numbers_returns_false():
    assert eval(parse("ap ap lt 1 1".split())) == Bool(False)


def test_lt_with_lhs_less_than_rhs_returns_true():
    assert eval(parse("ap ap lt 1 2".split())) == Bool(True)


def test_lt_with_lhs_greater_than_rhs_returns_false():
    assert eval(parse("ap ap lt 2 1".split())) == Bool(False)


def test_neg_with_positive_returns_negative():
    assert eval(parse("ap neg 5".split())) == Number(-5)


def test_neg_with_negative_returns_positive():
    assert eval(parse("ap neg -5".split())) == Number(5)


def test_s_combinator():
    assert eval(parse("ap ap ap s add inc 1".split())) == Number(3)
    assert eval(parse("ap ap ap s mul ap add 1 6".split())) == Number(42)


def test_c_combinator():
    assert eval(parse("ap ap ap c add 1 2".split())) == Number(3)
