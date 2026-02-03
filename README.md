# sphinxcontrib-autoyaml

This Sphinx autodoc extension documents YAML files from comments. Documentation
is returned as reST definitions, e.g.:

This document:

```yaml
###
# Enable Nginx web server.
enable_nginx: true

###
# Enable Varnish caching proxy.
enable_varnish: true
```

would be turned into text:

```rst
enable_nginx

   Enable Nginx web server.

enable_varnish

   Enable Varnish caching proxy.
```

Alternatively, with `autoyaml_use_method_directive = True`, YAML keys can be
rendered as Sphinx `.. method::` directives, allowing them to be cross-referenced
and appear in the domain index:

```rst
.. method:: enable_nginx

   Enable Nginx web server.

.. method:: enable_varnish

   Enable Varnish caching proxy.
```

See `tests/examples/output/*.yml` and `tests/examples/output/*.txt` for
more examples.

`autoyaml` will take into account only comments which first line starts with
`autoyaml_doc_delimiter`.

## Installing

Issue command:

```sh
pip install sphinxcontrib-autoyaml
```

And add the extension in your Sphinx project's ``conf.py`` file:

```python
extensions = ["sphinxcontrib.autoyaml"]
```

## Configuration

All configuration options are set in your Sphinx project's ``conf.py`` file. After adding the extension to the ``extensions`` list, you can configure the extension by adding any of the options below:

```python
# conf.py

# Add the extension
extensions = ["sphinxcontrib.autoyaml"]

# Configure autoyaml (all options are optional)
autoyaml_root = ".."                           # Default: ".."
autoyaml_doc_delimiter = "###"                 # Default: "###"
autoyaml_comment = "#"                         # Default: "#"
autoyaml_level = 1                             # Default: 1
autoyaml_safe_loader = False                   # Default: False
autoyaml_use_method_directive = False          # Default: False
```

### Configuration Options Explained

- **`autoyaml_root`**: Directory path (relative to conf.py) where YAML files are located
- **`autoyaml_doc_delimiter`**: Character(s) that start a documentation comment
- **`autoyaml_comment`**: Character(s) that start regular comments
- **`autoyaml_level`**: How many levels deep to parse nested structures (0 = unlimited)
- **`autoyaml_safe_loader`**: Whether to use YAML SafeLoader for security
- **`autoyaml_use_method_directive`**: Render YAML keys as `.. method::` directives instead of definition lists

### Method Directive Mode

When `autoyaml_use_method_directive` is set to `True` in your `conf.py`, YAML keys are rendered as
Sphinx `.. method::` directives instead of definition list terms. This provides
several advantages:

1. **Cross-referencing**: Keys can be referenced from other parts of documentation
2. **Domain index**: Keys appear in the Python domain index
3. **Better integration**: Works with Sphinx's standard documentation tools

To enable this mode, add to your `conf.py`:

```python
autoyaml_use_method_directive = True
```

In this mode, you can use standard Sphinx cross-reference syntax in your YAML
comments, such as `:envvar:`MY_VAR`` to reference environment variables.

Example:

```yaml
###
# API configuration
api:
  ###
  # The API key to use. Configure via :envvar:`API_KEY`.
  api_key: "default"
```

This will generate:

```rst
.. method:: api

   API configuration

   .. method:: api_key

      The API key to use. Configure via :envvar:`API_KEY`.
```

## Usage

You can use the `autoyaml` directive in your reStructuredText files to extract and document
YAML files:

```rst
Some title
==========

Documenting single YAML file.

.. autoyaml:: some_yml_file.yml
```

## Caveats

### Mapping keys nested in sequences

Sequences are traversed as well, but they are not represented in output
documentation. This extension focuses only on documenting mapping keys. It means
that structure like this:

```yaml
key:
  ###
  # comment1
  - - inner_key1: value
      ###
      # comment2
      inner_key2: value
  ###
  # comment3
  - inner_key3: value
```

will be flattened, so it will appear as though inner keys exist directly under
`key`. Duplicated key documentation will be duplicated in output as well. See
`tests/examples/output/comment-in-nested-sequence.txt` and
`tests/examples/output/comment-in-nested-sequence.yml` to get a better
understanding how sequences are processed.

### Complex mapping keys

YAML allows for complex mapping keys like so:

```yaml
[1, 2]: value
```

These kind of keys won't be documented in output, because it's unclear how they
should be represented as a string.

### Flow-style entries

YAML allows writing complex data structures in single line like JSON.
Documentation is generated only for the first key in such entry, so this:

```yaml
###
# comment
key: {key1: value, key2: value, key3: value}
```

would yield documentation only for `key`.
