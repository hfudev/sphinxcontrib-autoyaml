# Method Directive Feature - Complete Working Example

## Summary

The `autoyaml_use_method_directive` feature is **WORKING CORRECTLY**. Here's what it does:

### ✅ What Works

1. **YAML keys rendered as method directives** - Keys like `deploy_docs_production` become `.. method:: deploy_docs_production`
2. **Cross-references work** - You can reference methods with `:meth:`deploy_docs_production``
3. **Envvar cross-references work** - `:envvar:`DOCS_PROD_DEPLOY_KEY`` in YAML comments becomes clickable links
4. **Appears in general index** - Methods appear in the generated index (genindex.html)
5. **Python domain integration** - Methods are part of the Python domain and get proper styling

### 📋 How to Use

#### 1. Configure in conf.py

```python
# conf.py

extensions = ["sphinxcontrib.autoyaml"]

# Enable method directive mode
autoyaml_use_method_directive = True
```

#### 2. Create your YAML file with documentation

```yaml
###
#
# Deploy documentation to production server.
#
# Deploys the full built documentation to the production server.
#
# **Variables**
#
# :envvar:`DOCS_PROD_DEPLOY_KEY`
# :envvar:`DOCS_PROD_SERVER`
#
deploy_docs_production:
  stage: post_deploy
  variables:
    TYPE: "preview"
```

#### 3. Define envvar references in your RST file

```rst
Configuration
=============

Environment Variables
---------------------

.. envvar:: DOCS_PROD_DEPLOY_KEY

   SSH private key for deploying to the production documentation server.

.. envvar:: DOCS_PROD_SERVER

   Hostname of the production documentation server.

YAML Configuration
------------------

.. autoyaml:: config.yml

Using the Configuration
-----------------------

You can reference the :meth:`deploy_docs_production` method in your documentation.
```

#### 4. Build your documentation

```bash
cd docs
make clean
make html
```

## Results

### What You'll See in HTML

1. **Method Directive**:
   ```html
   <dl class="py method">
     <dt id="deploy_docs_production">
       <span class="sig-name">deploy_docs_production</span>()
     </dt>
     <dd>
       <p>Deploy documentation to production server.</p>
     </dd>
   </dl>
   ```

2. **Envvar Cross-References** (clickable links):
   - `DOCS_PROD_DEPLOY_KEY` → links to `#envvar-DOCS_PROD_DEPLOY_KEY`
   - `DOCS_PROD_SERVER` → links to `#envvar-DOCS_PROD_SERVER`

3. **Method Cross-References**:
   - `:meth:`deploy_docs_production`` → links to `#deploy_docs_production`

4. **In the Index**:
   - `deploy_docs_production()` appears in genindex.html with a link

### What You'll See in Text Output

```
Configuration
*************

deploy_docs_production()

   Deploy documentation to production server.

   Deploys the full built documentation to the production server.

   **Variables**

   "DOCS_PROD_DEPLOY_KEY" "DOCS_PROD_SERVER"
```

## About "TOC" (Table of Contents)

**Important**: Method directives do NOT create section headings, so they won't appear in a `.. contents::` directive or sidebar TOC.

However, they:
- ✅ Appear in the **general index** (genindex.html)
- ✅ Can be **cross-referenced** from anywhere
- ✅ Are **searchable** in the documentation
- ✅ Appear **under their section heading** in the structure

If you want methods to appear in TOC, put them under a section:

```rst
Configuration Keys
------------------

.. autoyaml:: config.yml
```

Then "Configuration Keys" will appear in TOC, and the methods will be listed under it in the rendered page.

## Test Results

All tests pass (22/22), including:
- `test_gitlab_ci_example` - Your exact scenario
- `test_envvar_reference` - Envvar cross-references
- `test_simple_method_directive` - Basic method directives
- `test_nested_method_directive` - Nested YAML structures

## Common Issues and Solutions

### "I don't see my method in the TOC"

**Expected behavior**: Methods don't create TOC entries. They appear:
- In the general index
- Under their section heading in the page
- As cross-reference targets

### "Cross-references aren't working"

Make sure:
1. You defined the envvar with `.. envvar:: NAME`
2. You're using `:envvar:`NAME`` (with backticks) in YAML comments
3. You rebuild completely: `make clean && make html`

### "I get 'unknown target' warnings"

1. Ensure envvar definitions come before or in the same file as the autoyaml directive
2. Check spelling of envvar names
3. Use `:envvar:`NAME`` not `:env:`NAME`` or other variants

## Verification Commands

### Check if method directive is in HTML:
```bash
grep -o 'id="deploy_docs_production"' docs/_build/html/index.html
```

### Check if envvar cross-references work:
```bash
grep -o 'href="#envvar-DOCS_PROD_DEPLOY_KEY"' docs/_build/html/index.html
```

### Check if method appears in index:
```bash
grep -o 'deploy_docs_production' docs/_build/html/genindex.html
```

## Example Project Structure

```
docs/
├── conf.py                          # autoyaml_use_method_directive = True
├── index.rst                        # Main doc with envvar definitions
├── config/
│   └── gitlab-ci.yml               # YAML file with ### comments
└── _build/
    └── html/
        ├── index.html              # deploy_docs_production() method
        └── genindex.html           # deploy_docs_production in index
```

## Conclusion

The feature is **working as designed**. All functionality is operational:
- ✅ Method directives generated
- ✅ Cross-references work
- ✅ Envvar references work
- ✅ Appears in index
- ✅ Can be referenced

The only thing to understand is that methods don't create TOC entries (by design in Sphinx), but they do appear in the index and under their section heading on the page.
