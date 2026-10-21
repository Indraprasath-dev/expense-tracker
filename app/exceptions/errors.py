class AppException(Exception):
    """Base for all application errors."""

    status_code: int = 400
    code: str = "app_error"
    message: str = "Application error"

    def __init__(self, message: str | None = None):
        self.message = message or type(self).message
        super().__init__(self.message)


class NotFoundError(AppException):
    status_code = 404
    code = "not_found"
    message = "Resource not found."


class ConflictError(AppException):
    status_code = 409
    code = "conflict"
    message = "Resource already exists."


class UnauthorizedError(AppException):
    status_code = 401
    code = "unauthorized"
    message = "Authentication required."


class UserNotFound(NotFoundError):
    code = "user_not_found"
    message = "User not found."


class CategoryNotFound(NotFoundError):
    code = "category_not_found"
    message = "Category not found."


class CategoryNameExists(ConflictError):
    code = "category_name_exists"
    message = "You already have a category with this name."


class EmailAlreadyExists(ConflictError):
    code = "email_already_exists"
    message = "This email is already registered."


class CategoryArchived(ConflictError):
    code = "category_archived"
    message = "This category is archived. Restore it first or choose another category."


class ExpenseNotFound(NotFoundError):
    code = "expense_not_found"
    message = "Expense not found."


class BudgetNotFound(NotFoundError):
    code = "budget_not_found"
    message = "Budget not found."


class BudgetAlreadyExists(ConflictError):
    code = "budget_already_exists"
    message = "A budget already exists for this category and month."


class NotAuthenticated(UnauthorizedError):
    code = "not_authenticated"
    message = "Not authenticated."


class InvalidCredentials(UnauthorizedError):
    code = "invalid_credentials"
    message = "Incorrect email or password."


class InvalidToken(UnauthorizedError):
    code = "invalid_token"
    message = "Invalid token. Log in again."


class TokenExpired(UnauthorizedError):
    code = "token_expired"
    message = "Token has expired. Log in again."
