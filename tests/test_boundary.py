"""
    test_boundary
    ~~~~~~~~~~~~~

    This module implements tests related to a template's boundary.
"""
import io

from binalyzer_core import Binalyzer, Template, ValueProperty
from binalyzer_template_provider import XMLTemplateParser


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


def test_boundary_and_matching_parent_offset():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0" offset="0x200">
                <area name="area0" boundary="0x200">
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout0.offset == 0x200
    assert template.layout0.area0.offset == 0x0
    assert template.layout0.area0.absolute_address == 0x200
    assert template.layout0.area0.boundary == 0x200
    assert template.layout0.area0.size == 0x200


def test_boundary_and_not_matching_parent_offset():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0" offset="0x300">
                <area name="area0" boundary="0x200">
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout0.offset == 0x300
    assert template.layout0.area0.offset == 0x100
    assert template.layout0.area0.absolute_address == 0x400
    assert template.layout0.area0.boundary == 0x200
    assert template.layout0.area0.size == 0x200


def test_nested_boundary():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0" offset="0x300">
                <area name="area0" boundary="0x200">
                    <field name="field0" boundary="0x100">
                    </field>
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout0.area0.offset == 0x100
    assert template.layout0.area0.absolute_address == 0x400
    assert template.layout0.area0.size == 0x200
    assert template.layout0.area0.field0.size == 0x100
    assert template.layout0.area0.field0.offset == 0x0


def test_root_template_no_offset_and_boundary():
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


def test_root_template_offset_and_boundary():
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
    binalyzer.data = io.BytesIO(bytes([0x01] * binalyzer.template.size))
    binalyzer.template.header.value = bytes([0x02] * 4)
    assert binalyzer.template.offset == 32
    assert binalyzer.template.size == 256
    assert binalyzer.template.header.size == 4
    assert binalyzer.template.header.value == bytes([0x02] * 4)
    assert binalyzer.template.payload.size == 252
    assert binalyzer.template.payload.value == bytes([0x01] * 220)
