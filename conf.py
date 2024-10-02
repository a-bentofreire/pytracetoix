# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
project = 'PyTraceToIX'
copyright = '2024 Alexandre Bento Freire'
author = 'Alexandre Bento Freire'
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx.ext.viewcode']
templates_path = ['_templates']
include_patterns = ['*.rst', '*.py']
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
