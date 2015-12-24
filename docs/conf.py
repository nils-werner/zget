# -*- coding: utf-8 -*-
import sys
import os

execfile('../zget/utils.py')

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
else:
    html_theme = 'default'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.pngmath',
    'sphinxcontrib.napoleon',
    'sphinx.ext.autosummary',
    'numpydoc'
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'zget'
copyright = u'2015, Nils Werner'

version = __version__
release = __version__

exclude_patterns = ['_build']

pygments_style = 'sphinx'

html_static_path = ['_static']

htmlhelp_basename = 'zgetdoc'

latex_elements = {
}

latex_documents = [
    ('index', 'zget.tex', u'zget Documentation',
     u'Nils Werner', 'manual'),
]

man_pages = [
    ('index', 'zget', u'zget Documentation',
     [u'Nils Werner'], 1)
]

texinfo_documents = [
    ('index', 'zget', u'zget Documentation',
     u'Nils Werner', 'zget',
     'Zeroconf based peer to peer file transfer',
     'Miscellaneous'),
]

numpydoc_show_class_members = False
