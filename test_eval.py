
from lis import tokenize, parse_tokens, eval_in_env, lookup


def test_eval_add_const():
    exp = ['+', 3, 4]
    res = eval_in_env(exp, [])
    assert res == 7


def test_eval_if():
    exp = ['if', True, 3, 4]
    assert eval_in_env(exp, []) == 3


def test_eval_cond_true():
    exp = ['cond', [['>', 4, 3], 1], ['else', 0]]
    assert eval_in_env(exp, []) == 1


def test_eval_cond_false():
    exp = ['cond', [['>', 4, 4], 1], ['else', 0]]
    assert eval_in_env(exp, []) == 0


def test_eval_let():
    exp = ['let', [['x', 3], ['y', 10]], ['+', 'x', 'y']]
    assert eval_in_env(exp, []) == 13


def test_eval_define():
    env = []
    exp = ['define', 'a', 3]
    eval_in_env(exp, env)
    assert env == [['a', 3]]


def test_eval_closure():
    env = [('add3', ['closure', ['lambda', ['x'], ['+', 'x', 3]], []])]
    exp = ['add3', 10]
    assert eval_in_env(exp, env) == 13


def test_eval_closure_2():
    env = [('ifthen', ['closure', ['lambda', ['x'], ['if', True, 'x', 3]], []])]
    exp = ['ifthen', 10]
    assert eval_in_env(exp, env) == 10


def test_eval_recursion():
    env = [('sumto', ['closure', ['lambda', ['n'],
                                    ['if',  ['<', 'n', 1],
                                            0,
                                            ['+', 'n', ['sumto', ['-', 'n', 1]]]]],
                                 []])]
    exp = ['sumto', 3]
    assert eval_in_env(exp, env) == 6

def test_eval_recursion_2():
    env = [('factorial', ['closure', ['lambda', ['n'],
                          ['if', ['<', 'n', 1], 1, ['*', 'n', ['factorial', ['-', 'n', 1]]]]], []])]
    exp = ['factorial', 5]
    assert eval_in_env(exp, env) == 120


def test_eval_anon():
    exp = [['lambda', ['x'], ['+', 'x', 'x']], 7]
    assert eval_in_env(exp, []) == 14


def test_eval_set():
    env = [['a', 0]]
    exp = ['set!', 'a', 10]
    eval_in_env(exp, env)
    assert lookup('a', env) == 10


def test_eval_begin():
    exp = ['begin', ['define', 'a', 0], ['set!', 'a', 10], 'a']
    assert eval_in_env(exp, []) == 10
