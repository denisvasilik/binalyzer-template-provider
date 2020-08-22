"""
    test_xml
    ~~~~~~~~~~

    This module implements tests for the XML parser. It solely tests whether
    the declarative description of a template tree is properly transfered to a
    template tree.
"""
import pytest

from binalyzer_core import (
    ValueProperty,
    ReferenceProperty,
    RelativeOffsetReferenceProperty,
    RelativeOffsetValueProperty,
)

from binalyzer_template_provider import XMLTemplateParser


def test_plain_template():
    template_description = """
        <template></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template


def test_name_attribute_value():
    template_description = """
        <template name="root"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.name == "root"


def test_name_attribute_no_reference_allowed():
    template_description = """
        <template name="{nowhere}"></template>
    """
    with pytest.raises(RuntimeError) as excinfo:
        XMLTemplateParser(template_description).parse()
    assert "Using a reference for a name attribute is not allowed." in str(
        excinfo.value
    )


def test_count_attribute_value():
    template_description = """
        <template count="7"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.count == 7
    assert isinstance(template.count_property, ValueProperty)


def test_count_attribute_reference():
    template_description = """
        <template count="{nowhere}"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.count_property.value_provider.reference_name == "nowhere"
    assert isinstance(template.count_property, ReferenceProperty)


def test_signature_attribute_value():
    pass


def test_hint_attribute_value():
    pass


def test_offset_attribute_value():
    template_description = """
        <template offset="0x10"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.offset == 0x10
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)


def test_offset_attribute_reference():
    template_description = """
        <template offset="{nowhere}"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.offset_property.value_provider.reference_name == "nowhere"
    assert isinstance(template.offset_property, RelativeOffsetReferenceProperty)


def test_addressing_mode_attribute_value():
    pass


def test_size_attribute_value():
    template_description = """
        <template size="16"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.size == 16
    assert isinstance(template.size_property, ValueProperty)


def test_size_attribute_reference():
    template_description = """
        <template size="{nowhere}"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.size_property.value_provider.reference_name == "nowhere"
    assert isinstance(template.size_property, ReferenceProperty)


def test_sizing_attribute_value():
    pass


def test_boundary_attribute_value():
    template_description = """
        <template boundary="0x100"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.boundary == 0x100
    assert isinstance(template.boundary_property, ValueProperty)


def test_boundary_attribute_reference():
    template_description = """
        <template boundary="{nowhere}"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.boundary_property.value_provider.reference_name == "nowhere"
    assert isinstance(template.boundary_property, ReferenceProperty)


def padding_before_attribute_value():
    template_description = """
        <template padding-before="0x20"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.padding_before == 0x20
    assert isinstance(template.padding_before_property, ValueProperty)


def padding_before_attribute_reference():
    template_description = """
        <template padding-before="{nowhere}"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.padding_before.value_provider.reference_name == "nowhere"
    assert isinstance(template.padding_before, ReferenceProperty)


def padding_after_attribute_referenced_value():
    template_description = """
        <template padding-after="0x30"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.padding_after == 0x30
    assert isinstance(template.padding_after_property, ValueProperty)


def padding_after_attribute_referenced_value():
    template_description = """
        <template padding-after="{nowhere}"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.padding_after.value_provider.reference_name == "nowhere"
    assert isinstance(template.padding_after, ReferenceProperty)


def test_template_tree_hierarchy():
    pass
