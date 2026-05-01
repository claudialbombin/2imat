import re
from color_string import color_string

FILE_PATH= 'input.py'

COMMENT_REGEX = re.compile(r'#.*\n') # punto significa algo/cualquier cosa
BLUE_REGEX = re.compile(r'\b(True|and|not|or|False|def|class)\b')


def parse_file(path, print_result = False):
	with open(path, 'r') as f:
		content = f.read()
	
	rules = [
		{
			'pattern': COMMENT_REGEX,
			"action": lambda match: color_string(match.group(0), "green")
		},
		{
			'pattern': BLUE_REGEX,
			"action": lambda match: color_string(match.group(1), "blue")
		}
	]

	parsed = content
	for rule in rules:
		parsed = re.sub(rule['pattern'], rule['action'], content)
	
	if print_result:
		print(parsed)
	
	if __name__ == "__main__":
		parse_file(FILE_PATH, True)