import pytest
import io

from anytree.util import rightsibling, leftsibling

from binalyzer_core import (
    Binalyzer,
    Sizing,
    TemplateProvider,
    ZeroedDataProvider,
    DataProvider,
    siblings,
    leftsiblings,
    rightsiblings,
)
from binalyzer_template_provider import XMLTemplateParser


def test_get_previous_sibling():
    template = XMLTemplateParser(
        """
        <template name="root" sizing="auto">
            <area name="child0" size="4"></area>
            <area name="child1" size="4"></area>
            <area name="child2" size="4"></area>
            <area name="child3" size="4"></area>
            <area name="child4" size="4"></area>
        </template>
    """
    ).parse()

    assert template.child1 == leftsibling(template.child2)
    assert None == leftsibling(template.child0)
    assert template.child3 == leftsibling(template.child4)


def test_get_previous_siblings():
    template = XMLTemplateParser(
        """
        <template name="root" sizing="auto">
            <area name="child0" size="4"></area>
            <area name="child1" size="4"></area>
            <area name="child2" size="4"></area>
            <area name="child3" size="4"></area>
            <area name="child4" size="4"></area>
        </template>
    """
    ).parse()

    actual_siblings = leftsiblings(template.child2)
    expected_siblings = [template.child1, template.child0]

    assert expected_siblings == actual_siblings


def test_get_next_sibling():
    template = XMLTemplateParser(
        """
        <template name="root" sizing="auto">
            <area name="child0" size="4"></area>
            <area name="child1" size="4"></area>
            <area name="child2" size="4"></area>
            <area name="child3" size="4"></area>
            <area name="child4" size="4"></area>
        </template>
    """
    ).parse()

    assert template.child3 == rightsibling(template.child2)
    assert template.child1 == rightsibling(template.child0)
    assert None == rightsibling(template.child4)


def test_get_next_siblings():
    template = XMLTemplateParser(
        """
        <template name="root" sizing="auto">
            <area name="child0" size="4"></area>
            <area name="child1" size="4"></area>
            <area name="child2" size="4"></area>
            <area name="child3" size="4"></area>
            <area name="child4" size="4"></area>
        </template>
    """
    ).parse()

    expected_siblings = [template.child2, template.child3, template.child4]

    assert expected_siblings == rightsiblings(template.child1)


def test_get_siblings():
    template = XMLTemplateParser(
        """
        <template name="root" sizing="auto">
            <area name="child0" size="4"></area>
            <area name="child1" size="4"></area>
            <area name="child2" size="4"></area>
            <area name="child3" size="4"></area>
            <area name="child4" size="4"></area>
        </template>
    """
    ).parse()

    expected_siblings = [
        template.child3,
        template.child2,
        template.child1,
        template.child0,
    ]

    actual_siblings = siblings(template.child4)

    assert expected_siblings == actual_siblings


def test_sizing_explicit_auto_root_no_children():
    template = XMLTemplateParser(
        """
        <template name="root" sizing="auto">
        </template>
    """
    ).parse()
    template_provider = TemplateProvider(template)
    binalyzer = Binalyzer(template_provider)

    assert binalyzer.template.root.size.value == 0


def test_sizing_implicit_auto_root_no_children():
    template = XMLTemplateParser(
        """
        <template name="root">
        </template>
    """
    ).parse()
    template_provider = TemplateProvider(template)
    binalyzer = Binalyzer(template_provider)

    assert binalyzer.template.root.size.value == 0


def test_sizing_explicit_auto_root_children():
    template = XMLTemplateParser(
        """
        <template name="root" sizing="auto">
            <area name="child" size="128"></area>
        </template>
    """
    ).parse()
    template_provider = TemplateProvider(template)
    binalyzer = Binalyzer(template_provider)

    assert binalyzer.template.root.size.value == 128


def test_sizing_implicit_auto_root_children():
    template = XMLTemplateParser(
        """
        <template name="root">
            <area name="child" size="128"></area>
        </template>
    """
    ).parse()
    template_provider = TemplateProvider(template)
    binalyzer = Binalyzer(template_provider)

    assert binalyzer.template.root.size.value == 128


def test_sizing_implicit_fix():
    template = XMLTemplateParser(
        """
        <template name="root" size="256">
        </template>
    """
    ).parse()
    template_provider = TemplateProvider(template)
    binalyzer = Binalyzer(template_provider)

    assert binalyzer.template.root.size.value == 256
    assert binalyzer.template.root.sizing == Sizing.Fix


def test_sizing_explicit_fix():
    template = XMLTemplateParser(
        """
        <template name="root" sizing="fix" size="256">
        </template>
    """
    ).parse()
    template_provider = TemplateProvider(template)
    binalyzer = Binalyzer(template_provider)

    assert binalyzer.template.root.size.value == 256
    assert binalyzer.template.root.sizing == Sizing.Fix


def test_sizing_fix_override_with_sizing_set_to_auto():
    template = XMLTemplateParser(
        """
        <template name="root" sizing="auto" size="256">
        </template>
    """
    ).parse()
    template_provider = TemplateProvider(template)
    binalyzer = Binalyzer(template_provider)

    assert binalyzer.template.root.size.value == 256
    assert binalyzer.template.root.sizing == Sizing.Fix


def test_sizing_fix_override_with_sizing_set_to_stretch():
    template = XMLTemplateParser(
        """
        <template name="root" sizing="stretch" size="256">
        </template>
    """
    ).parse()
    template_provider = TemplateProvider(template)
    binalyzer = Binalyzer(template_provider)

    assert binalyzer.template.root.size.value == 256
    assert binalyzer.template.root.sizing == Sizing.Fix


def test_sizing_stretch_root_template():
    template = XMLTemplateParser(
        """
        <template name="root" sizing="stretch">
        </template>
    """
    ).parse()
    data_provider = DataProvider(bytes([0] * 512))
    template_provider = TemplateProvider(template)
    binalyzer = Binalyzer(template_provider, data_provider)
    binalyzer.template = template_provider.template
    binalyzer.data = io.BytesIO(bytes([0] * 512))

    assert binalyzer.template.root.size.value == 512
    assert binalyzer.template.root.sizing == Sizing.Stretch


def test_sizing_stretch_to_parent():
    template = XMLTemplateParser(
        """
        <template name="root" size="96">
            <area size="32"></area>
            <area name="area1" sizing="stretch"></area>
        </template>
    """
    ).parse()
    template_provider = TemplateProvider(template)
    binalyzer = Binalyzer(template_provider)

    assert binalyzer.template.root.area1.size.value == 64
    assert binalyzer.template.root.area1.sizing == Sizing.Stretch


@pytest.mark.skip("origin attribute is not supported")
def test_sizing_stretch_to_sibling():
    template = XMLTemplateParser(
        """
        <template name="root" size="96">
            <area name="area0" size="32"></area>
            <area name="area1" sizing="stretch"></area>
            <area name="area2" origin="end" size="4"></area>
        </template>
    """
    ).parse()
    template_provider = TemplateProvider(template)
    binalyzer = Binalyzer(template_provider)

    assert binalyzer.template.root.area1.size.value == 60
    assert binalyzer.template.root.area1.sizing == Sizing.Stretch
