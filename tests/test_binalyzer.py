"""
    test_binalyzer
    ~~~~~~~~~~~~~~

    This module implements higher level tests for scenarios such as data
    dissection, analysis and generation.
"""
import io
import os
import pytest


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


@pytest.fixture
def binalyzer():
    binalyzer = Binalyzer()
    XMLTemplateProviderExtension(binalyzer)
    return binalyzer


def test_data_generation(binalyzer):
    binalyzer.xml.from_str(
        """
        <template>
            <layout name="layout">
                <area name="area">
                    <field name="field0" size="32"></field>
                    <field name="field1" size="32"></field>
                    <field name="field2" size="32"></field>
                    <field name="field3" size="32"></field>
                </area>
            </layout>
        </template>
    """
    )
    binalyzer.template.layout.area.field0.value = bytes([0] * 32)
    binalyzer.template.layout.area.field1.value = bytes([1] * 32)
    binalyzer.template.layout.area.field2.value = bytes([2] * 32)
    binalyzer.template.layout.area.field3.value = bytes([3] * 32)

    assert binalyzer.template.size == 128
    assertStreamEqual(binalyzer.data, TEST_DATA_STREAM_128)


def test_analysis_of_static_template(binalyzer):
    header_size = 0x100
    data_size = 0x10
    footer_size = 0x100

    binalyzer.xml.from_str(
        f"""
        <template>
            <section name="header" size="{header_size}"></section>
            <section name="data" size="{data_size}"></section>
            <section name="footer" size="{footer_size}"></section>
        </template>
    """
    )

    binalyzer.data = io.BytesIO(
        bytes([0x03] * header_size)
        + bytes([0x05] * data_size)
        + bytes([0x03] * footer_size)
    )

    assert binalyzer.template.size == (header_size + data_size + footer_size)
    assert binalyzer.template.header.size == header_size
    assert binalyzer.template.header.value == bytes([0x03] * header_size)
    assert binalyzer.template.data.size == data_size
    assert binalyzer.template.data.value == bytes([0x05] * data_size)
    assert binalyzer.template.footer.size == footer_size
    assert binalyzer.template.footer.value == bytes([0x03] * footer_size)


def test_analysis_of_dynamic_template(binalyzer):
    cwd_path = os.path.dirname(os.path.abspath(__file__))
    binalyzer.xml.from_file(
        os.path.join(cwd_path, "resources/wasm_module.xml"),
        os.path.join(cwd_path, "resources/wasm_module.wasm"),
    )

    instructions = binalyzer.template.code_section.code.function.instructions

    assert binalyzer.template.magic.value == bytes([0x00, 0x61, 0x73, 0x6D])
    assert binalyzer.template.version.value == bytes([0x01, 0x00, 0x00, 0x00])
    assert instructions.value == bytes([0x01, 0x0B])


def test_data_modification(binalyzer):
    cwd_path = os.path.dirname(os.path.abspath(__file__))
    binalyzer.xml.from_file(
        os.path.join(cwd_path, "resources/wasm_module.xml"),
        os.path.join(cwd_path, "resources/wasm_module.wasm"),
    )

    instructions = binalyzer.template.code_section.code.function.instructions

    instructions.value = bytes([0x0B, 0x00])

    assert binalyzer.template.magic.value == bytes([0x00, 0x61, 0x73, 0x6D])
    assert binalyzer.template.version.value == bytes([0x01, 0x00, 0x00, 0x00])
    assert instructions.value == bytes([0x0B, 0x00])
