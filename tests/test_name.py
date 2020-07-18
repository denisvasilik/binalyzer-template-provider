"""
    test_name
    ~~~~~~~~~

    This module implements tests for a template's name attribute.
"""
import pytest

from binalyzer_core import Template
from binalyzer_template_provider import XMLTemplateParser


def test_name_attribute():
    template = XMLTemplateParser(
        """
        <template name="test-template0">
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.name == "test-template0"


def test_name_attribut_no_reference_allowed():
    with pytest.raises(RuntimeError):
        template = XMLTemplateParser(
            """
            <template>
                <template name="a"></template>
                <template name="{a}"></template>
            </template>
        """
        ).parse()
