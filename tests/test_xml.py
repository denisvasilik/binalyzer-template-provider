import unittest
import antlr4

from binalyzer_core import (
    Template,
    RelativeOffsetValueProperty,
    AutoSizeValueProperty,
    ValueProperty,
    BackedBindingContext,
)
from binalyzer_template_provider import XMLTemplateParser, XMLTemplateFileParser
from binalyzer_template_provider.xml import create_input_stream


def test_default_template_mapping():
    template = XMLTemplateParser(
        """
        <template>
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.name is None
    assert template.children == ()
    assert template.parent is None
    assert template.absolute_address == 0
    assert template.offset == 0
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)
    assert template.size == 0
    assert isinstance(template.size_property, AutoSizeValueProperty)
    assert template.padding_before == 0
    assert isinstance(template.padding_before_property, ValueProperty)
    assert template.padding_after == 0
    assert isinstance(template.padding_after_property, ValueProperty)
    assert template.boundary == 0
    assert isinstance(template.boundary_property, ValueProperty)
    assert template.value == bytes()
    assert isinstance(template.binding_context, BackedBindingContext)


def test_name_attribute():
    template = XMLTemplateParser(
        """
        <template name="test-template0">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.name == "test-template0"


def test_offset_attribute():
    template = XMLTemplateParser(
        """
        <template offset="0x100">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.offset == 0x100
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)


def test_addressing_mode_absolute_without_offset_attribute():
    template = XMLTemplateParser(
        """
        <template addressing-mode="absolute">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)


def test_addressing_mode_absolute_with_offset_attribute():
    template = XMLTemplateParser(
        """
        <template offset="0x1" addressing-mode="absolute">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert isinstance(template.offset_property, ValueProperty)


def test_addressing_mode_relative_without_offset_attribute():
    template = XMLTemplateParser(
        """
        <template addressing-mode="relative">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)


def test_addressing_mode_relative_with_offset_attribute():
    template = XMLTemplateParser(
        """
        <template offset="0x1" addressing-mode="relative">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)


def test_size_attribute():
    template = XMLTemplateParser(
        """
        <template size="512">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.size == 512


def test_boundary_attribute():
    template = XMLTemplateParser(
        """
        <template boundary="0x800">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.boundary == 0x800


def test_padding_before_attribute():
    template = XMLTemplateParser(
        """
        <template padding-before="0x100">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.padding_before == 0x100


def test_padding_after_attribute():
    template = XMLTemplateParser(
        """
        <template padding-after="0x400">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.padding_after == 0x400


def test_field_padding_before():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field0" padding-before="0x100">
                    </field>
                </area>
            </layout>
        </template>
    """
    ).parse()
    field0 = template.layout0.area0.field0
    assert field0.padding_before == 0x100
    assert field0.padding_after == 0


def test_field_padding_after():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field0" padding-after="0x100">
                    </field>
                </area>
            </layout>
        </template>
    """
    ).parse()
    field0 = template.layout0.area0.field0
    assert field0.padding_before == 0
    assert field0.padding_after == 0x100


def test_parse_template():
    template = XMLTemplateParser(
        """
        <template>
        </template>
    """
    ).parse()
    assert isinstance(template, Template)


def test_parse_layout():
    template = XMLTemplateParser(
        """
        <template>
            <layout name="layout0">
            </layout>
        </template>
    """
    ).parse()
    assert isinstance(template.layout0, Template)
    assert id(template.layout0) == id(template.children[0])
    assert template.layout0.parent == template
    assert template.layout0.name == "layout0"


def test_parse_area():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                </area>
            </layout>
        </template>
    """
    ).parse()
    assert isinstance(template.layout0.area0, Template)
    assert id(template.layout0.area0) == id(template.children[0].children[0])
    assert template.layout0.area0.parent == template.layout0
    assert template.layout0.area0.name == "area0"


def test_parse_field():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field0" size="4"></field>
                    <field name="field1" size="4"></field>
                    <field name="field2" size="4"></field>
                    <field name="field3" size="4"></field>
                </area>
            </layout>
        </template>
    """
    ).parse()
    field0 = template.layout0.area0.field0
    assert isinstance(field0, Template)
    assert id(field0) == id(template.children[0].children[0].children[0])
    assert field0.parent == template.layout0.area0
    assert field0.name == "field0"


def test_parse_repetition():
    pass


def test_parse_nested_area():
    pass
