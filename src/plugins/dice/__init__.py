from simpleeval import SimpleEval, FunctionNotDefined, NameNotDefined

from nonebot import on_command
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.adapters import Message

import math
import re

from .dice import *

# 配置常量
MAX_ROLL_TIMES = 10  # 一次命令最多的摇动次数
MAX_DETAIL_CNT = 5  # n次投掷的骰子的总量超过该值时将不再显示详细信息
MAX_ITEM_COUNT = 10  # 骰子表达式最多的项数

dice_patterns = [
    r"(\d+A\d+(?:[KQM]?\d*)?(?:[KQM]?\d*)?(?:[KQM]?\d*)?)",  # WOD骰子
    r"(\d+C\d+M?\d*)",  # 双重十字骰子
    r"(?:D(?:100|%)?)?([BP]\d*)",  # 奖惩骰子
    r"(\d*D?F)",  # 命运骰子
    r"(\d*D\d*%?(?:K\d*|Q\d*)?)",  # 普通骰子
    r"(\d+)",  # 数字
    r"([\(\)])",  # 括号
]

math_funcs = {
    "abs": abs,
    "ceil": math.ceil,
    "comb": math.comb,
    "exp": math.exp,
    "fabs": math.fabs,
    "factorial": math.factorial,
    "fmod": math.fmod,
    "floor": math.floor,
    "gcd": math.gcd,
    "lcm": math.lcm,
    "log": math.log,
    "perm": math.perm,
    "pow": math.pow,
    "sqrt": math.sqrt,
}

se = SimpleEval()
se.functions.update(math_funcs)

dice_ = on_command("rd", aliases={"dice", "掷骰子"}, force_whitespace=True, priority=5)


@dice_.handle()
async def _(args: Message = CommandArg()):
    if args.extract_plain_text() == "":
        return
    part = args.extract_plain_text().split(" ")
    dices = part[0]
    if len(part) < 2:
        dc = None
    else:
        dc = part[1]
    output = await process_expression(dices, dc)
    await dice_.finish(output)


async def process_expression(expr: str, dc):
    dice_list, count, times, err = parse_dice_expression(expr)
    if err:
        return err
    output = generate_dice_message(expr, dice_list, count, times, dc)
    return output


def parse_dice_expression(dices):
    dice_item_list = []
    math_func_pattern = "(" + "|".join(re.escape(func) for func in math_funcs.keys()) + ")"  # 数学函数
    errmsg = None
        
    # 切分骰子表达式
    if "#" in dices:
        times = dices.split("#")[0]
        dices = dices.split("#")[1]
    else:
        times = "1"
    if not times.isdigit():
        return None, None, None, DiceValueError("唔……音卡无法解析骰子表达式：\n无效的投骰次数。").message

    dice_expr_list = re.split(f"{math_func_pattern}|" + "|".join(dice_patterns), dices, flags=re.I)
    dice_expr_list = [item for item in dice_expr_list if item]  # 清除空白元素

    for i, item in enumerate(dice_expr_list):  # 将所有骰子项切片转为大写
        for pattern in dice_patterns:
            match = re.match(pattern, item, flags=re.I)
            if match:
                dice_expr_list[i] = item.upper()
                dice_item_list.append(item)
                break
        # 将所有数学函数切片转为小写
        func_match = re.match(math_func_pattern, item, flags=re.I)
        if func_match:
            dice_expr_list[i] = item.lower()

    logger.debug(dice_expr_list)
    if len(dice_item_list) > MAX_ITEM_COUNT:
        return None, None, None, DiceValueError("唔……音卡无法解析骰子表达式：\n骰子表达式项数超过限制。").message
        
    dice_count = 0
    # 初始化骰子序列
    for j, item in enumerate(dice_expr_list):
        try:
            if any(item.lower() == func for func in math_funcs.keys()):
                continue
            elif "A" in item:
                dice_count += 1
                dice_expr_list[j] = WODDice(item)
            elif "C" in item:
                dice_count += 1
                dice_expr_list[j] = DXDice(item)
            elif "B" in item or "P" in item:
                dice_count += 1
                dice_expr_list[j] = BonusPunishDice(item)
            elif "F" in item:
                dice_count += 1
                dice_expr_list[j] = FudgeDice(item)
            elif "D" in item:
                dice_count += 1
                dice_expr_list[j] = Dice(item)
            elif item.isdigit():
                dice_count += 1
        except (DiceSyntaxError, DiceValueError) as ex:
            errmsg = f"第{dice_count}项发生：" + ex.message
    if errmsg:
        return None, None, None, DiceValueError("唔……音卡无法解析骰子表达式：\n" + errmsg).message
    return dice_expr_list, dice_count, int(times), None

# 在数字与数字之间加上乘号
def insert_multiply(lst):
    result = []
    asterisk = "*"
    for i in range(len(lst)):
        if i == 0:
            result.append(lst[i])
        else:
            if lst[i-1][-1].isdigit() and lst[i][0].isdigit():
                result.append(asterisk)
            elif lst[i-1][-1] == ")" and lst[i][0] == "(":
                result.append(asterisk)
            elif lst[i-1][-1].isdigit() and lst[i][0] == "(":
                result.append(asterisk)
            elif lst[i-1][-1] == ")" and lst[i][0].isdigit():
                result.append(asterisk)
            result.append(lst[i])
    return result

# 开始投掷并生成消息
def generate_dice_message(expr, dice_expr_list, dice_count, times, dc):
    success_num = 0
    fail_num = 0
    output = "你掷得的结果是："
    if "#" in expr:
        expr = expr.split("#")[1]
    if times < 1 or times > MAX_ROLL_TIMES:
        return DiceValueError(f"唔……音卡似乎无法理解该骰子表达式：\n投骰次数不要小于1或大于{MAX_ROLL_TIMES}。").message

    for _ in range(times):
        dice_detail_list = dice_expr_list.copy()
        dice_res_list = dice_expr_list.copy()
        output_line = ""
        for i, item in enumerate(dice_detail_list):
            if isinstance(item, (WODDice, DXDice, BonusPunishDice, Dice, FudgeDice)):  # 检查骰子类型并投掷
                item.Roll()
                res = item.GetResult()
                if times * dice_count < MAX_DETAIL_CNT:
                    dice_detail_list[i] = f"({item.GetDetail()})"
                else:
                    dice_detail_list[i] = f"({str(res)})" if res < 0 else str(res) # type: ignore # 负数加括号
                dice_res_list[i] = f"({str(res)})" if res < 0 else str(res) # type: ignore
            else:
                continue
        dice_detail_list = insert_multiply(dice_detail_list)
        dice_res_list = insert_multiply(dice_res_list)
        output_line += "".join(dice_detail_list)
        logger.debug(dice_detail_list)
        logger.debug(dice_res_list)
        try:
            if dice_res_list:
                dice_res = "".join(dice_res_list)
                dice_res = dice_res.replace("\*", "*") # type: ignore
                logger.debug(dice_res)
                result = int(se.eval(dice_res))
            else:
                raise SyntaxError
        except (FunctionNotDefined, NameNotDefined, SyntaxError, TypeError):
            return DiceSyntaxError("唔……骰子表达式无效！").message
        except Exception as e:
            return DiceValueError("音卡似乎无法理解该骰子表达式：\n" + str(e)).message
        try:
            output_line += '=' + str(result)
        except Exception:
            return DiceValueError("音卡似乎无法理解该骰子表达式：\n太复杂啦，不想算了啦……").message

        try:
            if dc:
                output_line += f"/{dc}  "
                if result <= int(dc):
                    output_line += "成功！"
                    success_num += 1
                else:
                    output_line += "失败！"
                    fail_num += 1
            output += f"\n{expr}={output_line}"
        except ValueError:
            return "无效的DC：" + dc
    if dc and times > 1:
        output += f"\n▷ 判定成功数量：{success_num}  判定失败数量：{fail_num}"

    return output
