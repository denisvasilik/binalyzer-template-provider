import unittest
import io
import antlr4

from anytree import find_by_attr

from binalyzer_core import (
    BindingContext,
    Binalyzer,
    Template,
    DataProvider,
    TemplateProvider,
)
from binalyzer_template_provider import XMLTemplateParser


TEST_DATA_STREAM_128 = io.BytesIO(
    bytes([0] * 32) + bytes([1] * 32) + bytes([2] * 32) + bytes([3] * 32)
)


def assertStreamEqual(first, second):
    for first_byte in first:
        for second_byte in second:
            assert first_byte == second_byte


def test_data_generation():
    binalyzer = Binalyzer()
    binalyzer.template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field0" size="32"></field>
                    <field name="field1" size="32"></field>
                    <field name="field2" size="32"></field>
                    <field name="field3" size="32"></field>
                </area>
            </layout>
        </template>
    """
    ).parse()
    area = binalyzer.template.layout0.area0
    area.children[0].value = bytes([0] * 32)
    area.children[1].value = bytes([1] * 32)
    area.children[2].value = bytes([2] * 32)
    area.children[3].value = bytes([3] * 32)

    assert binalyzer.template.size == 128
    assertStreamEqual(binalyzer.data, TEST_DATA_STREAM_128)


def test_field_absolute_offset():
    expected_data_stream = io.BytesIO(
        bytes([0] * 32) + bytes([1] * 32) + bytes([2] * 32) + bytes([3] * 32)
    )
    test_data_stream = io.BytesIO(bytes([0] * 128))
    template = XMLTemplateParser(
        """<template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field0" offset="0" size="32"></field>
                    <field name="field1" offset="32" size="32"></field>
                    <field name="field2" offset="64" size="32"></field>
                    <field name="field3" offset="96" size="32"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    binalyzer = Binalyzer(template, test_data_stream)
    area = template.layout0.area0
    area.children[0].value = bytes([0] * 32)
    area.children[1].value = bytes([1] * 32)
    area.children[2].value = bytes([2] * 32)
    area.children[3].value = bytes([3] * 32)
    assertStreamEqual(test_data_stream, expected_data_stream)


def test_field_relative_offset():
    expected_data_stream = io.BytesIO(
        bytes([0] * 32) + bytes([1] * 32) + bytes([2] * 32) + bytes([3] * 32)
    )
    test_data_stream = io.BytesIO(bytes([0] * 128))
    template = XMLTemplateParser(
        """<template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field0" size="32"></field>
                    <field name="field1" size="32"></field>
                    <field name="field2" size="32"></field>
                    <field name="field3" size="32"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    binalyzer = Binalyzer(template, test_data_stream)
    area = template.layout0.area0
    area.children[0].value = bytes([0] * 32)
    area.children[1].value = bytes([1] * 32)
    area.children[2].value = bytes([2] * 32)
    area.children[3].value = bytes([3] * 32)
    assertStreamEqual(test_data_stream, expected_data_stream)


def test_field_cross_reference():
    data = io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00]))
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field1_size" size="4"></field>
                    <field name="field1" size="{field1_size, ByteOrder=LittleEndian}"></field>
                    <field name="field2" size="{field1_size, ByteOrder=BigEndian}"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    binalyzer = Binalyzer(template, data)
    field1_size = find_by_attr(template, "field1_size")
    field1 = find_by_attr(template, "field1")
    field2 = find_by_attr(template, "field2")
    assert field1_size.size == 4
    assert field1_size.value == bytes([0x04, 0x00, 0x00, 0x00])
    assert field1.size == 0x4
    assert field2.size == 0x4000000


def test_binding_at_object_instantiation():
    data_stream = io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00]))
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field1_size" size="4"></field>
                    <field name="field1" size="{field1_size, ByteOrder=LittleEndian}"></field>
                    <field name="field2" size="{field1_size, ByteOrder=BigEndian}"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    binalyzer = Binalyzer(template, data_stream)
    field1_size = find_by_attr(template, "field1_size")
    field1 = find_by_attr(template, "field1")
    field2 = find_by_attr(template, "field2")
    assert field1_size.size == 4
    assert field1_size.value == bytes([0x04, 0x00, 0x00, 0x00])
    assert field1.size == 0x4
    assert field2.size == 0x4000000


def test_binding_at_stream_assignment():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field1_size" size="4"></field>
                    <field name="field1" size="{field1_size, ByteOrder=LittleEndian}"></field>
                    <field name="field2" size="{field1_size, ByteOrder=BigEndian}"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    binalyzer = Binalyzer(template, io.BytesIO(bytes(4 * [0x0])))
    binalyzer.data = io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00]))
    field1_size = find_by_attr(template, "field1_size")
    field1 = find_by_attr(template, "field1")
    field2 = find_by_attr(template, "field2")
    assert field1_size.size == 4
    assert field1_size.value == bytes([0x04, 0x00, 0x00, 0x00])
    assert field1.size == 0x4
    assert field2.size == 0x4000000


def test_binding_at_template_assignment():
    template0 = XMLTemplateParser(
        """
        <template name="template0" size="4">
        </template>
        """
    ).parse()
    template1 = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field1_size" size="4"></field>
                    <field name="field1" size="{field1_size, ByteOrder=LittleEndian}"></field>
                    <field name="field2" size="{field1_size, ByteOrder=BigEndian}"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    template_provider0 = TemplateProvider(template0)
    template_provider1 = TemplateProvider(template1)
    data_provider = DataProvider(io.BytesIO(bytes(4 * [0x0])))
    binalyzer = Binalyzer(template_provider0, data_provider)
    binalyzer.template = template_provider1.template
    binalyzer.data = io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00]))
    field1_size = find_by_attr(template1, "field1_size")
    field1 = find_by_attr(template1, "field1")
    field2 = find_by_attr(template1, "field2")
    assert field1_size.size == 4
    assert field1_size.value == bytes([0x04, 0x00, 0x00, 0x00])
    assert field1.size == 0x4
    assert field2.size == 0x4000000


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


def test_offset_override():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0" offset="0x300">
                <area name="area0" offset="0x300" boundary="0x200">
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout0.offset == 0x300
    assert template.layout0.area0.offset == 0x300
    assert template.layout0.area0.absolute_address == 0x600
    assert template.layout0.area0.boundary == 0x200
    assert template.layout0.area0.size == 0x200


def test_size_override():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0" offset="0x300">
                <area name="area0" size="0x500" boundary="0x200">
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout0.area0.boundary == 0x200
    assert template.layout0.area0.size == 0x500


def test_size_override_wrapped():
    template = XMLTemplateParser(
        """
            <template name="template0">
                <layout name="layout0" offset="0x300">
                    <area name="wrapper" boundary="0x200">
                        <area name="area0" size="0x500" boundary="0x200">
                        </area>
                    </area>
                </layout>
            </template>"""
    ).parse()
    assert template.layout0.wrapper.boundary == 0x200
    assert template.layout0.wrapper.area0.boundary == 0x200
    assert template.layout0.wrapper.area0.size == 0x500
    assert template.layout0.wrapper.size == 0x600


def test_size_with_children_and_even_boundary():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0" offset="0x300">
                <area name="area0" boundary="0x200">
                    <field name="field0" size="0x100"></field>
                    <field name="field1" size="0x100"></field>
                    <field name="field2" size="0x100"></field>
                    <field name="field3" size="0x100"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout0.area0.boundary == 0x200
    assert template.layout0.area0.size == 0x400


def test_size_with_children_and_uneven_boundary():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0" offset="0x300">
                <area name="area0" boundary="0x200">
                    <field name="field0" size="0x100"></field>
                    <field name="field1" size="0x100"></field>
                    <field name="field2" size="0x100"></field>
                    <field name="field3" size="0x200"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout0.area0.boundary == 0x200
    assert template.layout0.area0.size == 0x600


def test_size_with_children_and_even_padding():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0" boundary="0x200">
                    <field name="field0" size="0x100"
                                        padding-before="0x100"
                                        padding-after="0x100">
                    </field>
                    <field name="field1" size="0x100"
                                        padding-before="0x100"
                                        padding-after="0x100">
                    </field>
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout0.area0.boundary == 0x200
    assert template.layout0.area0.size == 0x600


def test_size_with_children_and_uneven_padding():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0" boundary="0x200">
                    <field name="field0" size="0x100"
                                        padding-before="0x100"
                                        padding-after="0x100">
                    </field>
                    <field name="field1" size="0x150"
                                        padding-before="0x100"
                                        padding-after="0x100">
                    </field>
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout0.area0.boundary == 0x200
    assert template.layout0.area0.size == 0x800


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


def test_size_aggregation_using_values_only():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area00">
                    <field name="field1" size="1"></field>
                    <field name="field2" size="1"></field>
                    <field name="field3" size="1"></field>
                    <field name="field4" size="1"></field>
                </area>
                <area name="area01">
                    <field name="field5" size="2"></field>
                    <field name="field6" size="2"></field>
                    <field name="field7" size="2"></field>
                    <field name="field8" size="2"></field>
                </area>
            </layout>
            <layout name="layout1">
                <area name="area10">
                    <field name="field9" size="4"></field>
                    <field name="field10" size="4"></field>
                    <field name="field11" size="4"></field>
                    <field name="field12" size="4"></field>
                </area>
                <area name="area11">
                    <field name="field13" size="8"></field>
                    <field name="field14" size="8"></field>
                    <field name="field15" size="8"></field>
                    <field name="field16" size="8"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.size == 60
    assert template.layout0.size == 12
    assert template.layout0.area00.size == 4
    assert template.layout0.area00.field1.size == 1
    assert template.layout0.area00.field2.size == 1
    assert template.layout0.area00.field3.size == 1
    assert template.layout0.area00.field4.size == 1
    assert template.layout0.area01.size == 8
    assert template.layout1.size == 48
    assert template.layout1.area10.size == 16
    assert template.layout1.area11.size == 32


def test_size_aggregation_using_same_offsets():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area00">
                    <field name="field1" size="1"></field>
                    <field name="field2" size="1"></field>
                    <field name="field3" size="1"></field>
                    <field name="field4" size="1"></field>
                </area>
                <area name="area01" offset="10">
                    <field name="field5" size="2"></field>
                    <field name="field6" size="2"></field>
                    <field name="field7" size="2"></field>
                    <field name="field8" size="2"></field>
                </area>
                <area name="area02" offset="10">
                    <field name="field9" size="8"></field>
                    <field name="field10" size="8"></field>
                    <field name="field11" size="8"></field>
                    <field name="field12" size="8"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.size == 64
    assert template.layout0.size == 64
    assert template.layout0.area00.size == 4
    assert template.layout0.area00.field1.size == 1
    assert template.layout0.area00.field2.size == 1
    assert template.layout0.area00.field3.size == 1
    assert template.layout0.area00.field4.size == 1
    assert template.layout0.area01.size == 8
    assert template.layout0.area02.size == 32


def test_size_with_resolvable_values():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                    <field name="field1_size" size="4"></field>
                    <field name="field1" size="{field1_size, ByteOrder=LittleEndian}"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    template_provider = TemplateProvider(template)
    data_provider = DataProvider(io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00])))
    template.binding_context = BindingContext(template_provider, data_provider)
    assert template.size == 8


def test_size_with_parent_override():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0" size="16">
                    <field name="field1_size" size="4"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    template_provider = TemplateProvider(template)
    data_provider = DataProvider(io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00])))
    template.binding_context = BindingContext(template_provider, data_provider)
    assert template.size == 16


def test_size_and_padding():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0" padding-after="4">
                    <field name="field1" size="1"></field>
                    <field name="field2" size="1"></field>
                    <field name="field3" size="1"></field>
                    <field name="field4" size="1" padding-before="1"
                                                padding-after="2"></field>
                </area>
                <area name="area1" padding-before="4">
                    <field name="field5" size="2"></field>
                    <field name="field6" size="2"></field>
                    <field name="field7" size="2"></field>
                    <field name="field8" size="2"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.layout0.area0.field4.offset == 4
    assert template.layout0.area0.size == 7
    assert template.layout0.area1.offset == 15


def test_size_without_children():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0">
                <area name="area0">
                </area>
            </layout>
        </template>"""
    ).parse()
    assert template.size == 0
    assert template.layout0.size == 0
    assert template.layout0.area0.size == 0


def test_size_and_boundary_with_leaf_node():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0" offset="0x300">
                <area name="area0" boundary="0x200">
                    <field name="field6" size="2"></field>
                </area>
            </layout>
        </template>"""
    ).parse()
    # Start on boundary
    assert template.layout0.area0.offset == 0x100
    assert template.layout0.area0.absolute_address == 0x400
    # End on boundary
    assert template.layout0.area0.size == 0x200


def test_size_and_boundary_without_leaf_node():
    template = XMLTemplateParser(
        """
        <template name="template0">
            <layout name="layout0" offset="0x300">
                <area name="area0" boundary="0x200">
                </area>
            </layout>
        </template>"""
    ).parse()
    # Start on boundary
    assert template.layout0.area0.offset == 0x100
    assert template.layout0.area0.absolute_address == 0x400
    # End on boundary
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
