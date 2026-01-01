# utils.py
import re
from datetime import datetime, timedelta

def interpolate_text(text, variables):
    if not text or not isinstance(text, str):
        return text or ""
    def repl(match):
        var_name = match.group(1)
        return str(variables.get(var_name, ""))
    return re.sub(r'\$\{(\w+)\}', repl, text)

def evaluate_expression(expr, variables):
    try:
        safe_expr = str(expr)
        for var, val in variables.items():
            if isinstance(val, (int, float)):
                safe_expr = safe_expr.replace(var, str(val))
        return eval(safe_expr, {"__builtins__": {}})
    except Exception:
        return 0.0

def parse_wait_time(time_str):
    """Returns target datetime"""
    if time_str.startswith('+'):
        delta = timedelta()
        matches = re.findall(r'(\d+)([dhms])', time_str[1:])
        for num, unit in matches:
            n = int(num)
            if unit == 'd': delta += timedelta(days=n)
            elif unit == 'h': delta += timedelta(hours=n)
            elif unit == 'm': delta += timedelta(minutes=n)
            elif unit == 's': delta += timedelta(seconds=n)
        return datetime.now() + delta
    else:
        return datetime.strptime(time_str.strip(), "%Y-%m-%d %H:%M:%S")