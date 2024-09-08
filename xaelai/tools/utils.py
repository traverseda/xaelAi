from phi.tools import Toolkit
import subprocess
from sympy import sympify
import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

def shell(command: str) -> str:
    """Run a shell command and return the output or error."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return f"Error: Command returned non-zero exit code {result.returncode}\n{result.stderr}"
        return result.stdout
    except FileNotFoundError:
        return "Error: Command not found"

def math(equation: str, as_float=False) -> str:
    """Evaluate a mathematical expression using sympy. Use as_float to return a float instead of a string.
    for example 1/2 will return 0.5 instead of 1/2.
    """
    if as_float:
        return str(sympify(equation).evalf())
    return str(sympify(equation))

def unit_conversion(from_unit: str, to_unit: str, value: float = 1.0) -> str:
    """Convert a value from one unit to another.
    You MUST fully spell out the unit. For example, Celsius or Columbs instead of "C".
    Meters insted of m, Farads, Fahrenheit, or Feet instead of F, etc.

    You must never use unit abbreviations when calling this tool.
    """
    return str(Q_(value, from_unit.lower()).to(to_unit.lower()))

utils = [shell, math, unit_conversion]
