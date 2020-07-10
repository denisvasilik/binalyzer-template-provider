"""
    binalyzer_template_provider.extension
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements the Binalyzer Template Provider extension.
"""
import io

from typing import Optional
from binalyzer_core import BinalyzerExtension

from .xml import XMLTemplateParser


class XMLTemplateProviderExtension(BinalyzerExtension):
    def __init__(self, binalyzer=None):
        super(XMLTemplateProviderExtension, self).__init__(binalyzer, "xml")

    def init_extension(self):
        super(XMLTemplateProviderExtension, self).init_extension()

    def from_file(self, template_file_path: str, data_file_path: Optional[str] = None):
        template_text = ""
        with open(template_file_path, "r") as template_file:
            template_text = template_file.read()

        data = io.BytesIO()
        if data_file_path:
            with open(data_file_path, "rb") as data_file:
                data = io.BytesIO(data_file.read())

        self.parse(template_text, data)

    def parse(self, text: str, data: Optional[io.IOBase] = None):
        template = XMLTemplateParser(text, data).parse()
        if data:
            self.binalyzer.data = data
        self.binalyzer.template = template
        return template