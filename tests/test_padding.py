"""
    test_padding
    ~~~~~~~~~~~~

    This module implements tests for a template's padding.
"""
from binalyzer_core import Template, ValueProperty
from binalyzer_template_provider import XMLTemplateParser


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
