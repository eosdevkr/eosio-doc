import sys
import os

extensions = []
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'EOSIO'
copyright = u'2018, block.one'
version = '1.4'
release = '1.4.0'
language = 'ko'
html_title = 'EOSIO'

exclude_patterns = ['_build']
html_static_path = ['_static']

import guzzle_sphinx_theme
html_translator_class = 'guzzle_sphinx_theme.HTMLTranslator'
html_theme_path = guzzle_sphinx_theme.html_theme_path()
html_theme = 'guzzle_sphinx_theme'

html_sidebars = {
    '**': ['logo-text.html', 'globaltoc.html', 'searchbox.html']
}

extensions.append("guzzle_sphinx_theme")

html_theme_options = {
}

def setup(app):
    app.add_stylesheet('theme_overrides.css')
