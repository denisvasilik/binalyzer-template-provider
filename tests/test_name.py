"""
    test_name
    ~~~~~~~~~

    This module implements tests for a template's name attribute.
"""
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
