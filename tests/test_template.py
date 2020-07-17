"""
    test_template
    ~~~~~~~~~~~~~

    This module implements tests for the mapping of a XML description to a
    template tree.
"""
from binalyzer_core import Template
from binalyzer_template_provider import XMLTemplateParser


def test_template_mapping_root():
    template = XMLTemplateParser(
        """
        <template>
        </template>
    """
    ).parse()
    assert isinstance(template, Template)
    assert template.name is None
    assert template.children == ()
    assert template.parent is None
    assert template.absolute_address == 0
    assert template.offset == 0
    assert template.size == 0
    assert template.padding_before == 0
    assert template.padding_after == 0
    assert template.boundary == 0
    assert template.value == bytes()


def test_template_mapping_nested_1st_depth():
    template = XMLTemplateParser(
        """
        <template>
            <section>
            </section>
        </template>
    """
    ).parse()
    assert isinstance(template.children[0], Template)
    assert template.children[0].name is None
    assert template.children[0].children == ()
    assert template.children[0].parent == template
    assert template.children[0].absolute_address == 0
    assert template.children[0].offset == 0
    assert template.children[0].size == 0
    assert template.children[0].padding_before == 0
    assert template.children[0].padding_after == 0
    assert template.children[0].boundary == 0
    assert template.children[0].value == bytes()


def test_template_mapping_nested_2nd_depth():
    template = XMLTemplateParser(
        """
        <template>
            <layout>
                <area></area>
            </layout>
        </template>
    """
    ).parse()
    assert isinstance(template.children[0].children[0], Template)
    assert template.children[0].children[0].name is None
    assert template.children[0].children[0].children == ()
    assert template.children[0].children[0].parent == template.children[0]
    assert template.children[0].children[0].absolute_address == 0
    assert template.children[0].children[0].offset == 0
    assert template.children[0].children[0].size == 0
    assert template.children[0].children[0].padding_before == 0
    assert template.children[0].children[0].padding_after == 0
    assert template.children[0].children[0].boundary == 0
    assert template.children[0].children[0].value == bytes()
