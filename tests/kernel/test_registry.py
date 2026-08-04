import pytest
from PySide6.QtWidgets import QPushButton
from limekit.kernel.registry import Registry, registry
from limekit.kernel.declarative import LimeObject
from limekit.kernel.errors import RegistryError


def test_register_and_get(qapp):
    r = Registry()

    class W(LimeObject, QPushButton):
        pass

    r.register("ui.Thing", W)
    assert r.get("ui.Thing") is W


def test_unknown_path_raises(qapp):
    with pytest.raises(RegistryError, match="ui.Missing"):
        Registry().get("ui.Missing")


def test_duplicate_path_raises(qapp):
    r = Registry()

    class A(LimeObject, QPushButton):
        pass

    class B(LimeObject, QPushButton):
        pass

    r.register("ui.Thing", A)
    with pytest.raises(RegistryError, match="already registered"):
        r.register("ui.Thing", B)


def test_path_must_be_dotted(qapp):
    class W(LimeObject, QPushButton):
        pass

    with pytest.raises(RegistryError, match="module.Name"):
        Registry().register("Thing", W)


def test_modules_groups_by_prefix(qapp):
    r = Registry()

    class A(LimeObject, QPushButton):
        pass

    class B(LimeObject, QPushButton):
        pass

    r.register("ui.Button", A)
    r.register("fs.Reader", B)
    assert r.modules() == {"ui": {"Button": A}, "fs": {"Reader": B}}


def test_declaring_lime_auto_registers(qapp):
    class W(LimeObject, QPushButton):
        __lime__ = "ui.AutoRegistered"

    assert registry.get("ui.AutoRegistered") is W
    registry.clear_path("ui.AutoRegistered")


def test_classes_without_lime_are_not_registered(qapp):
    class W(LimeObject, QPushButton):
        pass

    assert W not in registry.all()
