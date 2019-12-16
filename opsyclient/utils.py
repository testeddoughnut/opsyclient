import re
from bravado_core.exception import SwaggerValidationError
from bravado_core.formatter import SwaggerFormat


def validate_email(email_string):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(email_regex, email_string) is None:
        raise SwaggerValidationError(f'Email {email_string} is invalid')


email_format = SwaggerFormat(  # pylint: disable=invalid-name
    format='email',
    description='Email address format',
    to_wire=lambda email_object: email_object,
    to_python=lambda email_string: email_string,
    validate=validate_email
)
