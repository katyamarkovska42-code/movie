from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    if response.status_code == 400:
        code = "validation_error"
        message = "Перевірте коректність даних."

    elif response.status_code == 401:
        code = "unauthorized"
        message = "Для виконання цієї дії потрібно увійти в акаунт."

    elif response.status_code == 403:
        code = "permission_denied"
        message = "У вас немає дозволу на виконання цієї дії."

    elif response.status_code == 404:
        code = "not_found"
        message = "Об'єкт не знайдено."

    else:
        code = "request_error"
        message = "Не вдалося виконати запит."

    response.data = {
        "error": {
            "code": code,
            "message": message,
            "details": response.data,
        }
    }

    return response
