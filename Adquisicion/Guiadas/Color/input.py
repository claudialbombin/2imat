"""
This is just a test file to apply to the syntax highlighter
"""


def main(input_1):
    """Main function of the file

    Args:
        input_1 (bool): input boolean
    """
    if input_1 or (True and not False):
        # This is a comment that should be green
        print("This should be red")
    print("The end")
