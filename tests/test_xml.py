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
    OffsetValueProperty,
    RelativeOffsetValueProperty,
    AutoSizeValueProperty,
    StretchSizeProperty,
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
    assert template.count_property.reference_name == "nowhere"
    assert isinstance(template.count_property, ReferenceProperty)


def test_signature_attribute_value():
    template_description = """
        <template signature="0x11223344"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.signature == bytes([0x11, 0x22, 0x33, 0x44])


def test_hint_attribute_optional():
    template_description = """
        <template hint="optional"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.hint == "optional"


def test_offset_attribute_value():
    template_description = """
        <template offset="0x10"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.offset == 0x10
    assert isinstance(template.offset_property, OffsetValueProperty)


def test_offset_attribute_reference():
    template_description = """
        <template offset="{nowhere}"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.offset_property.reference_name == "nowhere"
    assert isinstance(template.offset_property, RelativeOffsetReferenceProperty)


def test_addressing_mode_default():
    template_description = """
        <template></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)


def test_addressing_mode_absolute():
    template_description = """
        <template adressing-mode="absolute"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)


def test_addressing_mode_relative_value():
    template_description = """
        <template adressing-mode="relative"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert isinstance(template.offset_property, RelativeOffsetValueProperty)


def test_addressing_mode_relative_value():
    template_description = """
        <template offset="{nowhere}" adressing-mode="relative"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert isinstance(template.offset_property, RelativeOffsetReferenceProperty)


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
    assert template.size_property.reference_name == "nowhere"
    assert isinstance(template.size_property, ReferenceProperty)


def test_sizing_attribute_default():
    template_description = """
        <template></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert isinstance(template.size_property, AutoSizeValueProperty)


def test_sizing_attribute_fix():
    template_description = """
        <template sizing="fix"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert isinstance(template.size_property, ValueProperty)


def test_sizing_attribute_auto():
    template_description = """
        <template sizing="auto"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert isinstance(template.size_property, AutoSizeValueProperty)


def test_sizing_attribute_stretch():
    template_description = """
        <template sizing="stretch"></template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert isinstance(template.size_property, StretchSizeProperty)


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
    assert template.boundary_property.reference_name == "nowhere"
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
    assert template.padding_before.reference_name == "nowhere"
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
    assert template.padding_after.reference_name == "nowhere"
    assert isinstance(template.padding_after, ReferenceProperty)


def test_template_tree_hierarchy():
    pass

def test_namespaces():
    template_description = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<template xmlns:g="https://schemas.denisvasilik.com/glsp" xmlns:ns3="https://schemas.denisvasilik.com/baml" name="sprotty">
    <template g:height="52.0" g:id="571b4dc1-8c40-4bd8-8deb-56fe69918469" g:layout="vbox" name="parent" g:taskType="manual" g:type="task:manual" g:width="128.48332977294922" g:x="110.0" g:y="160.0">
        <template g:height="52.0" g:id="child-1" g:layout="vbox" name="child-1" g:taskType="manual" g:type="task:manual" g:width="129.31666564941406" g:x="110.0" g:y="280.0">
            <template g:height="52.0" g:id="child-2" g:layout="vbox" name="child-2" g:taskType="manual" g:type="task:manual" g:width="129.31666564941406" g:x="220.0" g:y="450.0">
                <template g:height="52.0" g:id="a6e900f2-6ef0-425e-98f7-e1113e79de76" g:layout="vbox" name="ManualTask4" g:taskType="manual" g:type="task:manual" g:width="198.89999389648438" g:x="190.0" g:y="680.0"/>
            </template>
            <template g:height="52.0" g:id="2e3e308d-c835-4b2f-93d5-e00d1d871350" g:layout="vbox" name="ManualTask3" g:taskType="manual" g:type="task:manual" g:width="198.89999389648438" g:x="-110.0" g:y="440.0">
                <template g:height="52.0" g:id="37d07a39-87dc-41d6-ba06-610d87f8c0b7" g:layout="vbox" name="child-5" g:taskType="manual" g:type="task:manual" g:width="129.31666564941406" g:x="-70.0" g:y="680.0"/>
            </template>
        </template>
    </template>
</template>
    """
    template = XMLTemplateParser(template_description).parse()
    assert template.name == 'sprotty'
    assert template.children[0].name == 'parent'
    assert template.children[0].children[0].name == 'child-1'
