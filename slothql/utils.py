def is_magic_name(name: str) -> bool:
    return name.startswith('__') and name.endswith('__')
