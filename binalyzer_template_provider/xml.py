# -*- coding: utf-8 -*-
"""
    binalyzer_template_provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Template providers are used to create a template tree from a description.

    :copyright: 2020 Denis Vasilík
    :license: MIT
"""
import antlr4
import logging
import copy
import io

from typing import Optional

from binalyzer_core import (
    PropertyBase,
    ValueProperty,
    ReferenceProperty,
    AutoSizeValueProperty,
    StretchSizeProperty,
    RelativeOffsetValueProperty,
    RelativeOffsetReferenceProperty,
    IntegerValueConverter,
    IdentityValueConverter,
    LEB128UnsignedValueConverter,
    LEB128UnsignedBindingValueProvider,
    LEB128SizeBindingValueProvider,
    Template,
    TemplateProvider,
    DataProvider,
    BindingContext,
)

from .generated import XMLParserListener, XMLLexer, XMLParser


_log = logging.getLogger("binalyzer")
_log.setLevel(logging.DEBUG)


def create_input_stream(filepath):
    with open(filepath, "r") as template_file:
        return antlr4.InputStream(template_file.read())


class XMLTemplateParser(XMLParserListener):

    DEFAULT_ADDRESSING_MODE = "relative"
    DEFAULT_SIZING = "auto"

    ATTRIBUTES = {
        "name": lambda self, attribute, template, ctx: self._parse_name_attribute(
            attribute, template, ctx
        ),
        "offset": lambda self, attribute, template, ctx: self._parse_offset_attribute(
            attribute, template, ctx
        ),
        "size": lambda self, attribute, template, ctx: self._parse_size_attribute(
            attribute, template, ctx
        ),
        "count": lambda self, attribute, template, ctx: self._parse_count_attribute(
            attribute, template, ctx
        ),
        "signature": lambda self, attribute, template, ctx: self._parse_signature_attribute(
            attribute, template, ctx
        ),
        "hint": lambda self, attribute, template, ctx: self._parse_hint_attribute(
            attribute, template, ctx
        ),
        "padding-before": lambda self, attribute, template, ctx: self._parse_padding_before_attribute(
            attribute, template, ctx
        ),
        "padding-after": lambda self, attribute, template, ctx: self._parse_padding_after_attribute(
            attribute, template, ctx
        ),
        "boundary": lambda self, attribute, template, ctx: self._parse_boundary_attribute(
            attribute, template, ctx
        ),
    }

    CONVERTERS = {
        "leb128u": {
            "value_converter": LEB128UnsignedValueConverter,
            "value_provider": LEB128UnsignedBindingValueProvider,
        },
        "leb128size": {
            "value_converter": IdentityValueConverter,
            "value_provider": LEB128SizeBindingValueProvider,
        },
        "little": IntegerValueConverter("little"),
        "big": IntegerValueConverter("big"),
    }

    def __init__(self, template: str, data: Optional[bytes] = None):
        self._input_stream = antlr4.InputStream(template.strip())
        self._lexer = XMLLexer(self._input_stream)
        self._common_token_stream = antlr4.CommonTokenStream(self._lexer)
        self._parser = XMLParser(self._common_token_stream)
        self._parse_tree = self._parser.document()
        self._parse_tree_walker = antlr4.ParseTreeWalker()
        self._root = None
        self._templates = []
        self._data = data
        self._signature_property = None
        self._hint_property = None

    def parse(self):
        self._parse_tree_walker.walk(self, self._parse_tree)
        return self._root

    def enterElement(self, ctx):
        parent = None
        if self._templates:
            parent = self._templates[-1]

        template = self._parse_attributes(Template(), parent, ctx)

        if not parent:
            self._root = template
        else:
            parent._propagate_binding_context()

        self._templates.append(template)

    def exitElement(self, ctx):
        if self._templates:
            self._templates.pop()

    def _parse_attributes(self, template, parent, ctx):
        self._parse_sizing_attribute(template, ctx)

        for attribute_name, attribute_func in self.ATTRIBUTES.items():
            for attribute in ctx.attribute():
                if attribute_name == attribute.Name().getText():
                    attribute_func(self, attribute, template, ctx)

        template.parent = parent
        return template

    def _parse_name_attribute(self, attribute, template, ctx):
        if attribute.binding() is not None:
            raise RuntimeError("Using a reference for a name attribute is not allowed.")
        template.name = attribute.value().getText()[1:-1]

    def _parse_count_attribute(self, attribute, template, ctx):
        template.count_property = self._parse_attribute_value(attribute, template)

    def _parse_signature_attribute(self, attribute, template, ctx):
        self._signature_property = self._parse_signature_attribute_value(
            attribute, template
        )

    def _parse_hint_attribute(self, attribute, template, ctx):
        self._hint_property = self._parse_hint_attribute_value(attribute, template)

    def _parse_offset_attribute(self, attribute, template, ctx):
        offset_property = self._parse_attribute_value(attribute, template)
        addressing_mode = self._parse_addressing_mode_attribute(ctx)

        if addressing_mode == "absolute":
            template.offset_property = offset_property
        elif addressing_mode == "relative":
            if isinstance(offset_property, ReferenceProperty):
                reference_name = offset_property.value_provider.reference_name
                template.offset_property = RelativeOffsetReferenceProperty(
                    template, reference_name
                )
            else:
                template.offset_property = RelativeOffsetValueProperty(
                    template, ignore_boundary=True
                )
                template.offset_property.value = offset_property.value
        else:
            raise RuntimeError("Expected 'absolute' or 'relative'.")

    def _parse_addressing_mode_attribute(self, ctx):
        for attribute in ctx.attribute():
            if attribute.Name().getText() == "addressing-mode":
                return attribute.value().getText()[1:-1]
        return self.DEFAULT_ADDRESSING_MODE

    def _parse_size_attribute(self, attribute, template, ctx):
        template.size_property = self._parse_attribute_value(attribute, template)

    def _parse_sizing_attribute(self, template, ctx):
        sizing = self.DEFAULT_SIZING
        for attribute in ctx.attribute():
            if attribute.Name().getText() == "sizing":
                sizing = attribute.value().getText()[1:-1]

        if sizing == "fix":
            template.size_property = ValueProperty()
        elif sizing == "auto":
            template.size_property = AutoSizeValueProperty(template)
        elif sizing == "stretch":
            template.size_property = StretchSizeProperty(template)
        else:
            raise RuntimeError("Expected 'auto', 'fix' or 'stretch'.")

    def _parse_boundary_attribute(self, attribute, template, ctx):
        template.boundary_property = self._parse_attribute_value(attribute, template)

    def _parse_padding_before_attribute(self, attribute, template, ctx):
        template.padding_before_property = self._parse_attribute_value(
            attribute, template
        )

    def _parse_padding_after_attribute(self, attribute, template, ctx):
        template.padding_after_property = self._parse_attribute_value(
            attribute, template
        )

    def _parse_hint_attribute_value(self, attribute, template):
        return ValueProperty()

    def _parse_signature_attribute_value(self, attribute, template):
        hex_str = attribute.value().getText()[3:-1]
        return bytes.fromhex(hex_str)

    def _parse_attribute_value(self, attribute, template):
        if attribute.value() is not None:
            value = int(attribute.value().getText()[1:-1], base=0)
            return ValueProperty(value, template=template)

        if attribute.binding() is not None:
            return self._parse_attribute_value_reference(attribute, template)

        return ValueProperty()

    def _parse_attribute_value_reference(self, attribute, template):
        reference = None
        value_converter = IntegerValueConverter()
        names = attribute.binding().sequence().BRACKET_NAME()

        if not "name" in names:
            name = names[0].getText()
            if not name == "byteorder" and not name == "converter":
                reference = name

        for i, name in enumerate(names):
            if name.getText() == "name":
                reference = names[i + 1].getText()
            elif name.getText() == "byteorder":
                byteorder = names[i + 1].getText()
                value_converter = IntegerValueConverter(byteorder)
            elif name.getText() == "converter":
                converter_name = names[i + 1].getText()
                value_converter = self.CONVERTERS[converter_name]["value_converter"]()
                value_provider = self.CONVERTERS[converter_name]["value_provider"](
                    template
                )

        if reference:
            return ReferenceProperty(template, reference, value_converter)
        else:
            return PropertyBase(
                template=template,
                value_provider=value_provider,
                value_converter=value_converter,
            )
