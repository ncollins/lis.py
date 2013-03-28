#! /usr/bin/env python
import argparse
import operator
try:
    from termcolor import colored
    COLOR = True
except ImportError:
    COLOR = False


# COLOR PRINTING =======================

def color_print(string, color='white'):
    if COLOR:
        print(colored(string, color))
    else:
        print(string)

# LEXER ================================

def split_word(word):
    current = ''
    for c in word:
        if c == '(' or c == ')':
            if current != '':
                yield current
            yield c
            current = ''
        else:
            current = current + c
    if current != '':
        yield current

def tokenize(lines):
    for line in lines:
        for word in line.split():
            for s in split_word(word):
                yield s

# ERRORS ===============================

class LisError(Exception):
    pass


class LisSyntaxError(LisError):
    pass


class LisNameError(LisError):
    pass


# KEYWORDS and TYPE CONVERSION =========

def atom(token):
    # try to convert token to int or float
    try:
        return int(token)
        return float(token)
    except ValueError:
        if token == '#t':
            return True
        elif token == '#f':
            return False
        else:
            return token


# PARSER ===============================

def parse_tokens(tokens):
    """
    Parsing function: this relies on tokens being a generator
    so that each token is only seen once.
    ---------
    Arguments:
        tokens - a generator of tokens
    Output:
        A list of lists representing the syntax tree.
    """
    out = []
    for t in tokens:
        if t == '(':
            out.append(parse_tokens(tokens))
        elif out == [] and t == ')':
            raise Exception('Unexpected ")"')
        elif t == ')':
            return out
        else:
            out.append(atom(t))
    return out



# EVALUATOR ============================

def lookup(name, env):
    for n, v in env:
        if n == name:
            return v
    raise LisNameError('Unknown variable "{}"'.format(name))

function_map = {
                      # variadic functions
                      '+': sum,
                      '*': lambda gen: reduce(operator.mul, gen),
                      '-': lambda gen: reduce(operator.sub, gen),
                      '/': lambda gen: reduce(operator.div, gen),
                      'list': lambda gen: list(gen),

                      # short-circuiting functions
                      'and': lambda gen: all(p for p in gen),
                      'or':  lambda gen: any(p for p in gen),

                      # binary functions
                      'cons': lambda (x, y): [x] + y,
                      '<': lambda (x, y): operator.lt(x, y),
                      '>': lambda (x, y): operator.gt(x, y),
                      '=': lambda (x, y): operator.eq(x, y),
                      '>=': lambda (x, y): operator.ge(x, y),
                      '<=': lambda (x, y): operator.le(x, y),

                      # unary functions
                      'car': lambda (li,): li[0],
                      'cdr': lambda (li,): li[1:],
                      'null?': lambda (li,): li == [],
                    }

def eval_in_env(exp, env):
    if exp == 'null':
        return []
    elif isinstance(exp, str):
        return lookup(exp, env)
    if not isinstance(exp, list):
        return exp
    # FUNCTIONS
    rator, rands = exp[0], exp[1:]
    if not isinstance(rator, list) and rator in function_map:
        gen_params = (eval_in_env(rand, env) for rand in rands)
        return function_map[rator](gen_params)

    # CORE LANGUAGE
    if rator == 'if':
        (pred, expr_true, expr_false) = rands
        if eval_in_env(pred, env):
            return eval_in_env(expr_true, env)
        else:
            return eval_in_env(expr_false, env)
    elif rator == 'let':
        (_, pairs, e) = exp
        new_env = env
        for p in pairs:
            name, val = p[0], p[1]
            new_env = [(name, eval_in_env(val, env))] + new_env
        return eval_in_env(e, new_env)
    elif rator == 'define':
        # just a simple mofification of the current env
        (_, name, e) = exp
        env.insert(0, (name, eval_in_env(e, env)))
    elif rator == 'lambda':
        # needs to return a closure
        #(_, params, body) = exp
        return ['closure', exp, list(env)] # ensure the env won't be mutated
    elif rator == 'display':
        print(eval_in_env(exp[1], env))
    # FUNCTION EVALUATION
    else:
        # first element should be a variable pointing to a function
        # or a lambda expression
        closure = eval_in_env(rator, env)
        rands = [eval_in_env(a, env) for a in rands]
        (_, f, closure_env) = closure
        (_, params, body) = f
        if isinstance(rator, str):
            new_env = [(rator, closure)] + list(zip(params, rands)) + closure_env
        else:
            new_env = list(zip(params, rands)) + closure_env
        return eval_in_env(body, new_env)


def eval_loop(program):
    env = []
    for exp in program:
        eval_in_env(exp, env)


# REPL =================================

def repl():
    color_print('****************************************', 'blue')
    color_print('lis.py - a simple Lisp written in Python', 'blue')
    color_print('(c) Nick Collins, 2013', 'blue')
    color_print('****************************************', 'blue')
    env = []
    while True:
        try:
            user_input = raw_input('lis.py> ')
            exp = parse_tokens(tokenize([user_input]))[0]
            tmp_env = env[:]
            color_print(eval_in_env(exp, tmp_env), 'green')
            env = tmp_env
        except EOFError:
            color_print('\nLeaving lis.py.', 'blue')
            break
        except LisNameError as e:
            color_print(e, 'red')
        except Exception as e:
            color_print(e, 'red')
            print('*** Invalid input ***')

# RUN INTERPRETER ======================

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source', nargs = '?', default=None, help='source file')
    args = parser.parse_args()

    if args.source:
        try:
            with open(args.source, 'r') as source:
                tokens = tokenize(source)
                program = parse_tokens(tokens)
            eval_loop(program)
        except IOError as e:
            color_print(e, 'red')
            color_print('Invalid source file', 'red')
    else:
        repl()
