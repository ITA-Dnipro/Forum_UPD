class NotFoundError(Exception):
    def __init__(self, message="Resource not found"):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
    

class InvalidRelatedEntityError(Exception):
    def __init__(self, message="One or more related entity do not exist"):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
