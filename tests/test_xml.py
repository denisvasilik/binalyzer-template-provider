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


def test_template_mapping_root():
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
    assert template.size == 0
    assert template.padding_before == 0
    assert template.padding_after == 0
    assert template.boundary == 0
    assert template.value == bytes()


def test_template_mapping_nested_1st_depth():
    template = XMLTemplateParser(
        """
        <template>
            <section>
            </section>
        </template>
    """
    ).parse()
    assert isinstance(template.children[0], Template)
    assert template.children[0].name is None
    assert template.children[0].children == ()
    assert template.children[0].parent == template
    assert template.children[0].absolute_address == 0
    assert template.children[0].offset == 0
    assert template.children[0].size == 0
    assert template.children[0].padding_before == 0
    assert template.children[0].padding_after == 0
    assert template.children[0].boundary == 0
    assert template.children[0].value == bytes()


def test_template_mapping_nested_2nd_depth():
    template = XMLTemplateParser(
        """
        <template>
            <layout>
                <area></area>
            </layout>
        </template>
    """
    ).parse()
    assert isinstance(template.children[0].children[0], Template)
    assert template.children[0].children[0].name is None
    assert template.children[0].children[0].children == ()
    assert template.children[0].children[0].parent == template.children[0]
    assert template.children[0].children[0].absolute_address == 0
    assert template.children[0].children[0].offset == 0
    assert template.children[0].children[0].size == 0
    assert template.children[0].children[0].padding_before == 0
    assert template.children[0].children[0].padding_after == 0
    assert template.children[0].children[0].boundary == 0
    assert template.children[0].children[0].value == bytes()


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
    assert template.absolute_address == 0x100
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)


def test_addressing_mode_absolute_without_offset_attribute():
    template = XMLTemplateParser(
        """
        <template addressing-mode="absolute">
        </template>
    """
    ).parse()
    assert template.offset == 0
    assert template.absolute_address == 0
    assert isinstance(template, Template)
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)


def test_addressing_mode_absolute_with_offset_attribute():
    template = XMLTemplateParser(
        """
        <template offset="0x1" addressing-mode="absolute">
        </template>
    """
    ).parse()
    assert template.offset == 0x1
    assert template.absolute_address == 0x1
    assert isinstance(template, Template)
    assert isinstance(template.offset_property, ValueProperty)


def test_addressing_mode_relative_without_offset_attribute():
    template = XMLTemplateParser(
        """
        <template addressing-mode="relative">
        </template>
    """
    ).parse()
    assert template.offset == 0
    assert template.absolute_address == 0
    assert isinstance(template, Template)
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)


def test_addressing_mode_relative_with_offset_attribute():
    template = XMLTemplateParser(
        """
        <template offset="0x1" addressing-mode="relative">
        </template>
    """
    ).parse()
    assert template.offset == 0x1
    assert template.absolute_address == 0x1
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
    assert isinstance(template.size_property, ValueProperty)


def test_size_attribute_nested_1st_depth():
    template = XMLTemplateParser(
        """
        <template>
            <field name="field0" size="4"></field>
            <field name="field1" size="4"></field>
            <field name="field2" size="4"></field>
            <field name="field3" size="4"></field>
        </template>
    """
    ).parse()
    assert isinstance(template.field0, Template)
    assert isinstance(template.field1, Template)
    assert isinstance(template.field2, Template)
    assert isinstance(template.field3, Template)
    assert template.size == 16
    assert isinstance(template.size_property, AutoSizeValueProperty)


def test_boundary_attribute():
    template = XMLTemplateParser(
        """
        <template boundary="0x800">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.boundary == 0x800
    assert isinstance(template.boundary_property, ValueProperty)


def test_padding_before_attribute():
    template = XMLTemplateParser(
        """
        <template padding-before="0x100">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.padding_before == 0x100
    assert isinstance(template.padding_before_property, ValueProperty)


def test_padding_before_attribute_nested():
    template = XMLTemplateParser(
        """
        <template>
            <field name="field" padding-before="0x100"></field>
        </template>
    """
    ).parse()
    assert template.offset == 0x0
    assert template.absolute_address == 0x0
    assert template.size == 0x100
    assert template.field.offset == 0x100
    assert template.field.absolute_address == 0x100
    assert template.field.padding_before == 0x100
    assert template.field.padding_after == 0
    assert template.field.size == 0
    assert isinstance(template.field.padding_before_property, ValueProperty)


def test_padding_after_attribute():
    template = XMLTemplateParser(
        """
        <template padding-after="0x400">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.padding_after == 0x400
    assert isinstance(template.padding_after_property, ValueProperty)


def test_padding_after_attribute_nested():
    template = XMLTemplateParser(
        """
        <template>
            <field name="field" padding-after="0x100"></field>
        </template>
    """
    ).parse()
    assert template.offset == 0x0
    assert template.absolute_address == 0x0
    assert template.size == 0x100
    assert template.field.offset == 0
    assert template.field.absolute_address == 0
    assert template.field.padding_before == 0
    assert template.field.padding_after == 0x100
    assert template.field.size == 0
    assert isinstance(template.field.padding_after_property, ValueProperty)


def test_padding_after_attribute_affects_sibling():
    template = XMLTemplateParser(
        """
        <template>
            <field name="field-padded" padding-after="0x100"></field>
            <field name="field-affected"></field>
        </template>
    """
    ).parse()
    assert template.offset == 0x0
    assert template.absolute_address == 0x0
    assert template.size == 0x100
    assert template.field_padded.offset == 0
    assert template.field_padded.absolute_address == 0
    assert template.field_padded.padding_before == 0
    assert template.field_padded.padding_after == 0x100
    assert template.field_padded.size == 0
    assert template.field_affected.offset == 0x100
    assert template.field_affected.absolute_address == 0x100
