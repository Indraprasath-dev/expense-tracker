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
