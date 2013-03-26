#! /usr/bin/env python
import argparse
import operator

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


# KEYWORDS and TYPE CONVERSION =========

def atom(token):
    # try to convert token to int or float
    try:
        return int(token)
    except ValueError:
        try:
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
    raise Exception('unknown variable "{}"'.format(name))

variadic_functions = {'+': sum,
                      '*': lambda li: reduce(operator.mul, li),
                      '-': lambda li: reduce(operator.sub, li),
                      '/': lambda li: reduce(operator.div, li),
                      'list': lambda li: li,
                     }

lazy_functions = {'and': lambda li: all(p for p in li),
                  'or':  lambda li: any(p for p in li),
                 }

special_functions = { 'if': lambda (pred, exp_true, exp_false), env: eval_in_env(
                          exp_true if eval_in_env(pred,env) else exp_false, env)
                    }

binary_functions = {'<': operator.lt,
                    '>': operator.gt,
                    '=': operator.eq,
                    '>=': operator.ge,
                    '<=': operator.le,
                    # todo: extend tests to cover le and ge
                    'cons': lambda x, y: [x] + y,
                    }

unary_functions = {'car': lambda li: li[0],
                   'cdr': lambda li: li[1:],
                   'null?': lambda x: x == [],
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
    if not isinstance(rator, list):
        for funcmap in [variadic_functions, lazy_functions, special_functions,
                         binary_functions, unary_functions ]:
            if rator in funcmap:
                gen_params = (eval_in_env(rand, env) for rand in rands)
                if funcmap == variadic_functions:
                    return funcmap[rator](list(gen_params))
                elif funcmap == lazy_functions:
                    return funcmap[rator](gen_params)
                elif funcmap == special_functions:
                    return funcmap[rator](rands, env)
                elif funcmap == binary_functions:
                    # TODO: make this an exception
                    assert(len(rands) == 2)
                    return funcmap[rator](*gen_params)
                elif funcmap == unary_functions:
                    # TODO: make this an exception
                    assert(len(rands) == 1)
                    return funcmap[rator](*gen_params)

    # CORE LANGUAGE
    if rator == 'let':
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
        func = rator
        closure = eval_in_env(func, env)
        args = rands
        args = [eval_in_env(a, env) for a in args]
        (_, f, closure_env) = closure
        (_, params, body) = f
        if isinstance(func, str):
            new_env = [(func, closure)] + list(zip(params, args)) + closure_env
        else:
            new_env = list(zip(params, args)) + closure_env
        return eval_in_env(body, new_env)


def eval_loop(program):
    env = []
    for exp in program:
        eval_in_env(exp, env)


# REPL =================================

def repl():
    print('****************************************')
    print('lis.py - a simple Lisp written in Python')
    print('(c) Nick Collins, 2013')
    print('****************************************')
    env = []
    while True:
        try:
            user_input = raw_input('lis.py> ')
            exp = parse_tokens(tokenize([user_input]))[0]
            tmp_env = env[:]
            print(eval_in_env(exp, tmp_env))
            env = tmp_env
        except EOFError:
            print('\nLeaving lis.py.')
            break
        except Exception as e:
            print e
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
        except Exception as e:
            print e
            print('Invalid source file')
    else:
        repl()
