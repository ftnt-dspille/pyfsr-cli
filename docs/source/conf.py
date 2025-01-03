# Configuration file for Sphinx documentation builder

import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
project = 'PyFSR CLI'
copyright = f'{datetime.now().year}, Fortinet'
author = 'Fortinet'

# The full version, including alpha/beta/rc tags
release = '0.2.2'
version = release

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',  # Core autodoc functionality
    'sphinx.ext.napoleon',  # Support for Google/NumPy docstring formats
    'sphinx.ext.viewcode',  # Add links to source code
    'sphinx.ext.intersphinx',  # Link to other projects' documentation
    'sphinx.ext.autosummary',  # Generate summary tables
    'sphinx_click',  # CLI documentation
    'autoapi.extension',  # Auto API documentation
    'sphinx_autodoc_typehints',  # Better type hint support
]

# AutoAPI configuration for automatic module documentation
autoapi_type = 'python'
autoapi_dirs = ['../../src/pyfsr_cli']
autoapi_add_toctree_entry = True
autoapi_template_dir = '_templates/autoapi'  # Custom templates if needed
autoapi_options = [
    'members',
    'undoc-members',
    'show-inheritance',
    'show-module-summary',
    'imported-members',
    'special-members',
]
autoapi_python_class_content = 'both'
autoapi_python_use_implicit_namespaces = True
autoapi_keep_files = True  # Keep generated files for debugging

# Autosummary configuration
autosummary_generate = True
autosummary_imported_members = True

# Napoleon settings for docstring parsing
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'click': ('https://click.palletsprojects.com/en/8.1.x/', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
}

# -- Options for HTML output -------------------------------------------------
html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/ftnt-dspille/pyfsr",
            "icon": "fab fa-github",
        }
    ],
    "use_edit_page_button": True,
    "show_toc_level": 2,
}

html_context = {
    "github_user": "ftnt-dspille",
    "github_repo": "pyfsr-cli",
    "github_version": "main",  # Or the branch name where docs are located
    "doc_path": "docs/source",  # Path to the documentation source files in the repo
}

# These folders are copied to the documentation's HTML output
html_static_path = ['_static']
templates_path = ['_templates']

# These paths are either relative to html_static_path or fully qualified paths (eg. https://...)
html_css_files = [
    'custom.css',
]

# -- Extension configuration ------------------------------------------------
# Autodoc configuration
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

# Don't show full module path
add_module_names = False


# Generate the command-line interface documentation
def setup(app):
    # Add custom CSS
    app.add_css_file('custom.css')
    # Any additional setup here
