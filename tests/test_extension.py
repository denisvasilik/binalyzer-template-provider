import io
import pytest

from binalyzer_core import Binalyzer
from binalyzer_template_provider import XMLTemplateProviderExtension
from binalyzer_wasm import WebAssemblyExtension


def test_from_url():
    url = "https://raw.githubusercontent.com/denisvasilik/binalyzer-template-provider/"
    binalyzer = Binalyzer()
    XMLTemplateProviderExtension(binalyzer)
    WebAssemblyExtension(binalyzer)
    binalyzer.xml.from_url(
        url + "master/tests/resources/wasm_module.xml",
        url + "master/tests/resources/wasm_module.wasm",
    )

    instructions = binalyzer.template.code_section.code.function.func_body.instructions
    instructions.value = bytes([0x0B, 0x00])

    assert binalyzer.template.magic.value == bytes([0x00, 0x61, 0x73, 0x6D])
    assert binalyzer.template.version.value == bytes([0x01, 0x00, 0x00, 0x00])
    assert instructions.value == bytes([0x0B, 0x00])
