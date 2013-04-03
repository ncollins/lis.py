
from lex import tokenize
from parse import parse_tokens
from evaluate import eval_in_env, Environment


def test_eval_add_const():
    exp = ['+', 3, 4]
    res = eval_in_env(exp, Environment([]))
    assert res == 7


def test_eval_if():
    exp = ['if', True, 3, 4]
    assert eval_in_env(exp, Environment([])) == 3


def test_eval_cond_true():
    exp = ['cond', [['>', 4, 3], 1], ['else', 0]]
    assert eval_in_env(exp, Environment([])) == 1


def test_eval_cond_false():
    exp = ['cond', [['>', 4, 4], 1], ['else', 0]]
    assert eval_in_env(exp, Environment([])) == 0


def test_eval_let():
    exp = ['let', [['x', 3], ['y', 10]], ['+', 'x', 'y']]
    assert eval_in_env(exp, Environment([])) == 13


def test_eval_define():
    env = Environment([])
    exp = ['define', 'a', 3]
    eval_in_env(exp, env)
    #assert env._env == [['a', 3]]
    assert env.lookup('a') == 3


def test_eval_closure():
    env = Environment([['add3', ['closure', ['lambda', ['x'], ['+', 'x', 3]], []]]])
    exp = ['add3', 10]
    assert eval_in_env(exp, env) == 13


def test_eval_closure_2():
    env = Environment([['ifthen', ['closure', ['lambda', ['x'], ['if', True, 'x', 3]], []]]])
    exp = ['ifthen', 10]
    assert eval_in_env(exp, env) == 10


def test_eval_recursion():
    env = Environment([['sumto', ['closure', ['lambda', ['n'],
                                    ['if',  ['<', 'n', 1],
                                            0,
                                            ['+', 'n', ['sumto', ['-', 'n', 1]]]]],
                                 []]]])
    exp = ['sumto', 3]
    assert eval_in_env(exp, env) == 6

def test_eval_recursion_2():
    env = Environment([['factorial', ['closure', ['lambda', ['n'],
                          ['if', ['<', 'n', 1], 1, ['*', 'n', ['factorial', ['-', 'n', 1]]]]], []]]])
    exp = ['factorial', 5]
    assert eval_in_env(exp, env) == 120


def test_eval_anon():
    exp = [['lambda', ['x'], ['+', 'x', 'x']], 7]
    assert eval_in_env(exp, Environment([])) == 14


def test_eval_set():
    env = Environment([['a', 0]])
    exp = ['set!', 'a', 10]
    eval_in_env(exp, env)
    assert env.lookup('a') == 10


def test_eval_begin():
    exp = ['begin', ['define', 'a', 0], ['set!', 'a', 10], 'a']
    assert eval_in_env(exp, Environment([])) == 10


def test_eval_modulo():
    assert 0 == eval_in_env(['modulo', 9, 3], Environment([]))
    assert 1 == eval_in_env(['modulo', 10, 3], Environment([]))
    assert 2 == eval_in_env(['modulo', 11, 3], Environment([]))


def test_eval_not():
    assert True == eval_in_env(['not', False], Environment([]))
    assert False == eval_in_env(['not', True], Environment([]))
    assert False == eval_in_env(['not', 'null'], Environment([]))
