
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
