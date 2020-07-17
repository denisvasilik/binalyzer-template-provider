"""
    test_size
    ~~~~~~~~~

    This module implements tests related to a template's size.
"""
import io

from binalyzer_core import (
    Binalyzer,
    Template,
    ValueProperty,
    AutoSizeValueProperty,
    TemplateProvider,
    DataProvider,
    BindingContext,
)
from binalyzer_template_provider import XMLTemplateParser


def test_size_attribute():
    template = XMLTemplateParser(
        """
        <template size="512">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.size == 512
    assert isinstance(template.size_property, ValueProperty)


def test_size_attribute_nested_1st_depth():
    template = XMLTemplateParser(
        """
        <template>
            <field name="field0" size="4"></field>
            <field name="field1" size="4"></field>
            <field name="field2" size="4"></field>
            <field name="field3" size="4"></field>
        </template>
    """
    ).parse()
    assert isinstance(template.field0, Template)
    assert isinstance(template.field1, Template)
    assert isinstance(template.field2, Template)
    assert isinstance(template.field3, Template)
    assert template.size == 16
    assert isinstance(template.size_property, AutoSizeValueProperty)


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
                    <field name="field1" size="{field1_size, byteorder=little}"></field>
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
