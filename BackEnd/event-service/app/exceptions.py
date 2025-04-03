class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class FailedError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        
class RegistrationForbidden(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)