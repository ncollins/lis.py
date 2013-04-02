
from lexer import tokenize
from lisparser import parse_tokens
from lis import eval_in_env

def test_cons():
    source = ['(cons (+ 1 3 5) null)']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == [9]


def test_cons_2():
    source = ['(cons (+ 1 3 5) (cons (+ 1 3 5) null))']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == [9, 9]


def test_car():
    source = ['(car (cons 1 null))']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == 1


def test_cdr():
    source = ['(cdr (cons 1 null))']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == []


def test_list():
    source = ['(list 1 2 (+ 1 2) 4)']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == [1, 2, 3, 4]


def test_nullcheck():
    source = ['(null? null)']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == True


def test_nullcheck_2():
    source = ['(null? (cons 1 null))']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == False


def test_nullcheck_3():
    source = ['(null? (cdr (list 1)))']
    exp = parse_tokens(tokenize(source))[0]
    assert eval_in_env(exp, []) == True
