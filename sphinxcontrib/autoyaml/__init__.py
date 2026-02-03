import os

from ruamel.yaml.nodes import (
    MappingNode,
    SequenceNode,
    ScalarNode,
)
from ruamel.yaml import SafeLoader, Loader
from docutils.statemachine import ViewList
from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx.util import logging
from sphinx.util.docutils import switch_source_input
from sphinx.errors import ExtensionError


logger = logging.getLogger(__name__)


class TreeNode:
    def __init__(self, value, comments, parent=None):
        self.value = value
        self.parent = parent
        self.children = []
        self.comments = comments
        if value is None:
            self.comment = None
        else:
            # Flow-style entries may attempt to incorrectly reuse comments
            self.comment = self.comments.pop(self.value.start_mark.line + 1, None)

    def add_child(self, value):
        node = TreeNode(value, self.comments, self)
        self.children.append(node)
        return node

    def remove_child(self):
        return self.children.pop(0)


class AutoYAMLException(ExtensionError):

    category = "AutoYAML error"


class AutoYAMLDirective(Directive):

    required_arguments = 1

    def run(self):
        self.config = self.state.document.settings.env.config
        self.env = self.state.document.settings.env
        self.record_dependencies = self.state.document.settings.record_dependencies
        output_nodes = []
        location = os.path.normpath(
            os.path.join(
                self.env.srcdir, self.config.autoyaml_root + "/" + self.arguments[0]
            )
        )
        if os.path.isfile(location):
            logger.debug("[autoyaml] parsing file: %s", location)
            try:
                output_nodes.extend(self._parse_file(location))
            except Exception as e:
                raise AutoYAMLException(
                    "Failed to parse YAML file: %s" % (location)
                ) from e
        else:
            raise AutoYAMLException(
                '%s:%s: location "%s" is not a file.'
                % (
                    self.env.doc2path(self.env.docname, None),
                    self.content_offset - 1,
                    location,
                )
            )
        self.record_dependencies.add(location)
        return output_nodes

    def _get_comments(self, source, source_file):
        comments = {}
        in_docstring = False
        for linenum, line in enumerate(source.splitlines(), start=1):
            line = line.lstrip()
            if line.startswith(self.config.autoyaml_doc_delimiter):
                in_docstring = True
                comment = ViewList()
            elif line.startswith(self.config.autoyaml_comment) and in_docstring:
                line = line[len(self.config.autoyaml_comment) :]
                # strip preceding whitespace
                if line and line[0] == " ":
                    line = line[1:]
                comment.append(line, source_file, linenum)
            elif in_docstring:
                comments[linenum] = comment
                in_docstring = False
        return comments

    def _parse_document(self, doc, comments):
        tree = TreeNode(None, comments)
        if not isinstance(doc, MappingNode):
            return tree
        unvisited = [(doc, 0)]
        while len(unvisited) > 0:
            node, index = unvisited[-1]
            if index == len(node.value):
                # Only mapping nodes increase depth. Directly nested
                # sequences are flattened.
                if tree.parent is not None and (len(unvisited) == 1 or isinstance(unvisited[-2][0], MappingNode)):
                    tree = tree.parent
                unvisited.pop()
                continue
            for node_item in node.value[index:]:
                index += 1
                unvisited[-1] = (node, index)
                subtree = None
                node_key = None
                node_value = None
                if isinstance(node, SequenceNode):
                    node_value = node_item
                elif isinstance(node, MappingNode):
                    node_key, node_value = node_item
                    # Using complex structures for keys in YAML is possible as
                    # well, but it's currently not handled.
                    if not isinstance(node_key, ScalarNode):
                        continue
                    subtree = tree.add_child(node_key)
                for i in (node_key, node_value):
                    if isinstance(i, ScalarNode):
                        for i in range(i.start_mark.line, i.end_mark.line + 1):
                            comments.pop(i + 1, None)
                if isinstance(node_value, (MappingNode, SequenceNode)) and (
                    len(unvisited) + 1 <= self.config.autoyaml_level
                    or self.config.autoyaml_level == 0
                ):
                    unvisited.append((node_value, 0))
                    if subtree is not None:
                        tree = subtree
                    break
        return tree

    def _generate_documentation(self, tree):
        if self.config.autoyaml_use_method_directive:
            return self._generate_documentation_with_method_directive(tree)
        else:
            return self._generate_documentation_with_definition_list(tree)

    def _generate_documentation_with_definition_list(self, tree):
        """Original implementation using definition lists."""
        unvisited = [tree]
        while len(unvisited) > 0:
            node = unvisited[-1]
            if len(node.children) > 0:
                unvisited.append(node.remove_child())
                continue
            if node.parent is None or node.comment is None:
                unvisited.pop()
                continue
            with switch_source_input(self.state, node.comment):
                definition = nodes.definition()
                if isinstance(node.comment, ViewList):
                    self.state.nested_parse(node.comment, 0, definition)
                else:
                    definition += node.comment
                node.comment = nodes.definition_list_item(
                    "",
                    nodes.term("", node.value.value),
                    definition,
                )
                if node.parent.comment is None:
                    node.parent.comment = nodes.definition_list()
                elif not isinstance(node.parent.comment, nodes.definition_list):
                    with switch_source_input(self.state, node.parent.comment):
                        dlist = nodes.definition_list()
                        self.state.nested_parse(node.parent.comment, 0, dlist)
                        node.parent.comment = dlist
                node.parent.comment += node.comment
            unvisited.pop()
        return tree.comment

    def _generate_documentation_with_method_directive(self, tree):
        """New implementation using method directives."""
        unvisited = [tree]
        # Track which nodes have been converted to method directives
        converted = set()
        
        while len(unvisited) > 0:
            node = unvisited[-1]
            if len(node.children) > 0:
                unvisited.append(node.remove_child())
                continue
            if node.parent is None or node.comment is None:
                unvisited.pop()
                continue
            
            # Skip creating method directive if already converted, but still append to parent
            if id(node) not in converted:
                # Build ViewList for method directive
                method_viewlist = ViewList()
                
                # Get source info from the original comment
                if isinstance(node.comment, ViewList):
                    source_file = node.comment.source(0) if len(node.comment) > 0 else "<autoyaml>"
                else:
                    source_file = "<autoyaml>"
                
                # Add method directive line
                line_num = 0
                method_viewlist.append(f".. method:: {node.value.value}", source_file, line_num)
                method_viewlist.append("", source_file, line_num)
                
                # Add comment content with proper indentation
                if isinstance(node.comment, ViewList):
                    for i, line in enumerate(node.comment):
                        # Add 3 spaces for indentation (standard for directive content)
                        src, lineno = node.comment.info(i)
                        method_viewlist.append(f"   {line}", src, lineno)
                
                # Store as ViewList for now
                node.comment = method_viewlist
                converted.add(id(node))
            
            # Get source file for blank lines
            if isinstance(node.comment, ViewList):
                source_file = node.comment.source(0) if len(node.comment) > 0 else "<autoyaml>"
            else:
                source_file = "<autoyaml>"
            
            # Handle parent's comment
            if node.parent.comment is None:
                node.parent.comment = ViewList()
            elif isinstance(node.parent.comment, ViewList) and id(node.parent) not in converted and node.parent.value is not None:
                # Parent has its own doc comment and hasn't been converted yet. Convert it to method directive.
                parent_method = ViewList()
                parent_source = node.parent.comment.source(0) if len(node.parent.comment) > 0 else "<autoyaml>"
                parent_method.append(f".. method:: {node.parent.value.value}", parent_source, 0)
                parent_method.append("", parent_source, 0)
                # Add parent's documentation
                for i, line in enumerate(node.parent.comment):
                    src, lineno = node.parent.comment.info(i)
                    parent_method.append(f"   {line}", src, lineno)
                # Blank line before children
                parent_method.append("", parent_source, 0)
                node.parent.comment = parent_method
                converted.add(id(node.parent))
            
            # Append this node's method directive to parent's ViewList
            # Child methods need to be indented by 3 spaces to be inside parent method
            if isinstance(node.parent.comment, ViewList):
                for i, line in enumerate(node.comment):
                    src, lineno = node.comment.info(i)
                    # Indent by 3 spaces if parent has a value (not root)
                    if node.parent.value is not None:
                        node.parent.comment.append(f"   {line}", src, lineno)
                    else:
                        node.parent.comment.append(line, src, lineno)
                node.parent.comment.append("", source_file, 0)  # Blank line after method
            
            unvisited.pop()
        
        # Parse the accumulated ViewList
        if tree.comment is not None and isinstance(tree.comment, ViewList):
            with switch_source_input(self.state, tree.comment):
                parsed_nodes = nodes.container()
                self.state.nested_parse(tree.comment, 0, parsed_nodes)
                return parsed_nodes
        return tree.comment

    def _compose_all(self, loader):
        try:
            while loader.check_node():
                yield loader._composer.get_node()
        finally:
            loader._parser.dispose()

    def _parse_file(self, source_file):
        with open(source_file, "r") as f:
            source = f.read()
        comments = self._get_comments(source, source_file)
        if self.config.autoyaml_safe_loader:
            loader = SafeLoader
        else:
            loader = Loader
        for doc in self._compose_all(Loader(source)):
            docs = self._generate_documentation(self._parse_document(doc, comments))
            if docs is not None:
                yield docs


def setup(app):
    app.add_directive("autoyaml", AutoYAMLDirective)
    app.add_config_value("autoyaml_root", "..", "env")
    app.add_config_value("autoyaml_doc_delimiter", "###", "env")
    app.add_config_value("autoyaml_comment", "#", "env")
    app.add_config_value("autoyaml_level", 1, "env")
    # Set to false to preserve backward compatibility.
    app.add_config_value("autoyaml_safe_loader", False, "env")
    app.add_config_value("autoyaml_use_method_directive", False, "env")
