Bitbucket Issues Migration
===========================

.. image:: https://travis-ci.org/RonnyPfannschmidt/bitbucket_issue_migration.svg?branch=master
    :target: https://travis-ci.org/RonnyPfannschmidt/bitbucket_issue_migration

This is a small script that will migrate issues to a github project.

It will use the bitbucket api to pull out the issues and comments.

It will import issues (and close them as needed) and their comments. Labels and
milestones are not supported at the moment.
