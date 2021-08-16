"""
    test_text
    ~~~~~~~~~

    This module implements tests for the text property.
"""
from binalyzer_core import Template
from binalyzer_template_provider import XMLTemplateParser


def test_text_property_with_hex_value():
    template = XMLTemplateParser(
        """
        <template text="0x00112233">
        </template>
    """
    ).parse()
    assert template.text == bytes([0x00, 0x11, 0x22, 0x33])


def test_text_between_tags():
    template = XMLTemplateParser(
        """
        <template>
            00 11 22 33
        </template>
    """
    ).parse()
    assert template.text == bytes([0x00, 0x11, 0x22, 0x33])


def test_text_sets_template_size_between_tags():
    template = XMLTemplateParser(
        """
        <template>
            55 66 77 88
        </template>
    """).parse()
    assert template.text == bytes([0x55, 0x66, 0x77, 0x88])
    assert template.value == bytes()
    assert template.size == 4


def test_text_sets_template_size_with_hex_value():
    template = XMLTemplateParser(
        """
        <template text="0x55667788">
        </template>
    """).parse()
    assert template.text == bytes([0x55, 0x66, 0x77, 0x88])
    assert template.value == bytes()
    assert template.size == 4


def test_size_overrides_size_of_text_attribute():
    template = XMLTemplateParser(
        """
        <template size="2" text="0x55667788">
        </template>
    """).parse()
    assert template.text == bytes([0x55, 0x66, 0x77, 0x88])
    assert template.value == bytes()
    assert template.size == 2