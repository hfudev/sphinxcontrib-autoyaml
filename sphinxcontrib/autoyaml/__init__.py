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
        """Generate documentation using sections and function directives."""
        sections = []
        unvisited = [tree]
        
        while len(unvisited) > 0:
            node = unvisited[-1]
            if len(node.children) > 0:
                unvisited.append(node.remove_child())
                continue
            if node.parent is None or node.comment is None:
                unvisited.pop()
                continue
            
            # Create a section for this YAML key
            section = nodes.section()
            section['ids'] = [nodes.make_id(node.value.value)]
            
            # Add title heading
            title_text = node.value.value
            title = nodes.title()
            title += nodes.Text(title_text)
            section += title
            
            # Build ViewList for the function directive
            viewlist = ViewList()
            
            # Get source info from the original comment
            if isinstance(node.comment, ViewList):
                source_file = node.comment.source(0) if len(node.comment) > 0 else "<autoyaml>"
            else:
                source_file = "<autoyaml>"
            
            line_num = 0
            
            # Add function directive
            viewlist.append(f".. function:: {node.value.value}", source_file, line_num)
            viewlist.append("", source_file, line_num)
            
            # Add comment content with proper indentation
            if isinstance(node.comment, ViewList):
                for i, line in enumerate(node.comment):
                    src, lineno = node.comment.info(i)
                    viewlist.append(f"   {line}", src, lineno)
            
            # Extract variables/parameters from the node
            variables_info = self._extract_variables(node)
            if variables_info:
                viewlist.append("", source_file, line_num)
                for var_name, var_value in variables_info.items():
                    # Add parameter documentation
                    param_line = f"   :param {var_name}:"
                    if var_value:
                        if isinstance(var_value, str):
                            param_line += f" {var_value}"
                    viewlist.append(param_line, source_file, line_num)
            
            # Parse the ViewList content into the section
            with switch_source_input(self.state, viewlist):
                self.state.nested_parse(viewlist, 0, section)
            
            # Store the section
            node.comment = section
            
            # Accumulate sections in parent
            if node.parent.comment is None:
                node.parent.comment = []
            elif isinstance(node.parent.comment, ViewList) and node.parent.value is not None:
                # Parent has its own comment - create section for it too
                parent_section = nodes.section()
                parent_section['ids'] = [nodes.make_id(node.parent.value.value)]
                
                parent_title_text = node.parent.value.value
                parent_title = nodes.title()
                parent_title += nodes.Text(parent_title_text)
                parent_section += parent_title
                
                # Add parent's function directive
                parent_viewlist = ViewList()
                parent_source = node.parent.comment.source(0) if len(node.parent.comment) > 0 else "<autoyaml>"
                parent_viewlist.append(f".. function:: {node.parent.value.value}", parent_source, 0)
                parent_viewlist.append("", parent_source, 0)
                
                for i, line in enumerate(node.parent.comment):
                    src, lineno = node.parent.comment.info(i)
                    parent_viewlist.append(f"   {line}", src, lineno)
                
                with switch_source_input(self.state, parent_viewlist):
                    self.state.nested_parse(parent_viewlist, 0, parent_section)
                
                node.parent.comment = [parent_section]
            
            if isinstance(node.parent.comment, list):
                node.parent.comment.append(section)
            
            unvisited.pop()
        
        # Return all sections
        if isinstance(tree.comment, list):
            return tree.comment
        return []
    
    def _extract_variables(self, node):
        """Extract variables from a YAML node to create parameter documentation."""
        variables = {}
        
        # Look for a 'variables' child node
        for child in node.children:
            if child.value and hasattr(child.value, 'value') and child.value.value == 'variables':
                # This is the variables section
                for var_child in child.children:
                    if var_child.value and hasattr(var_child.value, 'value'):
                        var_name = var_child.value.value
                        # Try to get the variable's value/description
                        var_value = None
                        if hasattr(var_child.value, 'end_mark'):
                            # Could extract default value here if needed
                            var_value = ""
                        variables[var_name] = var_value
        
        return variables

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
                # If docs is a list (new approach), yield each node individually
                if isinstance(docs, list):
                    for node in docs:
                        yield node
                else:
                    # Old-style single node
                    yield docs


def setup(app):
    app.add_directive("autoyaml", AutoYAMLDirective)
    app.add_config_value("autoyaml_root", "..", "env")
    app.add_config_value("autoyaml_doc_delimiter", "###", "env")
    app.add_config_value("autoyaml_comment", "#", "env")
    app.add_config_value("autoyaml_level", 1, "env")
    # Set to false to preserve backward compatibility.
    app.add_config_value("autoyaml_safe_loader", False, "env")
