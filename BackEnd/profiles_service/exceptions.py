class NotFoundError(Exception):
    def __init__(self, message="Resource not found"):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message