import json

from core.models import DynamicSetting

BILLING_ENABLED = "billing_enabled"
INVOICE_TAX = "invoice_tax"

DEFAULTS = {
    BILLING_ENABLED: False,
    INVOICE_TAX: 11
}


def _get_casted_value(setting: DynamicSetting):
    if setting.type == DynamicSetting.DataType.JSON:
        return json.loads(setting.value)
    elif setting.type == DynamicSetting.DataType.BOOLEAN:
        return setting.value == "1"
    elif setting.type == DynamicSetting.DataType.INT:
        return int(setting.value)
    elif setting.type == DynamicSetting.DataType.STR:
        return setting.value
    else:
        raise ValueError("Type not supported")


def get_dynamic_settings():
    result = DEFAULTS.copy()
    settings = DynamicSetting.objects.all()
    for setting in settings:
        result[setting.key] = _get_casted_value(setting)

    return result


def get_dynamic_setting(key):
    setting: DynamicSetting = DynamicSetting.objects.filter(key=key).first()
    if not setting:
        return DEFAULTS[key]

    return setting.value


def set_dynamic_setting(key, value):
    if type(value) is dict:
        inserted_value = json.dumps(value)
        data_type = DynamicSetting.DataType.JSON
    elif type(value) is bool:
        inserted_value = "1" if value else "0"
        data_type = DynamicSetting.DataType.BOOLEAN
    elif type(value) is int:
        inserted_value = str(value)
        data_type = DynamicSetting.DataType.INT
    elif type(value) is str:
        inserted_value = value
        data_type = DynamicSetting.DataType.STR
    else:
        raise ValueError("Type not supported")

    DynamicSetting.objects.update_or_create(key=key, defaults={
        "value": inserted_value,
        "type": data_type
    })
