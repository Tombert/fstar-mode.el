# -*- coding: utf-8 -*-

from sphinx.domains import Domain
from sphinx.util.osutil import relative_uri
from . import docutils4fstar

# Export here so config files can refer to just this module
LiterateFStarParser = docutils4fstar.LiterateFStarParser

class FStarDomain(Domain):
    """A domain to document F* code.

    Sphinx has a notion of “domains”, used to tailor it to a specific language.
    Domains mostly consist in descriptions of the objects that we wish to
    describe, as well as domain-specific roles and directives.

    Each domain is responsible for tracking its objects, and resolving
    references to them.
    """

    name = 'fstar'
    label = 'F*'

    object_types = dict() # ObjType (= directive type) → (Local name, *xref-roles)

    directives = dict() # Directive → Object

    roles = { # FIXME
        'type': docutils4fstar.FStarTypeRole
    }

    indices = []

    data_version = 1
    initial_data = {
        # Collect everything under a key that we control, since Sphinx adds
        # others, such as “version”
        'objects' : {}
    }


def unfold_folded_fst_blocks(_app, doctree, _fromdocname):
    for node in doctree.traverse(docutils4fstar.fst_node):
        node.replace_self(node.original_node)

def process_external_editor_references(app, doctree, fromdocname):
    """Adjust links to the external editor.
In HTML mode, set the refuri appropriately; in other modes, remove them."""
    for node in doctree.traverse(docutils4fstar.standalone_editor_reference_node):
        if app.buildername == "html":
            node['refuri'] = relative_uri(app.builder.get_target_uri(fromdocname), node['docpath'])
        else:
            node.parent.remove(node)

def register_fst_parser(app):
    app.config.source_parsers['.fst'] = 'fslit.sphinx4fstar.LiterateFStarParser'

def add_html_assets(app):
    app.config.html_static_path.append(docutils4fstar.ASSETS_PATH)

    app.add_javascript("https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.27.2/codemirror.min.js")
    app.add_stylesheet("https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.27.2/codemirror.min.css")

    app.add_javascript("fstar.cm.js")
    app.add_stylesheet("cm.tango.css")

    app.add_javascript("fslit.js")
    app.add_stylesheet("fslit.css")

def setup(app):
    """Register the F* domain"""

    app.add_domain(FStarDomain)

    for role in docutils4fstar.ROLES:
        app.add_role(role.role, role)

    for node in docutils4fstar.NODES:
        app.add_node(node,
                     html=(node.visit, node.depart),
                     latex=(node.visit, node.depart),
                     text=(node.visit, node.depart))

    for directive in docutils4fstar.DIRECTIVES:
        getattr(directive, "setup", lambda _: None)(app.srcdir)
        app.add_directive(directive.directive, directive)

    for transform in docutils4fstar.TRANSFORMS:
        app.add_transform(transform)

    if app.buildername == "html":
        app.connect('builder-inited', add_html_assets)
        app.connect('doctree-resolved', unfold_folded_fst_blocks)
    app.connect('builder-inited', register_fst_parser)
    app.connect('doctree-resolved', process_external_editor_references)

    return {'version': '0.1', "parallel_read_safe": True}
