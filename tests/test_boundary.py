"""
    test_boundary
    ~~~~~~~~~~~~~

    This module implements tests related to a template's boundary. A boundary
    attribute influences the following attributes:

    * Offset of current template
    * Absolute address of current template
    * Size of current template
    * Size of parent template

    NOTE: The current template is the template where the boundary is declared.
"""
import io

from binalyzer_core import Binalyzer, Template, ValueProperty
from binalyzer_template_provider import XMLTemplateParser


def test_boundary_attribute():
    template = XMLTemplateParser(
        """
        <template boundary="0x800"></template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert isinstance(template.boundary_property, ValueProperty)
    assert template.offset == 0
    assert template.boundary == 0x800
    assert template.size == 0


def test_boundary_attribute_nested():
    template = XMLTemplateParser(
        """
        <template boundary="0x200">
            <template boundary="0x100">
                <field size="1"></field>
            </template>
        </template>
    """
    ).parse()
    assert template.absolute_address == 0
    assert template.offset == 0
    assert template.size == 0x200
    assert template.children[0].absolute_address == 0
    assert template.children[0].offset == 0
    assert template.children[0].size == 0x100


def test_boundary_attribute_nested_with_inner_element_having_greater_boundary():
    template = XMLTemplateParser(
        """
        <template boundary="0x200">
            <template boundary="0x500">
                <field name="field" size="1">
                </field>
            </template>
        </template>
    """
    ).parse()
    assert template.absolute_address == 0
    assert template.offset == 0
    assert template.size == 0x600
    assert template.children[0].absolute_address == 0
    assert template.children[0].offset == 0
    assert template.children[0].size == 0x500


def test_boundary_attribute_with_offset():
    template = XMLTemplateParser(
        """
        <template offset="0x20" boundary="0x100">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert isinstance(template.boundary_property, ValueProperty)
    assert template.offset == 256
    assert template.size == 0


def test_boundary_attribute_with_offset_and_child():
    template = XMLTemplateParser(
        """
        <template offset="0x20" boundary="0x100">
            <field size="1"></field>
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert isinstance(template.boundary_property, ValueProperty)
    assert template.offset == 256
    assert template.size == 256


def test_boundary_attribute_with_parent_offset_on_boundary():
    template = XMLTemplateParser(
        """
        <template>
            <layout name="layout" offset="0x200">
                <area name="area" boundary="0x200">
                    <field name="field" size="1"></field>
                </area>
            </layout>
        </template>
    """
    ).parse()
    assert template.layout.area.absolute_address == 0x200
    assert template.layout.offset == 0x200
    assert template.layout.area.offset == 0x0
    assert template.layout.area.boundary == 0x200
    assert template.layout.area.size == 0x200


def test_boundary_attribute_with_parent_offset_besides_boundary():
    template = XMLTemplateParser(
        """
        <template>
            <layout name="layout" offset="0x300">
                <area name="area" boundary="0x200">
                    <field name="field" size="1"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout.offset == 0x300
    assert template.layout.area.offset == 0x100
    assert template.layout.area.absolute_address == 0x400
    assert template.layout.area.boundary == 0x200
    assert template.layout.area.size == 0x200


def test_boundary_attribute_with_parent_offset_besides_boundary_and_nested():
    template = XMLTemplateParser(
        """
        <template>
            <layout name="layout" offset="0x300">
                <area name="area" boundary="0x200">
                    <field name="field" boundary="0x100">
                        <field name="nested_field" size="1"></field>
                    </field>
                </area>
            </layout>
        </template>
    """
    ).parse()
    assert template.layout.area.absolute_address == 0x400
    assert template.layout.area.offset == 0x100
    assert template.layout.area.size == 0x200
    assert template.layout.area.field.size == 0x100
    assert template.layout.area.field.offset == 0x0


def test_boundary_and_sizing_stretch():
    template = XMLTemplateParser(
        """
        <template boundary="0x100">
            <header name="header" size="4">
            </header>
            <payload name="payload" sizing="stretch">
            </payload>
        </template>
    """
    ).parse()
    binalyzer = Binalyzer(template)
    binalyzer.data = io.BytesIO(bytes([0x01] * binalyzer.template.size))
    binalyzer.template.header.value = bytes([0x02] * 4)
    assert binalyzer.template.payload.size == 252
    assert binalyzer.template.size == 256
    assert binalyzer.template.header.size == 4
    assert binalyzer.template.header.value == bytes([0x02] * 4)
    assert binalyzer.template.payload.value == bytes([0x01] * 252)


def test_boundary_and_sizing_stretch_with_offset():
    template = XMLTemplateParser(
        """
        <template offset="0x20" boundary="0x100">
            <header name="header" size="4">
            </header>
            <payload name="payload" sizing="stretch">
            </payload>
        </template>
    """
    ).parse()
    binalyzer = Binalyzer(template)
    binalyzer.template.header.value = bytes([0x02] * 4)
    binalyzer.template.payload.value = bytes([0x01] * binalyzer.template.payload.size)
    assert binalyzer.template.offset == 256
    assert binalyzer.template.size == 256
    assert binalyzer.template.header.size == 4
    assert binalyzer.template.header.value == bytes([0x02] * 4)
    assert binalyzer.template.payload.offset == 4
    assert binalyzer.template.payload.size == 252
    assert binalyzer.template.payload.value == bytes(
        [0x01] * binalyzer.template.payload.size
    )
