"""
    test_size
    ~~~~~~~~~

    This module implements tests related to a template's binding.
"""
import io
import pytest

from anytree import find_by_attr

from binalyzer_core import (
    Binalyzer,
    BinalyzerExtension,
    Template,
    DataProvider,
    TemplateProvider,
    ValueProviderBase,
)
from binalyzer_template_provider import XMLTemplateParser


@pytest.fixture
def binalyzer():
    binalyzer = Binalyzer()
    MockExtension(binalyzer)
    return binalyzer


def test_field_cross_reference():
    data = io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00]))
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field1-size" size="4"></field>
                    <field name="field1" size="{field1-size, byteorder=little}"></field>
                    <field name="field2" size="{field1-size, byteorder=big}"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    binalyzer = Binalyzer(template, data)
    field1_size = find_by_attr(template, "field1-size")
    field1 = find_by_attr(template, "field1")
    field2 = find_by_attr(template, "field2")
    assert field1_size.size == 4
    assert field1_size.value == bytes([0x04, 0x00, 0x00, 0x00])
    assert field1.size == 0x4
    assert field2.size == 0x4000000


def test_binding_at_object_instantiation():
    data_stream = io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00]))
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field1_size" size="4"></field>
                    <field name="field1" size="{field1_size, byteorder=little}"></field>
                    <field name="field2" size="{field1_size, byteorder=big}"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    binalyzer = Binalyzer(template, data_stream)
    field1_size = find_by_attr(template, "field1_size")
    field1 = find_by_attr(template, "field1")
    field2 = find_by_attr(template, "field2")
    assert field1_size.size == 4
    assert field1_size.value == bytes([0x04, 0x00, 0x00, 0x00])
    assert field1.size == 0x4
    assert field2.size == 0x4000000


def test_binding_at_stream_assignment():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field1_size" size="4"></field>
                    <field name="field1" size="{field1_size, byteorder=little}"></field>
                    <field name="field2" size="{field1_size, byteorder=big}"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    binalyzer = Binalyzer(template, io.BytesIO(bytes(4 * [0x0])))
    binalyzer.data = io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00]))
    field1_size = find_by_attr(template, "field1_size")
    field1 = find_by_attr(template, "field1")
    field2 = find_by_attr(template, "field2")
    assert field1_size.size == 4
    assert field1_size.value == bytes([0x04, 0x00, 0x00, 0x00])
    assert field1.size == 0x4
    assert field2.size == 0x4000000


def test_binding_at_template_assignment():
    template0 = XMLTemplateParser(
        """
        <template name="template0" size="4">
        </template>
        """
    ).parse()
    template1 = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field1_size" size="4"></field>
                    <field name="field1" size="{field1_size, byteorder=little}"></field>
                    <field name="field2" size="{field1_size, byteorder=big}"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    template_provider0 = TemplateProvider(template0)
    template_provider1 = TemplateProvider(template1)
    data_provider = DataProvider(io.BytesIO(bytes(4 * [0x0])))
    binalyzer = Binalyzer(template_provider0, data_provider)
    binalyzer.template = template_provider1.template
    binalyzer.data = io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00]))
    field1_size = find_by_attr(template1, "field1_size")
    field1 = find_by_attr(template1, "field1")
    field2 = find_by_attr(template1, "field2")
    assert field1_size.size == 4
    assert field1_size.value == bytes([0x04, 0x00, 0x00, 0x00])
    assert field1.size == 0x4
    assert field2.size == 0x4000000


def test_template_reference_with_provider(binalyzer):
    data = io.BytesIO(bytes([0xE5, 0x8E, 0x26]))
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field1_size" size="3"></field>
                    <field name="field1" size="{field1_size, provider=mock.ref_custom}"></field>
                </area>
            </layout>
        </template>""",
        binalyzer=binalyzer,
    ).parse()
    binalyzer = Binalyzer(template, data)
    field1_size = find_by_attr(template, "field1_size")
    field1 = find_by_attr(template, "field1")
    assert field1_size.size == 3
    assert field1_size.value == bytes([0xE5, 0x8E, 0x26])
    assert field1.size == 2526949


def test_template_with_provider(binalyzer):
    data = io.BytesIO(bytes([0x01, 0x02, 0x03, 0xE5, 0x8E, 0x26]))
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field1_size" size="3"></field>
                    <field name="field1" size="{provider=mock.custom}"></field>
                </area>
            </layout>
        </template>""",
        binalyzer=binalyzer,
    ).parse()
    binalyzer = Binalyzer(template, data)
    field1_size = find_by_attr(template, "field1_size")
    field1 = find_by_attr(template, "field1")
    assert field1_size.size == 3
    assert field1_size.value == bytes([0x01, 0x02, 0x03])
    assert field1.value == bytes([0xE5, 0x8E, 0x26])
    assert field1.size == 2526949


class MockExtension(BinalyzerExtension):
    def __init__(self, binalyzer=None):
        super(MockExtension, self).__init__(binalyzer, "mock")

    def init_extension(self):
        super(MockExtension, self).init_extension()

    def custom(self, property):
        value_provider = MockValueProvider(property)
        property.value_provider = value_provider
        return value_provider

    def ref_custom(self, property):
        value_provider = MockValueProvider(property)
        property.value_provider = value_provider
        return value_provider


class MockValueProvider(ValueProviderBase):
    def __init__(self, property):
        self.property = property

    def get_value(self):
        data = self.property.template.binding_context.data_provider.data
        absolute_address = self.property.template.absolute_address
        data.seek(absolute_address)
        return int.from_bytes(data.read(3), "little")

    def set_value(self, value):
        raise RuntimeError("Not implemented")
