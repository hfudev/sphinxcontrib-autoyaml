# sphinxcontrib-autoyaml

This Sphinx autodoc extension documents YAML files from comments.

## Output Format

Each YAML key is rendered as:
1. **Section heading** (H2/H3) - appears in TOC/sidebar
2. **Function directive** - for cross-referencing
3. **Parameters** - extracted from `variables` section with default values

### Example

This document:

```yaml
###
# Deploy documentation to production server.
deploy_docs_production:
  stage: post_deploy
  variables:
    TYPE: "preview"
    DOCS_DEPLOY_KEY: "$PROD_KEY"
```

would be rendered as:

**In TOC/Sidebar:**
```
deploy_docs_production
```

**On Page:**
```rst
deploy_docs_production
^^^^^^^^^^^^^^^^^^^^^^

deploy_docs_production()

   Deploy documentation to production server.
   
   Parameters:
      • TYPE -- (default: "preview")
      • DOCS_DEPLOY_KEY -- (default: "$PROD_KEY")
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
```

### Configuration Options

- **`autoyaml_root`**: Directory path (relative to conf.py) where YAML files are located
- **`autoyaml_doc_delimiter`**: Character(s) that start a documentation comment
- **`autoyaml_comment`**: Character(s) that start regular comments
- **`autoyaml_level`**: How many levels deep to parse nested structures (0 = unlimited)
- **`autoyaml_safe_loader`**: Whether to use YAML SafeLoader for security

## Features

### Automatic TOC Integration

YAML keys automatically appear in the table of contents as section headings. No manual RST structure needed!

### Function Directives

Each YAML key gets a `.. function::` directive for cross-referencing:

```rst
See :func:`deploy_docs_production` for details.
```

### Parameter Extraction

Variables defined in a YAML `variables` section are automatically extracted as function parameters with default values:

```yaml
###
# Deploy documentation
deploy_docs_production:
  variables:
    TYPE: "preview"
    DEPLOY_KEY: "$PROD_KEY"
```

Renders as:

```rst
Parameters:
   • TYPE -- (default: "preview")
   • DEPLOY_KEY -- (default: "$PROD_KEY")
```

### Cross-References

You can use standard Sphinx cross-reference syntax in your YAML comments:

```yaml
###
# Configure via :envvar:`API_KEY` environment variable.
api_config:
  key: "default"
```

## Usage

Use the `autoyaml` directive in your reStructuredText files:

```rst
CI/CD Pipeline
==============

.. autoyaml:: gitlab-ci.yml
```

This will generate section headings for each YAML key, making them automatically appear in your documentation's table of contents and sidebar navigation.

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
