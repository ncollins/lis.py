#! /usr/bin/env python
import argparse

try:
    from termcolor import colored
    COLOR = True
except ImportError:
    COLOR = False

from errors import LisError, LisSyntaxError, LisNameError
from lex import tokenize
from parse import parse_tokens
from evaluate import eval_in_env, eval_loop


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
