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

.. envvar:: DEPLOY_STABLE

   Flag to indicate stable deployment to production.

Documentation Deployment
------------------------

This section describes the documentation deployment jobs.

.. autoyaml:: templates/idf/deploy-docs.yml

The :meth:`deploy_docs_production` method deploys documentation to production
using environment variables like :envvar:`DOCS_PROD_DEPLOY_KEY`.
