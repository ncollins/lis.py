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
    """
    This wraps the standard Python print() function.
    It uses colored output if the import of termcolor succeeded.
    Parameters:
        string - the string to be printed. 
        color - a string representing a color, e.g. 'white', 'red', 'blue'.
    """
    if COLOR:
        print(colored(string, color))
    else:
        print(string)

# LEXER ================================

def split_word(word):
    """
    Takes a block of text with no whitespace and returns a generator
    yielding the individual tokens. e.g. '(function)' would yield:
        '(', 'fuction', ')'
    """
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
    """
    Takes an iterable of strings, for example the lines from a file,
    and returns a generator yielding the individual tokens.
    """
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
    """
    Takes a single token and tries in order:
        (1) to convert to an int or float,
        (2) to convert '#t' or '#f' into a boolean,
    and returns the string if none of the above succeed.
    """
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

def parse_tokens(tokens, parens=0):
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
            lst, parens = parse_tokens(tokens, parens+1)
            out.append(lst)
        elif parens == 0 and t == ')':
            raise LisSyntaxError('Unexpected ")"')
        elif t == ')':
            return (out, parens - 1)
        else:
            out.append(atom(t))
    return out



# EVALUATOR ============================

def lookup(name, env):
    for n, v in env:
        if n == name:
            return v
    raise LisNameError('Unknown variable "{}"'.format(name))


def set_var(name, env, val):
    for i, (n, _) in enumerate(env):
        if n == name:
            env[i][1] = val
            return
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
    if exp == 'else':
        return True
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
    if rator == 'cond':
        for pred, exp in rands:
            if eval_in_env(pred, env):
                return eval_in_env(exp, env)
        raise LisSyntaxError('cond statement without else branch')
    elif rator == 'let':
        (_, pairs, e) = exp
        new_env = env
        for p in pairs:
            name, val = p[0], p[1]
            new_env = [[name, eval_in_env(val, env)]] + new_env
        return eval_in_env(e, new_env)
    elif rator == 'define':
        # just a simple mofification of the current env
        (_, name, e) = exp
        env.insert(0, [name, eval_in_env(e, env)])
    elif rator == 'lambda':
        # needs to return a closure
        return ['closure', exp, list(env)] # ensure the env won't be mutated
    elif rator == 'set!':
        (_, name, e) = exp
        set_var(name, env, eval_in_env(e, env))
    elif rator == 'begin':
        out = None
        for e in rands:
            out = eval_in_env(e, env)
        return out
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
        except LisSyntaxError as e:
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
