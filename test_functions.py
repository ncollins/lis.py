
from lis import tokenize, parse_tokens, eval_in_env

def test_add():
    source = ['(+ 1 3 5)']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == 9


def test_multiply():
    source = ['(* 1 3 5)']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == 15


def test_subtract():
    source = ['(- 10 14)']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == -4


def test_divide():
    source = ['(/ 10 3)']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == 3


def test_equals():
    source0, source1 = ['(= 1 2)'], ['(= 2 2)']
    exp0 = parse_tokens(tokenize(source0))[0]
    exp1 = parse_tokens(tokenize(source1))[0]
    assert eval_in_env(exp0, []) == False
    assert eval_in_env(exp1, []) == True


def test_lt():
    source0, source1 = ['(< 2 2)'], ['(< 1 2)']
    exp0 = parse_tokens(tokenize(source0))[0]
    exp1 = parse_tokens(tokenize(source1))[0]
    assert eval_in_env(exp0, []) == False
    assert eval_in_env(exp1, []) == True


def test_gt():
    source0, source1 = ['(> 2 2)'], ['(> 3 2)']
    exp0 = parse_tokens(tokenize(source0))[0]
    exp1 = parse_tokens(tokenize(source1))[0]
    assert eval_in_env(exp0, []) == False
    assert eval_in_env(exp1, []) == True


def test_and_true():
    source = ['(and (> 2 1) (= 1 1) #t)']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == True


def test_and_false():
    source = ['(and (> 2 1) (= 1 2) #t)']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == False

def test_and_shortcircuit():
    source = ['(and #f never-reached)']
    exp = parse_tokens(tokenize(source))[0]
    try:
        eval_in_env(exp, [])
    except Exception as e:
        assert str(e) != 'unknown variable "never-reached"'

def test_or_true():
    source = ['(or (> 2 10) (= 1 1) #f)']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == True


def test_or_false():
    source = ['(or (> 2 10) (= 1 2) #f)']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == False

def test_or_shortcircuit():
    source = ['(or #t never-reached)']
    exp = parse_tokens(tokenize(source))[0]
    try:
        eval_in_env(exp, [])
    except Exception as e:
        assert str(e) != 'unknown variable "never-reached"'
