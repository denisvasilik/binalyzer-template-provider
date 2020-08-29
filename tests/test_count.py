"""
    test_count
    ~~~~~~~~~~

    This module implements tests for a template's count attribute.
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


@pytest.fixture
def binalyzer():
    binalyzer = Binalyzer()
    XMLTemplateProviderExtension(binalyzer)
    return binalyzer


def test_count_attribute_without_children(binalyzer):
    binalyzer.xml.from_str(
        f"""
        <template>
            <field name="data" size="1" count="2"></field>
        </template>
    """
    )
    binalyzer.data = io.BytesIO(bytes([0x01, 0x02]))

    assert binalyzer.template.children[0].value == bytes([0x01])
    assert binalyzer.template.children[1].value == bytes([0x02])


def test_count_attribute_with_children(binalyzer):
    binalyzer.xml.from_str(
        f"""
        <template>
            <field name="data" count="2">
                <field name="field" size="1"></field>
            </field>
        </template>
    """
    )
    binalyzer.data = io.BytesIO(bytes([0x01, 0x02]))

    template = binalyzer.template

    assert template.children[0].children[0].value == bytes([0x01])
    assert template.children[1].children[0].value == bytes([0x02])


@pytest.mark.skip
def test_count_attribute_nested(binalyzer):
    pass


@pytest.mark.skip
def test_wasm_import_header_duplication_with_children(binalyzer):
    cwd_path = os.path.dirname(os.path.abspath(__file__))
    binalyzer.xml.from_file(
        os.path.join(cwd_path, "resources/wasm_module_format.xml"),
        os.path.join(cwd_path, "resources/app-hello-wasm.wasm"),
    )

    import_header = binalyzer.template.import_section.data.import_header

    assert len(import_header.children) == 4
    assert import_header.children[0].method_string_data.value == "proc_exit"
    assert import_header.children[1].method_string_data.value == "fd_write"
    assert import_header.children[2].method_string_data.value == "environ_sizes_get"
    assert import_header.children[3].method_string_data.value == "environ_get"
