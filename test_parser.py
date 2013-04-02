import pytest

from lex import tokenize
from parse import parse_tokens
from errors import LisError, LisSyntaxError, LisNameError

def test_tokenize():
    source0 = ['(define a 3)']
    tokens0 = tokenize(source0)
    source1 = ['(+ 10 25 0)']
    tokens1 = tokenize(source1)
    assert list(tokens0) == ['(', 'define', 'a', '3', ')']
    assert list(tokens1) == ['(', '+', '10', '25', '0', ')']


def test_parse_define():
    source = ['(define a 3)']
    tokens = tokenize(source)
    exp = parse_tokens(tokens)
    assert exp == [['define', 'a', 3]]


def test_parse_add():
    source = ['(define a (+ 3 3))']
    tokens = tokenize(source)
    exp = parse_tokens(tokens)
    assert exp == [['define', 'a', ['+', 3, 3]]]


def test_parse_lambda():
    source = ['(lambda (x y) (+ x y))']
    tokens = tokenize(source)
    exp = parse_tokens(tokens)
    assert exp == [['lambda', ['x', 'y'], ['+', 'x', 'y']]]


def test_parse_define_lambda():
    source = ['(define add (lambda (x y) (+ x y)))']
    tokens = tokenize(source)
    exp = parse_tokens(tokens)
    assert exp == [['define', 'add', ['lambda', ['x', 'y'], ['+', 'x', 'y']]]]


def test_parse_unexpected_closing_paren():
    source = ['(define add 3))']
    tokens = tokenize(source)
    with pytest.raises(LisSyntaxError) as e:
        exp = parse_tokens(tokens)
