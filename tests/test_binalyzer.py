import unittest
import io
import antlr4

from anytree import find_by_attr

from binalyzer_core import (
    BindingContext,
    Binalyzer,
    Template,
    ByteOrder,
    AddressingMode,
    ResolvableValue,
    DataProvider,
    TemplateProvider,
)
from binalyzer_template_provider import XMLTemplateParser


class BinalyzerTestCase(unittest.TestCase):

    TEST_DATA_STREAM_128 = io.BytesIO(
        bytes([0] * 32) + bytes([1] * 32) + bytes([2] * 32) + bytes([3] * 32)
    )

    def assertStreamEqual(self, first, second):
        for first_byte in first:
            for second_byte in second:
                self.assertEqual(first_byte, second_byte)

    def test_data_generation(self):
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
        self.assertEqual(binalyzer.template.size.value, 128)
        self.assertStreamEqual(binalyzer.data, self.TEST_DATA_STREAM_128)

    def test_data_transformation(self):
        """Layout stays the same for source and binary file, but data changes
        """
        pass

    def test_layout_transformation(self):
        """Layout projection or transformation happens if a file with its source layout
        is projected or transformed to a destination file with a destination layout that
        differs from the source layout"""
        pass

    def test_field_absolute_offset(self):
        test_data_stream = io.BytesIO(bytes([0] * 128))
        expected_data_stream = io.BytesIO(
            bytes([0] * 32) + bytes([1] * 32) + bytes([2] * 32) + bytes([3] * 32)
        )
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
        template_provider = TemplateProvider(template)
        data_provider = DataProvider(test_data_stream)
        template.binding_context = BindingContext(template_provider, data_provider)
        area = template.layout0.area0
        area.children[0].value = bytes([0] * 32)
        area.children[1].value = bytes([1] * 32)
        area.children[2].value = bytes([2] * 32)
        area.children[3].value = bytes([3] * 32)
        self.assertStreamEqual(test_data_stream, expected_data_stream)

    def test_field_relative_offset(self):
        test_data_stream = io.BytesIO(bytes([0] * 128))
        expected_data_stream = io.BytesIO(
            bytes([0] * 32) + bytes([1] * 32) + bytes([2] * 32) + bytes([3] * 32)
        )
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
        template_provider = TemplateProvider(template)
        data_provider = DataProvider(test_data_stream)
        template.binding_context = BindingContext(template_provider, data_provider)
        area = template.layout0.area0
        area.children[0].value = bytes([0] * 32)
        area.children[1].value = bytes([1] * 32)
        area.children[2].value = bytes([2] * 32)
        area.children[3].value = bytes([3] * 32)
        self.assertStreamEqual(test_data_stream, expected_data_stream)

    def test_field_cross_reference(self):
        test_data_stream = io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00]))
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
        template_provider = TemplateProvider(template)
        data_provider = DataProvider(test_data_stream)
        template.binding_context = BindingContext(template_provider, data_provider)
        field1_size = find_by_attr(template, "field1_size")
        field1 = find_by_attr(template, "field1")
        field2 = find_by_attr(template, "field2")
        self.assertEqual(field1_size.size.value, 4)
        self.assertEqual(field1_size.value, bytes([0x04, 0x00, 0x00, 0x00]))
        self.assertEqual(field1.size.value, 0x4)
        self.assertEqual(field2.size.value, 0x4000000)

    def test_binding_at_object_instantiation(self):
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
        self.assertEqual(field1_size.size.value, 4)
        self.assertEqual(field1_size.value, bytes([0x04, 0x00, 0x00, 0x00]))
        self.assertEqual(field1.size.value, 0x4)
        self.assertEqual(field2.size.value, 0x4000000)

    def test_binding_at_stream_assignment(self):
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
        template_provider = TemplateProvider(template)
        data_provider = DataProvider(io.BytesIO(bytes(4 * [0x0])))
        binalyzer = Binalyzer(template_provider, data_provider)
        binalyzer.data = io.BytesIO(bytes([0x04, 0x00, 0x00, 0x00]))
        binalyzer.template = template_provider.template
        field1_size = find_by_attr(template, "field1_size")
        field1 = find_by_attr(template, "field1")
        field2 = find_by_attr(template, "field2")
        self.assertEqual(field1_size.size.value, 4)
        self.assertEqual(field1_size.value, bytes([0x04, 0x00, 0x00, 0x00]))
        self.assertEqual(field1.size.value, 0x4)
        self.assertEqual(field2.size.value, 0x4000000)

    def test_binding_at_template_assignment(self):
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
        self.assertEqual(field1_size.size.value, 4)
        self.assertEqual(field1_size.value, bytes([0x04, 0x00, 0x00, 0x00]))
        self.assertEqual(field1.size.value, 0x4)
        self.assertEqual(field2.size.value, 0x4000000)


class BoundaryAttributeTestCase(unittest.TestCase):
    """The boundary attribute specifies the boundary relative to the
    beginning of the template.

    The boundary attribute influences the relative offset as well
    as the size of a data area.

    In case a boundary and a relative offset is specified, the given
    offset overrides the offset influenced by the boundary. The same
    applies to the size.

    If the element that uses the boundary attribute has children, the size
    of the children will be considered for boundary calculation. The size
    will be a multiple of the boundary so that the size of the children are
    within the size of the multiple of the boundary.

    If a child specifies a padding-before or padding-after attribute, it will
    be taken into account for the size calculation.
    """

    def test_boundary_and_matching_parent_offset(self):
        template = XMLTemplateParser(
            """
            <template name="template0">
                <layout name="layout0" offset="0x200">
                    <area name="area0" boundary="0x200">
                    </area>
                </layout>
            </template>"""
        ).parse()
        self.assertEqual(template.layout0.offset.value, 0x200)
        self.assertEqual(template.layout0.area0.offset.value, 0x0)
        self.assertEqual(template.layout0.area0.absolute_address.value, 0x200)
        self.assertEqual(template.layout0.area0.boundary.value, 0x200)
        self.assertEqual(template.layout0.area0.size.value, 0x200)

    def test_boundary_and_not_matching_parent_offset(self):
        template = XMLTemplateParser(
            """
            <template name="template0">
                <layout name="layout0" offset="0x300">
                    <area name="area0" boundary="0x200">
                    </area>
                </layout>
            </template>"""
        ).parse()
        self.assertEqual(template.layout0.offset.value, 0x300)
        self.assertEqual(template.layout0.area0.offset.value, 0x100)
        self.assertEqual(template.layout0.area0.absolute_address.value, 0x400)
        self.assertEqual(template.layout0.area0.boundary.value, 0x200)
        self.assertEqual(template.layout0.area0.size.value, 0x200)

    def test_offset_override(self):
        template = XMLTemplateParser(
            """
            <template name="template0">
                <layout name="layout0" offset="0x300">
                    <area name="area0" offset="0x300" boundary="0x200">
                    </area>
                </layout>
            </template>"""
        ).parse()
        self.assertEqual(template.layout0.offset.value, 0x300)
        self.assertEqual(template.layout0.area0.offset.value, 0x300)
        self.assertEqual(template.layout0.area0.absolute_address.value, 0x600)
        self.assertEqual(template.layout0.area0.boundary.value, 0x200)
        self.assertEqual(template.layout0.area0.size.value, 0x200)

    def test_size_override(self):
        template = XMLTemplateParser(
            """
            <template name="template0">
                <layout name="layout0" offset="0x300">
                    <area name="area0" size="0x500" boundary="0x200">
                    </area>
                </layout>
            </template>"""
        ).parse()
        self.assertEqual(template.layout0.area0.boundary.value, 0x200)
        self.assertEqual(template.layout0.area0.size.value, 0x500)

    def test_size_override_wrapped(self):
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
        self.assertEqual(template.layout0.wrapper.boundary.value, 0x200)
        self.assertEqual(template.layout0.wrapper.area0.boundary.value, 0x200)
        self.assertEqual(template.layout0.wrapper.area0.size.value, 0x500)
        self.assertEqual(template.layout0.wrapper.size.value, 0x600)

    def test_size_with_children_and_even_boundary(self):
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
        self.assertEqual(template.layout0.area0.boundary.value, 0x200)
        self.assertEqual(template.layout0.area0.size.value, 0x400)

    def test_size_with_children_and_uneven_boundary(self):
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
        self.assertEqual(template.layout0.area0.boundary.value, 0x200)
        self.assertEqual(template.layout0.area0.size.value, 0x600)

    def test_size_with_children_and_even_padding(self):
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
        self.assertEqual(template.layout0.area0.boundary.value, 0x200)
        self.assertEqual(template.layout0.area0.size.value, 0x600)

    def test_size_with_children_and_uneven_padding(self):
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
        self.assertEqual(template.layout0.area0.boundary.value, 0x200)
        self.assertEqual(template.layout0.area0.size.value, 0x800)


class OffsetAttributeTestCase(unittest.TestCase):
    def test_relative_offset_calculation(self):
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
        self.assertEqual(template.offset.value, 0)
        self.assertEqual(template.absolute_address.value, 0)
        self.assertEqual(template.layout0.offset.value, 0)
        self.assertEqual(template.layout0.absolute_address.value, 0)
        self.assertEqual(template.layout0.area0.offset.value, 0)
        self.assertEqual(template.layout0.area0.absolute_address.value, 0)
        self.assertEqual(template.layout0.area1.offset.value, 0x300)
        self.assertEqual(template.layout0.area1.absolute_address.value, 0x300)
        self.assertEqual(template.layout1.offset.value, 0xA00)
        self.assertEqual(template.layout1.absolute_address.value, 0xA00)
        self.assertEqual(template.layout1.area2.offset.value, 0x0)
        self.assertEqual(template.layout1.area2.absolute_address.value, 0xA00)
        self.assertEqual(template.layout1.area3.offset.value, 0x300)
        self.assertEqual(template.layout1.area3.absolute_address.value, 0xD00)

    def test_absolute_address_assignment(self):
        template = XMLTemplateParser(
            """
            <template name="template0" offset="0x400">
                <layout name="layout0" offset="0x200">
                    <area name="area0" addressing-mode="absolute" offset="0x100">
                    </area>
                </layout>
            </template>"""
        ).parse()
        self.assertEqual(template.offset.value, 0x400)
        self.assertEqual(template.absolute_address.value, 0x400)
        self.assertEqual(template.layout0.offset.value, 0x200)
        self.assertEqual(template.layout0.absolute_address.value, 0x600)
        self.assertEqual(template.layout0.area0.offset.value, 0x100)
        self.assertEqual(template.layout0.area0.absolute_address.value, 0x100)

    def test_relative_offset_override(self):
        template = XMLTemplateParser(
            """
            <template name="template0" offset="0x400">
                <layout name="layout0" offset="0x200">
                    <area name="area0" offset="0x100">
                    </area>
                </layout>
            </template>"""
        ).parse()
        self.assertEqual(template.offset.value, 0x400)
        self.assertEqual(template.absolute_address.value, 0x400)
        self.assertEqual(template.layout0.offset.value, 0x200)
        self.assertEqual(template.layout0.absolute_address.value, 0x600)
        self.assertEqual(template.layout0.area0.offset.value, 0x100)
        self.assertEqual(template.layout0.area0.absolute_address.value, 0x700)


class PaddingAttributeTestCase(unittest.TestCase):
    def test_padding(self):
        pass


class SiteAttributeTestCase(unittest.TestCase):
    def test_size_aggregation_using_values_only(self):
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
        self.assertEqual(template.size.value, 60)
        self.assertEqual(template.layout0.size.value, 12)
        self.assertEqual(template.layout0.area00.size.value, 4)
        self.assertEqual(template.layout0.area00.field1.size.value, 1)
        self.assertEqual(template.layout0.area00.field2.size.value, 1)
        self.assertEqual(template.layout0.area00.field3.size.value, 1)
        self.assertEqual(template.layout0.area00.field4.size.value, 1)
        self.assertEqual(template.layout0.area01.size.value, 8)
        self.assertEqual(template.layout1.size.value, 48)
        self.assertEqual(template.layout1.area10.size.value, 16)
        self.assertEqual(template.layout1.area11.size.value, 32)

    def test_size_aggregation_using_same_offsets(self):
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
        self.assertEqual(template.size.value, 42)
        self.assertEqual(template.layout0.size.value, 42)
        self.assertEqual(template.layout0.area00.size.value, 4)
        self.assertEqual(template.layout0.area00.field1.size.value, 1)
        self.assertEqual(template.layout0.area00.field2.size.value, 1)
        self.assertEqual(template.layout0.area00.field3.size.value, 1)
        self.assertEqual(template.layout0.area00.field4.size.value, 1)
        self.assertEqual(template.layout0.area01.size.value, 8)
        self.assertEqual(template.layout0.area02.size.value, 32)

    def test_size_with_resolvable_values(self):
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
        self.assertEqual(template.size.value, 8)

    def test_size_with_parent_override(self):
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
        self.assertEqual(template.size.value, 16)

    def test_size_and_padding(self):
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
        self.assertEqual(template.layout0.area0.field4.offset.value, 4)
        self.assertEqual(template.layout0.area0.size.value, 7)
        self.assertEqual(template.layout0.area1.offset.value, 15)

    def test_size_without_children(self):
        template = XMLTemplateParser(
            """
            <template name="template0">
                <layout name="layout0">
                    <area name="area0">
                    </area>
                </layout>
            </template>"""
        ).parse()
        self.assertEqual(template.size.value, 0)
        self.assertEqual(template.layout0.size.value, 0)
        self.assertEqual(template.layout0.area0.size.value, 0)

    def test_size_and_boundary_with_leaf_node(self):
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
        self.assertEqual(template.layout0.area0.offset.value, 0x100)
        self.assertEqual(template.layout0.area0.absolute_address.value, 0x400)
        # End on boundary
        self.assertEqual(template.layout0.area0.size.value, 0x200)

    def test_size_and_boundary_without_leaf_node(self):
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
        self.assertEqual(template.layout0.area0.offset.value, 0x100)
        self.assertEqual(template.layout0.area0.absolute_address.value, 0x400)
        # End on boundary
        self.assertEqual(template.layout0.area0.size.value, 0x200)

    def test_nested_boundary(self):
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
        self.assertEqual(template.layout0.area0.offset.value, 0x100)
        self.assertEqual(template.layout0.area0.absolute_address.value, 0x400)
        self.assertEqual(template.layout0.area0.size.value, 0x200)
        self.assertEqual(template.layout0.area0.field0.size.value, 0x100)
        self.assertEqual(template.layout0.area0.field0.offset.value, 0x0)

    def test_inner_boundary_greater_than_outer_boundary(self):
        pass

    def test_inner_boundary_equal_outer_boundary(self):
        pass

    def test_inner_boundary_smaller_than_outer_boundary(self):
        pass


class ByteOrderTestCase(unittest.TestCase):
    def test_default_instantiation(self):
        byte_order = ByteOrder()
        self.assertTrue(isinstance(byte_order, ByteOrder))
        self.assertEqual(byte_order.value, ByteOrder.LITTLE_ENDIAN_VALUE)

    def test_instantiation_with_value(self):
        byte_order = ByteOrder(ByteOrder.BIG_ENDIAN_VALUE)
        self.assertTrue(isinstance(byte_order, ByteOrder))
        self.assertEqual(byte_order.value, ByteOrder.BIG_ENDIAN_VALUE)
        byte_order = ByteOrder(ByteOrder.LITTLE_ENDIAN_VALUE)
        self.assertTrue(isinstance(byte_order, ByteOrder))
        self.assertEqual(byte_order.value, ByteOrder.LITTLE_ENDIAN_VALUE)

    def test_factory_method_for_byte_order_little_endian(self):
        byte_order = ByteOrder.LittleEndian
        self.assertTrue(isinstance(byte_order, ByteOrder))
        self.assertEqual(byte_order.value, ByteOrder.LITTLE_ENDIAN_VALUE)

    def test_factory_method_for_byte_order_big_endian(self):
        byte_order = ByteOrder.BigEndian
        self.assertTrue(isinstance(byte_order, ByteOrder))
        self.assertEqual(byte_order.value, ByteOrder.BIG_ENDIAN_VALUE)


class AddressingModeTestCase(unittest.TestCase):
    def test_default_instantiation(self):
        addressing_mode = AddressingMode()
        self.assertTrue(isinstance(addressing_mode, AddressingMode))
        self.assertEqual(addressing_mode.value, AddressingMode.ABSOLUTE_VALUE)

    def test_instantiation_with_value(self):
        addressing_mode = AddressingMode(AddressingMode.ABSOLUTE_VALUE)
        self.assertTrue(isinstance(addressing_mode, AddressingMode))
        self.assertEqual(addressing_mode.value, AddressingMode.ABSOLUTE_VALUE)
        addressing_mode = AddressingMode(AddressingMode.RELATIVE_VALUE)
        self.assertTrue(isinstance(addressing_mode, AddressingMode))
        self.assertEqual(addressing_mode.value, AddressingMode.RELATIVE_VALUE)

    def test_factory_method_for_addressing_mode_absolute(self):
        addressing_mode = AddressingMode.Absolute
        self.assertTrue(isinstance(addressing_mode, AddressingMode))
        self.assertEqual(addressing_mode.value, AddressingMode.ABSOLUTE_VALUE)

    def test_factory_method_for_addressing_mode_relative(self):
        addressing_mode = AddressingMode.Relative
        self.assertTrue(isinstance(addressing_mode, AddressingMode))
        self.assertEqual(addressing_mode.value, AddressingMode.RELATIVE_VALUE)


class ResolvableValueTestCase(unittest.TestCase):
    def test_default_instantiation(self):
        resolvable_value = ResolvableValue()
        self.assertEqual(resolvable_value.value, 0)
        self.assertEqual(resolvable_value.ref_id, None)
        self.assertFalse(resolvable_value.is_reference)
        self.assertEqual(resolvable_value.addressing_mode, AddressingMode.Relative)
        self.assertEqual(resolvable_value.byte_order, ByteOrder.LittleEndian)
