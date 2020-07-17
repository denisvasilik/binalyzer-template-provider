"""
    test_binalyzer.py
    ~~~~~~~~~~~~~~~~~

    This module implements higher level tests for scenarios such as data
    dissection, analysis and generation.
"""
import io
import os
import unittest


from anytree import find_by_attr

from binalyzer_core import (
    BindingContext,
    Binalyzer,
    Template,
    DataProvider,
    TemplateProvider,
)
from binalyzer_template_provider import XMLTemplateParser, XMLTemplateProviderExtension


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


def test_data_analysis():
    cwd_path = os.path.dirname(os.path.abspath(__file__))

    binalyzer = Binalyzer()
    XMLTemplateProviderExtension(binalyzer)
    binalyzer.xml.from_file(
        os.path.join(cwd_path, "resources/wasm_module.xml"),
        os.path.join(cwd_path, "resources/wasm_module.wasm"),
    )

    instructions = binalyzer.template.code_section.code.function.instructions

    assert binalyzer.template.magic.value == bytes([0x00, 0x61, 0x73, 0x6D])
    assert binalyzer.template.version.value == bytes([0x01, 0x00, 0x00, 0x00])
    assert instructions.value == bytes([0x01, 0x0B])
