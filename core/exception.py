class PriceNotFound(Exception):
    def __init__(self, identifier=None):
        self.identifier = identifier
