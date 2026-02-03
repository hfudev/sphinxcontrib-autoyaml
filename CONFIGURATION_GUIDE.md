# Configuration Guide for sphinxcontrib-autoyaml

## Quick Start

To use the `autoyaml_use_method_directive` option (or any other configuration option), you need to set it in your Sphinx project's **`conf.py`** file.

## Step-by-Step Configuration

### 1. Locate your conf.py file

Your Sphinx project should have a `conf.py` file, typically in the root of your documentation directory (e.g., `docs/conf.py` or `doc/source/conf.py`).

### 2. Add the extension

First, ensure the extension is added to your extensions list:

```python
# conf.py

extensions = [
    "sphinxcontrib.autoyaml",
    # ... other extensions ...
]
```

### 3. Add configuration options

After the extensions list, add any configuration options you want to use. All options are optional and have default values.

#### Example 1: Enable Method Directive Mode

```python
# conf.py

extensions = ["sphinxcontrib.autoyaml"]

# Enable method directive mode
autoyaml_use_method_directive = True
```

#### Example 2: Complete Configuration

```python
# conf.py

extensions = ["sphinxcontrib.autoyaml"]

# Autoyaml configuration
autoyaml_root = ".."                      # Where to look for YAML files
autoyaml_doc_delimiter = "###"            # Comment delimiter for docs
autoyaml_comment = "#"                    # Regular comment character
autoyaml_level = 0                        # Parse all nested levels (0 = unlimited)
autoyaml_safe_loader = True               # Use SafeLoader for security
autoyaml_use_method_directive = True      # Use method directives
```

### 4. Use in your documentation

Once configured, use the `autoyaml` directive in your `.rst` files:

```rst
Configuration Reference
=======================

.. autoyaml:: config.yml
```

## Configuration Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `autoyaml_root` | string | `".."` | Directory path (relative to conf.py) where YAML files are located |
| `autoyaml_doc_delimiter` | string | `"###"` | Character(s) that start a documentation comment |
| `autoyaml_comment` | string | `"#"` | Character(s) that start regular comments |
| `autoyaml_level` | int | `1` | How many levels deep to parse nested structures (0 = unlimited) |
| `autoyaml_safe_loader` | bool | `False` | Whether to use YAML SafeLoader for security |
| `autoyaml_use_method_directive` | bool | `False` | Render YAML keys as `.. method::` directives instead of definition lists |

## Common Issues

### "Where do I set autoyaml_use_method_directive?"

Set it in your `conf.py` file, after the `extensions` list:

```python
extensions = ["sphinxcontrib.autoyaml"]
autoyaml_use_method_directive = True
```

### "The configuration isn't working"

1. Make sure you're editing the correct `conf.py` file (the one Sphinx uses to build your docs)
2. Ensure there are no typos in the option name
3. Rebuild your documentation completely: `make clean && make html`
4. Check for error messages during the build

### "Can I use different settings for different files?"

No, configuration options apply globally to all `.. autoyaml::` directives in your project. If you need different behavior, consider using separate Sphinx projects.
