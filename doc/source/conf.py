"""Sphinx configuration for PrismQ module documentation."""

import os
import sys

# Add project source to path for autodoc
sys.path.insert(0, os.path.abspath('../../src'))

# Project information
project = 'PrismQ Module Template'
copyright = '2025, PrismQ'
author = 'PrismQ'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
]

# Templates path
templates_path = ['_templates']

# Exclude patterns
exclude_patterns = []

# HTML output options
html_theme = 'alabaster'
html_static_path = ['_static']
