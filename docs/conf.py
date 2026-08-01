# SPDX-License-Identifier: AGPL-3.0-or-later

import  sys, os
from pathlib import Path
from pallets_sphinx_themes import ProjectLink
from types import SimpleNamespace as _NS
from typing import Any as _Any

# Ensure Windows build works before importing any aperion modules that may
# require POSIX-only deps (uvloop, pwd, grp)
import types as _types
_uvloop = sys.modules.setdefault('uvloop', _types.ModuleType('uvloop'))
if not hasattr(_uvloop, 'install'):
    # Silencing type checker; at runtime this is fine
    setattr(_uvloop, 'install', (lambda: None))  # type: ignore[attr-defined]
if os.name == 'nt':
    sys.modules.setdefault('pwd', _types.ModuleType('pwd'))
    sys.modules.setdefault('grp', _types.ModuleType('grp'))

# Try importing aperion metadata; provide fallbacks if not available
try:
    from aperion import get_setting
    from aperion.version import VERSION_STRING, GIT_URL, GIT_BRANCH
except Exception:
    def get_setting(name, default=None):
        return default
    VERSION_STRING = "0.0.0"
    GIT_URL = ""
    GIT_BRANCH = ""

# Project --------------------------------------------------------------

project = 'Aperion Search'
copyright = 'Aperion Search team'
author = 'Aperion Search team'
release, version = VERSION_STRING, VERSION_STRING
aperion_URL = get_setting('server.base_url') or 'https://example.org/aperion'
ISSUE_URL = get_setting('brand.issue_url') or ''
DOCS_URL = get_setting('brand.docs_url') or ''
PUBLIC_INSTANCES = get_setting('brand.public_instances') or ''
PRIVACYPOLICY_URL = get_setting('general.privacypolicy_url') or ''
CONTACT_URL = get_setting('general.contact_url') or ''
WIKI_URL = get_setting('brand.wiki_url') or ''

SOURCEDIR = Path(__file__).parent.parent / "aperion"
os.environ['SOURCEDIR'] = str(SOURCEDIR)

# hint: sphinx.ext.viewcode won't highlight when 'highlight_language' [1] is set
#       to string 'none' [2]
#
# [1] https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html
# [2] https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-highlight_language

highlight_language = 'default'

# General --------------------------------------------------------------

master_doc = "index"
source_suffix = '.rst'
numfig = True

exclude_patterns = ['build-templates/*.rst', 'user/*.md']

DOCS_MINIMAL = os.getenv('DOCS_MINIMAL', '1' if os.name == 'nt' else '0') == '1'

if not DOCS_MINIMAL:
    import aperion.engines
    import aperion.plugins
    import aperion.webutils
    # import aperion.webapp is needed to init the engines & plugins, to init a
    # (empty) secret_key is needed.
    from aperion import settings as _Aperion_settings
    _Aperion_settings['server']['secret_key'] = ''
    import aperion.webapp
    aperion.engines.load_engines(_Aperion_settings['engines'])
else:
    # Provide minimal dummies so docs can build without full app
    aperion: _Any = _NS()
    aperion.engines = _NS()
    aperion.plugins = _NS()
    aperion.webutils = _NS()
    aperion.engines.engines = {}
    aperion.engines.categories = {}
    aperion.plugins.STORAGE = {}
    def _group_engines_in_tab(x):
        return x
    aperion.webutils.group_engines_in_tab = _group_engines_in_tab

_categories_as_tabs = {}
if not DOCS_MINIMAL:
    from aperion import settings as _Aperion_settings
    _cat_tabs = _Aperion_settings.get('categories_as_tabs', [])
    _categories_as_tabs = {c: getattr(aperion.engines, 'categories', {}).get(c, []) for c in _cat_tabs}

jinja_contexts = {
    'aperion': {
        'engines': getattr(aperion.engines, 'engines', {}),
        'plugins': getattr(aperion.plugins, 'STORAGE', {}),
        'version': {
            'node': os.getenv('NODE_MINIMUM_VERSION')
        },
        'enabled_engine_count': sum((not getattr(x, 'disabled', False)) for x in getattr(aperion.engines, 'engines', {}).values()) if getattr(aperion.engines, 'engines', None) else 0,
        'categories': getattr(aperion.engines, 'categories', {}),
        'categories_as_tabs': _categories_as_tabs,
    },
}
jinja_filters = {
    'group_engines_in_tab': aperion.webutils.group_engines_in_tab,
}

# Let the Jinja template in configured_engines.rst access documented_modules
# to automatically link documentation for modules if it exists.
def setup(app):
    ENGINES_DOCNAME = 'user/configured_engines'

    def before_read_docs(app, env, docnames):
        assert ENGINES_DOCNAME in docnames
        docnames.remove(ENGINES_DOCNAME)
        docnames.append(ENGINES_DOCNAME)
        # configured_engines must come last so that sphinx already has
        # discovered the python module documentations

    def source_read(app, docname, source):
        if docname == ENGINES_DOCNAME:
            jinja_contexts['aperion']['documented_modules'] = app.env.domains['py'].modules

    app.connect('env-before-read-docs', before_read_docs)
    app.connect('source-read', source_read)

# usage::   lorem :patch:`f373169` ipsum
extlinks = {}

# upstream links
extlinks['wiki'] = ('https://github.com/aperion/aperion/wiki/%s', ' %s')
extlinks['pull'] = ('https://github.com/aperion/aperion/pull/%s', 'PR %s')
extlinks['pull-aperion'] = ('https://github.com/aperion/aperion/pull/%s', 'PR %s')

# links to custom brand
extlinks['origin'] = (GIT_URL + '/blob/' + GIT_BRANCH + '/%s', 'git://%s')
extlinks['patch'] = (GIT_URL + '/commit/%s', '#%s')
extlinks['docs'] = (DOCS_URL + '/%s', 'docs: %s')
extlinks['pypi'] = ('https://pypi.org/project/%s', 'PyPi: %s')
extlinks['man'] = ('https://manpages.debian.org/jump?q=%s', '%s')
#extlinks['role'] = (
#    'https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html#role-%s', '')
extlinks['duref'] = (
    'https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#%s', '%s')
extlinks['durole'] = (
    'https://docutils.sourceforge.io/docs/ref/rst/roles.html#%s', '%s')
extlinks['dudir'] =  (
    'https://docutils.sourceforge.io/docs/ref/rst/directives.html#%s', '%s')
extlinks['ctan'] =  (
    'https://ctan.org/pkg/%s', 'CTAN: %s')

extensions = [
    'sphinx.ext.imgmath',
    'sphinx.ext.extlinks',
    'sphinx.ext.viewcode',
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "pallets_sphinx_themes",
    "sphinx_issues", # https://github.com/sloria/sphinx-issues/blob/master/README.rst
    "sphinx_jinja",  # https://github.com/tardyp/sphinx-jinja
    "sphinxcontrib.programoutput",  # https://github.com/NextThought/sphinxcontrib-programoutput
    'linuxdoc.kernel_include',  # Implementation of the 'kernel-include' reST-directive.
    'linuxdoc.rstFlatTable',    # Implementation of the 'flat-table' reST-directive.
    'linuxdoc.kfigure',         # Sphinx extension which implements scalable image handling.
    "sphinx_tabs.tabs", # https://github.com/djungelorm/sphinx-tabs
    'myst_parser',  # https://www.sphinx-doc.org/en/master/usage/markdown.html
    'notfound.extension',  # https://github.com/readthedocs/sphinx-notfound-page
]

# autodoc_typehints = "description"
autodoc_default_options = {
    'member-order': 'bysource',
}

myst_enable_extensions = [
  "replacements", "smartquotes"
]

suppress_warnings = ['myst.domains']

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "babel" : ("https://babel.readthedocs.io/en/latest/", None),
    "flask": ("https://flask.palletsprojects.com/en/stable/", None),
    "flask_babel": ("https://python-babel.github.io/flask-babel/", None),
    "werkzeug": ("https://werkzeug.palletsprojects.com/en/stable/", None),
    "jinja": ("https://jinja.palletsprojects.com/en/stable/", None),
    "linuxdoc" : ("https://return42.github.io/linuxdoc/", None),
    "sphinx" : ("https://www.sphinx-doc.org/en/master/", None),
    "valkey": ('https://valkey-py.readthedocs.io/en/stable/', None),
}

issues_github_path = "aperion/aperion"

# HTML -----------------------------------------------------------------

# Ensure 404 links are relative
notfound_urls_prefix = ''

sys.path.append(os.path.abspath('_themes'))
sys.path.insert(0, os.path.abspath("../"))
html_theme_path = ['_themes']
html_theme = "aperion"

# sphinx.ext.imgmath setup
html_math_renderer = 'imgmath'
imgmath_image_format = 'svg'
imgmath_font_size = 14
# sphinx.ext.imgmath setup END

html_show_sphinx = False
html_theme_options = {"index_sidebar_logo": True}
html_context = {"project_links": [] }
html_context["project_links"].append(ProjectLink("Source", GIT_URL + '/tree/' + GIT_BRANCH))

if WIKI_URL:
    html_context["project_links"].append(ProjectLink("Wiki", WIKI_URL))
if PUBLIC_INSTANCES:
    html_context["project_links"].append(ProjectLink("Public instances", PUBLIC_INSTANCES))
if ISSUE_URL:
    html_context["project_links"].append(ProjectLink("Issue Tracker", ISSUE_URL))
if PRIVACYPOLICY_URL:
    html_context["project_links"].append(ProjectLink("Privacy Policy", PRIVACYPOLICY_URL))
if CONTACT_URL:
    html_context["project_links"].append(ProjectLink("Contact", CONTACT_URL))

html_sidebars = {
    "**": [
        "globaltoc.html",
        "project.html",
        "relations.html",
        "searchbox.html",
        "sourcelink.html"
    ],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html"]}
html_logo = "../aperion/static/themes/simple/img/aperion.png"
html_title = "Aperion Search Documentation ({})".format(VERSION_STRING)
html_show_sourcelink = True

# LaTeX ----------------------------------------------------------------

latex_documents = [
    (master_doc, "aperion-{}.tex".format(VERSION_STRING), html_title, author, "manual")
]
