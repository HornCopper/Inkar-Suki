import itertools

from simpleeval import simple_eval

def calc(expr):
    try:
        return simple_eval(expr)
    except Exception:
        return None


def check_valid(expr):
    operators = ["+", "-", "*", "/"]
    other_symbols = ["(", ")"]
    valid_chars_set = set(operators + other_symbols)

    i = 0
    num_numbers = 0
    while i < len(expr):
        char = expr[i]
        if char.isdigit():
            while i < len(expr) and expr[i].isdigit():
                i += 1
            num_numbers += 1
        elif char in valid_chars_set:
            if char in operators and i + 1 < len(expr) and expr[i + 1] in operators:
                return False
            i += 1
        else:
            return False
    if num_numbers > 9:
        return False
    return True


async def find_solution(numbers):
    perms = list(itertools.permutations(numbers))
    operators = ["+", "-", "*", "/"]
    exprs = list(itertools.product(operators, repeat=4))

    for perm in perms:
        for expr in exprs:  # 穷举就完事了
            exp = "(({}{}{}){}{}){}{}".format(perm[0], expr[0], perm[1], expr[1], perm[2], expr[2], perm[3])
            try:
                if (calc(exp) == 24 or 0 < 24 - calc(exp) < 1e-13): # type: ignore
                    return exp
            except:
                pass
            exp = "({}{}{}){}({}{}{})".format(perm[0], expr[0], perm[1], expr[1], perm[2], expr[2], perm[3])
            try:
                if (calc(exp) == 24 or 0 < 24 - calc(exp) < 1e-13): # type: ignore
                    return exp
            except:
                pass
            exp = "{}{}({}{}({}{}{}))".format(perm[0], expr[0], perm[1], expr[1], perm[2], expr[2], perm[3])
            try:
                if (calc(exp) == 24 or 0 < 24 - calc(exp) < 1e-13): # type: ignore
                    return exp
            except:
                pass
            exp = "{}{}({}{}{}){}{}".format(perm[0], expr[0], perm[1], expr[1], perm[2], expr[2], perm[3])
            try:
                if (calc(exp) == 24 or 0 < 24 - calc(exp) < 1e-13): # type: ignore
                    return exp
            except:
                pass
    return None


def contains_all_numbers(expr, numbers):
    used_numbers = [str(num) for num in numbers]
    used_count = {str(num): 0 for num in numbers}
    i = 0
    while i < len(expr):
        char = expr[i]
        if isint(char): # type: ignore
            number = char
            while i + 1 < len(expr) and isint(expr[i + 1]): # type: ignore
                number += expr[i + 1]
                i += 1
            if number in used_numbers:
                used_count[number] += 1
                if used_count[number] > numbers.count(int(number)):
                    return False
            else:
                return False
        i += 1
    return True

