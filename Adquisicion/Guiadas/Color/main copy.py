"""
This module implements a basic syntax highlighter.
It reads a file and prints in the console the contents of the file 

Returns:
    _type_: _description_
"""
import re
from color_string import color_string


FILE_PATH = "/Users/claudialbombin/Desktop/2025 -2026/Practicas/Adquisicion/Pguiada_color/input.py"

STRING_REGEX = re.compile(r"((\"{3}[\s\S]*?\"{3}|'{3}[\s\S]*?'{3})|(\"[^\"]*\"|'[^']*'))")
COMMENT_REGEX = re.compile(r"#.*\n")
MAGENTA_REGEX = re.compile(
    r"\b(if|while|for|break|continue|pass|from|import|try|except|as|raise|return)\b"
)
BLUE_REGEX = re.compile(r"\b(True|and|not|or|False|def|class)\b")
FUNCTION_CALLS_REGEX = re.compile(r"([ |\n]+)(\w+)(\()")


def parse_file(path, print_result=False):
    """
    Parses an input file and prints it with syntax highlighting in the console
    """
    # type: (str, bool) -> str
    with open(path, "r") as fp:
        content = fp.read()

    rules = [
        {
            "pattern": MAGENTA_REGEX,
            "action": lambda match: color_string(match.group(1), "magenta"),
        },
        {
            "pattern": FUNCTION_CALLS_REGEX,
            "action": lambda match: match.group(1)
            + color_string(match.group(2), "sandy_brown")
            + match.group(3),
        },
        {
            "pattern": BLUE_REGEX,
            "action": lambda match: color_string(match.group(1), "blue"),
        },
        {
            "pattern": STRING_REGEX,
            "action": lambda match: color_string(match.group(0), "red"),
        },
        {
            "pattern": COMMENT_REGEX,
            "action": lambda match: color_string(match.group(0), "green"),
        },
    ]
    parsed = content
    for rule in rules:
        parsed = re.sub(rule["pattern"], rule["action"], parsed)

    if print_result:
        print(parsed)
    return content


if __name__ == "__main__":
    parse_file(FILE_PATH, True)
