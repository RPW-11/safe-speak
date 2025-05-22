from fastapi import HTTPException


class AppExceptionBase(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(AppExceptionBase):
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail)


class DuplicateEntryException(AppExceptionBase):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class UserInputException(AppExceptionBase):
    def __init__(self, detail):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedException(AppExceptionBase):
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail)


class DatabaseException(AppExceptionBase):
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(status_code=500, detail=detail)


class ForbiddenException(AppExceptionBase):
    def __init__(self, detail: str):
        super().__init__(status_code=403, detail=detail)