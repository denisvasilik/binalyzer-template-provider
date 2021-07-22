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
