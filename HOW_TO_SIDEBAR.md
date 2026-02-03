# How to Make deploy_docs_production Appear in Sidebar

## Your Question

> "if i have .. autoyaml:: templates/idf/deploy-docs.yml it shows the deploy_docs_production in the side bar"

## Quick Answer

To make `deploy_docs_production` appear in the sidebar, wrap it in a **section heading**:

```rst
Documentation Deployment
------------------------

.. autoyaml:: templates/idf/deploy-docs.yml
```

**Result:**
- ✅ "Documentation Deployment" appears in sidebar
- ✅ `deploy_docs_production()` method appears under it on the page
- ✅ Both can be cross-referenced

## Complete Example

Here's your `index.rst` file:

```rst
CI/CD Pipeline Configuration
=============================

.. toctree::
   :maxdepth: 2
   :caption: Pipeline Stages

Environment Variables
---------------------

.. envvar:: DOCS_PROD_DEPLOY_KEY

   SSH private key for deploying to the production documentation server.

.. envvar:: DOCS_PROD_SERVER

   Hostname of the production documentation server.

.. envvar:: DOCS_PROD_SERVER_USER

   Username for SSH access to the production documentation server.

.. envvar:: DOCS_PROD_PATH

   Directory path on the production documentation server for storing documentation.

Documentation Deployment
------------------------

This section contains the production deployment configuration.

.. autoyaml:: templates/idf/deploy-docs.yml

The :meth:`deploy_docs_production` job deploys documentation to production
using :envvar:`DOCS_PROD_DEPLOY_KEY` and :envvar:`DOCS_PROD_SERVER`.
```

## Your conf.py

```python
# conf.py

extensions = ["sphinxcontrib.autoyaml"]

# Enable method directive mode for cross-referencing
autoyaml_use_method_directive = True
```

## What You'll See

### In the Sidebar/TOC:
```
CI/CD Pipeline Configuration
├─ Environment Variables
├─ Documentation Deployment
```

### On the Page (under "Documentation Deployment"):
```
Documentation Deployment
------------------------

This section contains the production deployment configuration.

deploy_docs_production()

   Deploy documentation to production server.

   Deploys the full built documentation to the production server for 
   protected branches and tags (master, release branches, and version tags).

   Variables:

   DOCS_PROD_DEPLOY_KEY [link]
   DOCS_PROD_SERVER [link]
   DOCS_PROD_SERVER_USER [link]
   DOCS_PROD_PATH [link]
```

## Why This Works

- **Section headings** (`Documentation Deployment`) create TOC entries and appear in sidebar
- **Method directives** (`deploy_docs_production()`) provide cross-referencing and index entries
- **Combined** gives you both sidebar visibility and cross-reference functionality

## Alternative: Multiple Sections

If you want each configuration area in the sidebar:

```rst
CI/CD Pipeline
==============

Build Documentation
-------------------

.. autoyaml:: templates/idf/build-docs.yml

Test Documentation
------------------

.. autoyaml:: templates/idf/test-docs.yml

Deploy Documentation
--------------------

.. autoyaml:: templates/idf/deploy-docs.yml
```

Sidebar shows:
```
CI/CD Pipeline
├─ Build Documentation
├─ Test Documentation
└─ Deploy Documentation
```

## Cross-Referencing

Once set up, you can reference from anywhere:

```rst
See :ref:`Documentation Deployment` for production deployment.

The :meth:`deploy_docs_production` method uses :envvar:`DOCS_PROD_DEPLOY_KEY`.
```

## Important Note

Method directives (like `.. method:: deploy_docs_production`) **do not** create sidebar entries themselves. This is standard Sphinx behavior for all Python domain directives (method, function, class, etc.).

To get sidebar entries, you **must** use section headings.

## Summary

✅ **What you asked for:**
- YAML file: `templates/idf/deploy-docs.yml`
- Want: `deploy_docs_production` in sidebar

✅ **Solution:**
- Create section: "Documentation Deployment" (appears in sidebar)
- Add `.. autoyaml::` under it
- Methods appear on page, section appears in sidebar

✅ **Benefits:**
- Sidebar navigation ✓
- Cross-referencing ✓
- Index entries ✓
- Envvar links ✓
