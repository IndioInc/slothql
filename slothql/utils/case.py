import re

CAMELCASE_SNAKE_REGEX = re.compile(r"([a-z\d])([A-Z])")


def snake_to_camelcase(string: str) -> str:
    first_char = next((i for i, c in enumerate(string) if c != "_"), len(string))
    prefix, suffix = string[:first_char], string[first_char:]
    words = [i or "_" for i in suffix.split("_")] if suffix else []
    return prefix + "".join(word.title() if i else word for i, word in enumerate(words))


def camelcase_to_snake(string: str) -> str:
    return re.sub(CAMELCASE_SNAKE_REGEX, r"\1_\2", string).lower()
