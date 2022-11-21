from django.core import validators
from django.core.exceptions import ValidationError
from rest_framework import serializers


def email_list(value):
    try:
        emails = value.replace(" ", "").split(",")
        for email in emails:
            validators.validate_email(email)
    except ValidationError:
        raise serializers.ValidationError('Field contain invalid email address')
