class TemplateNotFound(Exception):
    def __init__(self, path):
        super().__init__(path)
