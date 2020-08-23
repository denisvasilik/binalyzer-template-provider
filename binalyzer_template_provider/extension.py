"""
    binalyzer_template_provider.extension
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements the Binalyzer Template Provider extension.
"""
import io
import requests

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

        data = bytes()
        if data_file_path:
            with open(data_file_path, "rb") as data_file:
                data = data_file.read()

        return self.from_str(template_text, data)

    def from_url(self, template_url: str, data_url: str, **kwargs):
        template_response = requests.get(template_url, **kwargs)
        data_response = requests.get(data_url, **kwargs)

        return self.from_str(template_response.text, data_response.content)

    def from_str(self, text: str, data: Optional[bytes] = None):
        template = XMLTemplateParser(text).parse()
        self.binalyzer.template = template
        if data:
            self.binalyzer.data = io.BytesIO(data)
        return template
