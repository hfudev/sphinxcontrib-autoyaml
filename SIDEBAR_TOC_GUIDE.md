# How to Make YAML Keys Appear in Sidebar

## The Problem

When using `autoyaml_use_method_directive = True`, YAML keys become method directives like `.. method:: deploy_docs_production`, which don't appear in the sidebar/TOC.

## Solution: Use Manual Sections

To make YAML keys appear in the sidebar, you need to create section headings manually in your RST file.

### Option 1: Section Headings with autoyaml (Recommended)

Create a section for each major configuration area, then use autoyaml within it:

```rst
Configuration
=============

.. toctree::
   :maxdepth: 2

Deploy Documentation
--------------------

.. autoyaml:: templates/idf/deploy-docs.yml

Preview Documentation
---------------------

.. autoyaml:: templates/idf/preview-docs.yml
```

**Result**: "Deploy Documentation" and "Preview Documentation" appear in sidebar, with YAML keys underneath.

### Option 2: Individual Sections for Each Key

If you want each YAML key in the sidebar, create sections manually and reference the YAML for documentation:

```rst
Configuration Reference
=======================

deploy_docs_production
----------------------

.. autoyaml:: templates/idf/deploy-docs.yml
   :key: deploy_docs_production

Or document it manually:

Deploys documentation to production server.

**Variables:**

- :envvar:`DOCS_PROD_DEPLOY_KEY`
- :envvar:`DOCS_PROD_SERVER`
```

**Note**: The `:key:` option doesn't exist yet (see Option 3 below).

### Option 3: Use Definition Lists (Default Behavior)

If you don't need cross-referencing, use the default definition list mode:

```python
# conf.py
autoyaml_use_method_directive = False  # or omit this line
```

Then structure your RST:

```rst
Configuration Keys
==================

.. autoyaml:: templates/idf/deploy-docs.yml
```

With definition lists, you can wrap them in sections:

```rst
Deploy Jobs
-----------

.. autoyaml:: deploy-jobs.yml

Build Jobs
----------

.. autoyaml:: build-jobs.yml
```

**Result**: "Deploy Jobs" and "Build Jobs" appear in sidebar, with YAML keys as definition list items underneath.

## Comparison

| Approach | Sidebar Entry | Cross-reference | Index Entry |
|----------|---------------|-----------------|-------------|
| Method directives | ✗ No | ✓ Yes (`:meth:`) | ✓ Yes |
| Section headings | ✓ Yes | ✓ Yes (`:ref:`) | ✗ No |
| Definition lists | ✗ No | ✗ No | ✗ No |
| Sections + methods | ✓ Yes (section) | ✓ Yes (`:ref:` or `:meth:`) | ✓ Yes |

## Recommended Structure

For the best of both worlds (sidebar + cross-references + index):

```rst
CI/CD Pipeline Configuration
=============================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Deploy to Production
--------------------

.. autoyaml:: templates/idf/deploy-docs.yml

This section contains production deployment configurations.

Cross-reference: Use :ref:`Deploy to Production` to reference this section,
or :meth:`deploy_docs_production` to reference the specific method.
```

With this structure:
- ✓ "Deploy to Production" appears in sidebar
- ✓ YAML keys appear as methods under it
- ✓ Both section and methods can be cross-referenced
- ✓ Methods appear in index

## Why Method Directives Don't Appear in Sidebar

This is standard Sphinx behavior. Method directives (like `.. method::`, `.. function::`, `.. class::`) are part of the **Python domain** and appear in:
- The general index (genindex.html)
- Object inventory (for cross-referencing)
- Search results

But NOT in:
- Sidebar navigation
- `.. contents::` directive
- `.. toctree::` entries

This is by design - method directives are meant to document API elements, not create document structure.

## Quick Example

**Your RST file** (`index.rst`):

```rst
CI/CD Configuration
===================

.. toctree::
   :maxdepth: 2

Documentation Deployment
------------------------

.. autoyaml:: templates/idf/deploy-docs.yml
```

**Your conf.py**:

```python
extensions = ["sphinxcontrib.autoyaml"]
autoyaml_use_method_directive = True
```

**Result**:
- Sidebar shows: "CI/CD Configuration" > "Documentation Deployment"
- Page shows: deploy_docs_production() method under "Documentation Deployment"
- You can reference with: `:ref:`Documentation Deployment`` or `:meth:`deploy_docs_production``

## Advanced: Multiple Files

```rst
CI/CD Pipeline
==============

.. toctree::
   :maxdepth: 2
   :caption: Pipeline Stages

Build Stage
-----------

.. autoyaml:: templates/idf/build.yml

Test Stage
----------

.. autoyaml:: templates/idf/test.yml

Deploy Stage
------------

.. autoyaml:: templates/idf/deploy.yml
```

Each section ("Build Stage", "Test Stage", "Deploy Stage") appears in sidebar with its YAML methods underneath.
