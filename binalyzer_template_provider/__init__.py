# -*- coding: utf-8 -*-
"""
    binalyzer_template_provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Template provider for Binalyzer.

    :copyright: 2020 Denis Vasilík
    :license: MIT, see LICENSE for details.
"""

name = "binalyzer_template_provider"

__tag__ = ""
__build__ = 0
__version__ = "{}".format(__tag__)
__commit__ = "0000000"

from .extension import XMLTemplateProviderExtension
from .xml import XMLTemplateParser, XMLTemplateFileParser
