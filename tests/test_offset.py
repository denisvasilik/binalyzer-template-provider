"""
    test_offset
    ~~~~~~~~~~~

    This module implements tests related to a template's offset.
"""
import io

from binalyzer_core import (
    Binalyzer,
    Template,
    RelativeOffsetValueProperty,
    OffsetValueProperty,
    ValueProperty,
)
from binalyzer_template_provider import XMLTemplateParser


TEST_DATA_STREAM_128 = io.BytesIO(
    bytes([0] * 32) + bytes([1] * 32) + bytes([2] * 32) + bytes([3] * 32)
)


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
    assert isinstance(template.offset_property, OffsetValueProperty)


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
    assert isinstance(template.offset_property, OffsetValueProperty)


def test_field_absolute_offset():
    expected_data_stream = bytes([0] * 32 + [1] * 32 + [2] * 32 + [3] * 32)
    test_data_stream = io.BytesIO(bytes([0] * 128))
    template = XMLTemplateParser(
        """<template name="template0">
            <field name="field0" offset="0" size="32"></field>
            <field name="field1" offset="32" size="32"></field>
            <field name="field2" offset="64" size="32"></field>
            <field name="field3" offset="96" size="32"></field>
        </template>"""
    ).parse()
    binalyzer = Binalyzer(template, test_data_stream)
    template = binalyzer.template
    template.field0.value = bytes([0] * 32)
    template.field1.value = bytes([1] * 32)
    template.field2.value = bytes([2] * 32)
    template.field3.value = bytes([3] * 32)
    assert binalyzer.template.value == expected_data_stream


def test_field_relative_offset():
    expected_data_stream = bytes([0] * 32 + [1] * 32 + [2] * 32 + [3] * 32)
    test_data_stream = io.BytesIO(bytes([0] * 128))
    template = XMLTemplateParser(
        """<template name="template0">
            <field name="field0" size="32"></field>
            <field name="field1" size="32"></field>
            <field name="field2" size="32"></field>
            <field name="field3" size="32"></field>
        </template>"""
    ).parse()
    binalyzer = Binalyzer(template, test_data_stream)

    binalyzer.template.field0.value = bytes([0] * 32)
    binalyzer.template.field1.value = bytes([1] * 32)
    binalyzer.template.field2.value = bytes([2] * 32)
    binalyzer.template.field3.value = bytes([3] * 32)
    assert binalyzer.template.value == expected_data_stream


def test_offset_override():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0" offset="0x300">
                <area name="area0" offset="0x300" boundary="0x200">
                    <field name="field0" size="1">
                    </field>
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout0.offset == 0x300
    assert template.layout0.area0.offset == 0x300
    assert template.layout0.area0.absolute_address == 0x600
    assert template.layout0.area0.boundary == 0x200
    assert template.layout0.area0.size == 0x200


def test_relative_offset_calculation():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field size="0x100"></field>
                    <field size="0x200"></field>
                </area>
                <area name="area1">
                    <field size="0x300"></field>
                    <field size="0x400"></field>
                </area>
            </layout>
            <layout name="layout1">
                <area name="area2">
                    <field size="0x100"></field>
                    <field size="0x200"></field>
                </area>
                <area name="area3">
                    <field size="0x300"></field>
                    <field size="0x400"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.offset == 0
    assert template.absolute_address == 0
    assert template.layout0.offset == 0
    assert template.layout0.absolute_address == 0
    assert template.layout0.area0.offset == 0
    assert template.layout0.area0.absolute_address == 0
    assert template.layout0.area1.offset == 0x300
    assert template.layout0.area1.absolute_address == 0x300
    assert template.layout1.offset == 0xA00
    assert template.layout1.absolute_address == 0xA00
    assert template.layout1.area2.offset == 0x0
    assert template.layout1.area2.absolute_address == 0xA00
    assert template.layout1.area3.offset == 0x300
    assert template.layout1.area3.absolute_address == 0xD00


def test_absolute_address_assignment():
    template = XMLTemplateParser(
        """
        <template name="template0" offset="0x400">
            <layout name="layout0" offset="0x200">
                <area name="area0" addressing-mode="absolute" offset="0x100">
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.offset == 0x400
    assert template.absolute_address == 0x400
    assert template.layout0.offset == 0x200
    assert template.layout0.absolute_address == 0x600
    assert template.layout0.area0.offset == 0x100
    assert template.layout0.area0.absolute_address == 0x100


def test_relative_offset_override():
    template = XMLTemplateParser(
        """
        <template name="template0" offset="0x400">
            <layout name="layout0" offset="0x200">
                <area name="area0" offset="0x100">
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.offset == 0x400
    assert template.absolute_address == 0x400
    assert template.layout0.offset == 0x200
    assert template.layout0.absolute_address == 0x600
    assert template.layout0.area0.offset == 0x100
    assert template.layout0.area0.absolute_address == 0x700

def test_relative_offset_override():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <field name="field0" offset="0x4" size="4"></field>
            <field name="field1" offset="{field0}"></field>
        </template>"""
    ).parse()
    template.field0.value = bytes([0x08])
    assert template.field0.offset == 0x4
    assert template.field0.value == bytes([0x08])
    assert template.field1.offset == 0x8
    assert template.field1.absolute_address == 0x8
