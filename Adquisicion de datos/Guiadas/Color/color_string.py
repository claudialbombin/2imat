from colored import Fore, Style

color_mapping = {
    "magenta": Fore.magenta,
    "blue": Fore.blue,
    "red": Fore.red,
    "green": Fore.green,
    "navy_blue": Fore.navy_blue,
    "light_blue": Fore.light_blue,
    "sandy_brown": Fore.sandy_brown,
}


def color_string(string: str, color: str, print_string: bool = False) -> str:
    """
     Returns the input string colored with the input color
     Args:
     string (str): string to be colored
     color (str): color to be applied
     print_string (bool, optional): Set to True if you want the string to be
    printed. Defaults to False.
     Returns:
     str: the input string formatted with the right color
    """
    formatted_string = f"{color_mapping[color]}{string}{Style.reset}"
    if print_string:
        print(formatted_string)
    return formatted_string


if __name__ == "__main__":
    color_string("Hello world!", "red", True)
    color_string("Hello world!", "magenta", True)
    color_string("Hello world!", "blue", True)
