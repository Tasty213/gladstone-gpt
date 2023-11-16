# test_getattr_or_default.py
from ingester.utils import getattr_or_default


class Object:
    pass


def test_existing_attribute():
    obj = Object()
    obj.key = "value"
    result = getattr_or_default(obj, "key", "default")
    assert result == "value"


def test_non_existing_attribute():
    obj = Object()
    obj.another_key = "value"
    result = getattr_or_default(obj, "key", "default")
    assert result == "default"


def test_none_value_attribute():
    obj = Object()
    obj.key = None
    result = getattr_or_default(obj, "key", "default")
    assert result == "default"


def test_default_value():
    obj = Object()
    obj.another_key = "value"
    result = getattr_or_default(obj, "key")
    assert result is None


def test_default_argument():
    obj = Object()
    obj.another_key = "value"
    result = getattr_or_default(obj, "key", default="custom_default")
    assert result == "custom_default"


def test_object_without_getattr():
    obj = None
    result = getattr_or_default(obj, "key", "default")
    assert result == "default"


def test_object_with_getattr_error():
    class CustomObject:
        def __getattr__(self, attr):
            raise AttributeError("Custom AttributeError")

    obj = CustomObject()
    result = getattr_or_default(obj, "key", "default")
    assert result == "default"
