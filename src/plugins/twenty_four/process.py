import ast
from collections import Counter
from fractions import Fraction


OPERATORS = {
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
}


def _apply(left: Fraction, right: Fraction, op: str) -> Fraction | None:
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        if right == 0:
            return None
        return left / right
    return None


def _eval_node(node: ast.AST) -> Fraction:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return Fraction(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        result = _apply(left, right, OPERATORS[type(node.op)])
        if result is None:
            raise ZeroDivisionError
        return result
    raise ValueError("invalid expression")


def calc(expr: str) -> Fraction | None:
    try:
        return _eval_node(ast.parse(expr.strip(), mode="eval"))
    except Exception:
        return None


def _extract_numbers(expr: str) -> list[int] | None:
    numbers: list[int] = []
    i = 0
    while i < len(expr):
        char = expr[i]
        if char.isspace():
            i += 1
            continue
        if char.isdigit():
            number = char
            i += 1
            while i < len(expr) and expr[i].isdigit():
                number += expr[i]
                i += 1
            numbers.append(int(number))
            continue
        if char in "+-*/()":
            i += 1
            continue
        return None
    return numbers


def check_valid(expr: str) -> bool:
    numbers = _extract_numbers(expr)
    if numbers is None or len(numbers) > 4:
        return False
    return calc(expr) is not None


def _search_solution(items: list[tuple[Fraction, str]]) -> str | None:
    if len(items) == 1:
        return items[0][1] if items[0][0] == 24 else None

    for left_index, left in enumerate(items):
        for right_index, right in enumerate(items):
            if left_index == right_index:
                continue
            rest = [
                item
                for index, item in enumerate(items)
                if index not in {left_index, right_index}
            ]
            for op in ["+", "-", "*", "/"]:
                value = _apply(left[0], right[0], op)
                if value is None:
                    continue
                expression = f"({left[1]}{op}{right[1]})"
                solution = _search_solution(rest + [(value, expression)])
                if solution is not None:
                    return solution
    return None


async def find_solution(numbers: list[int]) -> str | None:
    return _search_solution([(Fraction(number), str(number)) for number in numbers])


def contains_all_numbers(expr: str, numbers: list[int]) -> bool:
    used_numbers = _extract_numbers(expr)
    if used_numbers is None:
        return False
    return Counter(used_numbers) == Counter(numbers)
