import pytest
from bravado_core.exception import SwaggerValidationError
from opsyclient.utils import validate_email, email_format


def test_validate_email():
    good_emails = [
        'admin@example.com',
        'admin@example123.com',
        'admin+opsy@example.com']
    bad_emails = [
        'admin&&&@example.com',
        'admin@example___123.com']

    for email in good_emails:
        validate_email(email)  # should not raise exception
    for email in bad_emails:
        with pytest.raises(SwaggerValidationError):
            validate_email(email)


def test_email_format():
    assert email_format.format == 'email'
    assert email_format.to_wire('admin.example.com') == 'admin.example.com'
    assert email_format.to_python('admin.example.com') == 'admin.example.com'
    assert email_format.validate == validate_email
