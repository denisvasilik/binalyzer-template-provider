# -*- coding: utf-8 -*-
"""
    binalyzer_template_provider.xml
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Template providers are used to create a template tree from a description.

    :copyright: 2020 Denis Vasilík
    :license: MIT
"""
import antlr4
import logging

from binalyzer_core import (
    ByteOrder,
    AddressingMode,
    ValueProperty,
    ReferenceProperty,
    Sizing,
    Template,
)

from .generated import XMLParserListener, XMLLexer, XMLParser


_log = logging.getLogger("binalyzer")
_log.setLevel(logging.DEBUG)


def create_input_stream(filepath):
    with open(filepath, "r") as template_file:
        return antlr4.InputStream(template_file.read())


class XMLTemplateParser(XMLParserListener):

    DEFAULT_ADDRESSING_MODE = AddressingMode.Relative
    DEFAULT_SIZING = Sizing.Auto

    ATTRIBUTES = {
        "name": lambda self, attribute, template: self._parse_name_attribute(
            attribute, template
        ),
        "addressing-mode": lambda self, attribute, template: self._parse_addressing_mode_attribute(
            attribute, template
        ),
        "sizing": lambda self, attribute, template: self._parse_sizing_attribute(
            attribute, template
        ),
        "size": lambda self, attribute, template: self._parse_size_attribute(
            attribute, template
        ),
        "offset": lambda self, attribute, template: self._parse_offset_attribute(
            attribute, template
        ),
        "boundary": lambda self, attribute, template: self._parse_boundary_attribute(
            attribute, template
        ),
        "padding-before": lambda self, attribute, template: self._parse_padding_before_attribute(
            attribute, template
        ),
        "padding-after": lambda self, attribute, template: self._parse_padding_after_attribute(
            attribute, template
        ),
    }

    def __init__(self, xml_template):
        self._input_stream = antlr4.InputStream(xml_template.strip())
        self._lexer = XMLLexer(self._input_stream)
        self._common_token_stream = antlr4.CommonTokenStream(self._lexer)
        self._parser = XMLParser(self._common_token_stream)
        self._parse_tree = self._parser.document()
        self._parse_tree_walker = antlr4.ParseTreeWalker()
        self._root = None
        self._elements = []

    def parse(self):
        self._parse_tree_walker.walk(self, self._parse_tree)
        return self._root

    def enterElement(self, ctx):
        parent = None
        if self._elements:
            parent = self._elements[-1]
        element = self._parse_template_attributes(Template(), parent, ctx)
        self._elements.append(element)
        if parent:
            element.parent = parent
        else:
            self._root = element

    def exitElement(self, ctx):
        if self._elements:
            self._elements.pop()

    def _parse_template_attributes(self, template, parent, ctx):
        for attribute_name, attribute_func in self.ATTRIBUTES.items():
            for attribute in ctx.attribute():
                if attribute_name == attribute.Name().getText():
                    attribute_func(self, attribute, template)
        template.parent = parent
        return template

    def _parse_name_attribute(self, attribute, template):
        template.name = attribute.value().getText()[1:-1]

    def _parse_size_attribute(self, attribute, template):
        template.size_property = self._parse_attribute_value(attribute, template)

    def _parse_boundary_attribute(self, attribute, template):
        boundary_property = self._parse_attribute_value(attribute, template)

        if not isinstance(template.size, ValueProperty) and not template.children:
            template.size = ValueProperty(boundary_property.value)

        template.boundary_property = boundary_property

    def _parse_addressing_mode_attribute(self, attribute):
        addressing_mode = AddressingMode(attribute.value().getText()[1:-1])

    def _parse_sizing_attribute(self, attribute, template):
        sizing = Sizing(attribute.value().getText()[1:-1])

    def _parse_padding_before_attribute(self, attribute, template):
        padding_before_property = self._parse_attribute_value(attribute, template)

    def _parse_padding_after_attribute(self, attribute, template):
        padding_after_property = self._parse_attribute_value(attribute, template)

    def _parse_attribute_value(self, attribute, template):
        attribute_name = attribute.Name().getText()

        if attribute.value() is not None:
            _log.debug("Parse value of attribute %s", attribute_name)
            value = int(attribute.value().getText()[1:-1], base=0)
            return ValueProperty(value, template=template)

        if attribute.binding() is not None:
            _log.debug("Parse attribute reference of %s", attribute_name)
            names = attribute.binding().sequence().BRACKET_NAME()
            reference_name = names[0].getText()  # mandatory
            template.byte_order = ByteOrder.LittleEndian  # optional
            if len(names) > 1 and names[1].getText() == "ByteOrder":
                template.byte_order = ByteOrder(names[2].getText())  # mandatory
            return ReferenceProperty(template, reference_name)

        return ValueProperty()


class XMLTemplateFileParser(XMLTemplateParser):
    def __init__(self, filepath):
        self.template_filepath = filepath
        self.input_stream = create_input_stream(self.template_filepath)
        super(XMLTemplateFileParser, self).__init__(self.input_stream)
