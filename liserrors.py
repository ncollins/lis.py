# Custom Exceptions for lis.py

class LisError(Exception):
    pass


class LisSyntaxError(LisError):
    pass


class LisNameError(LisError):
    pass
