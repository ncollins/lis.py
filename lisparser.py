
from liserrors import LisSyntaxError

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

