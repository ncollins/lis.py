import sys
import operator

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
        sys.stdout.write(str(eval_in_env(exp[1], env)))
    elif rator == 'write-line':
        print(eval_in_env(exp[1], env))
    elif rator == 'read-line':
        return raw_input()

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
