# -- Project information -----------------------------------------------------
project = 'SlyMastodon for Python'
copyright = '2023, Dunkyl 🔣🔣'
author = 'Dunkyl 🔣🔣'

# -- General configuration ---------------------------------------------------
templates_path = ['_templates']
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']

extensions = [
    'myst_parser',
    'sphinxcontrib_trio',
    'sphinx_copybutton',
    'sphinxext.opengraph',
    'sphinx.ext.autodoc',
    'sphinx.ext.duration',
    'sphinx.ext.autosummary',
]
myst_enable_extensions = ["colon_fence"]


# -- Options for HTML output -------------------------------------------------
html_theme = 'furo'
html_static_path = ['_static']
html_title = "SlyMastodon for Python"
