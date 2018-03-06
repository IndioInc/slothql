def snake_to_camelcase(string: str) -> str:
    first_char = next((i for i, c in enumerate(string) if c != '_'), len(string))
    prefix, suffix = string[:first_char], string[first_char:]
    words = [i or '_' for i in suffix.split('_')] if suffix else []
    return prefix + ''.join(word.title() if i else word for i, word in enumerate(words))
