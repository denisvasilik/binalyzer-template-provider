"""
    test_binalyzer.py
    ~~~~~~~~~~~~~~~~~

    This module implements higher level tests for scenarios such as data
    dissection, analysis and generation.
"""
import unittest
import io

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
