.. _installation basic:

=========================
Step by step installation
=========================

.. contents::
   :depth: 2
   :local:
   :backlinks: entry


In this section we show the setup of a aperion instance that will be installed
by the :ref:`installation scripts`.

.. _install packages:

Install packages
================

.. kernel-include:: $DOCS_BUILD/includes/aperion.rst
   :start-after: START distro-packages
   :end-before: END distro-packages

.. hint::

   This installs also the packages needed by :ref:`aperion uwsgi`

.. _create aperion user:

Create user
===========

.. kernel-include:: $DOCS_BUILD/includes/aperion.rst
   :start-after: START create user
   :end-before: END create user

.. _aperion-src:

Install aperion & dependencies
==============================

Start a interactive shell from new created user and clone aperion:

.. kernel-include:: $DOCS_BUILD/includes/aperion.rst
   :start-after: START clone aperion
   :end-before: END clone aperion

In the same shell create *virtualenv*:

.. kernel-include:: $DOCS_BUILD/includes/aperion.rst
   :start-after: START create virtualenv
   :end-before: END create virtualenv

To install aperion's dependencies, exit the aperion *bash* session you opened above
and start a new one.  Before installing, check if your *virtualenv* was sourced
from the login (*~/.profile*):

.. kernel-include:: $DOCS_BUILD/includes/aperion.rst
   :start-after: START manage.sh update_packages
   :end-before: END manage.sh update_packages

.. tip::

   Open a second terminal for the configuration tasks and leave the ``(aperion)$``
   terminal open for the tasks below.


.. _use_default_settings.yml:

Configuration
=============

.. sidebar:: ``use_default_settings: True``

   - :ref:`settings.yml`
   - :ref:`settings location`
   - :ref:`settings use_default_settings`
   - :origin:`/etc/aperion/settings.yml <utils/templates/etc/aperion/settings.yml>`

To create a initial ``/etc/aperion/settings.yml`` we recommend to start with a
copy of the file :origin:`utils/templates/etc/aperion/settings.yml`.  This setup
:ref:`use default settings <settings use_default_settings>` from
:origin:`aperion/settings.yml` and is shown in the tab *"Use default settings"*
below. This setup:

- enables :ref:`limiter <limiter>` to protect against bots
- enables :ref:`image proxy <image_proxy>` for better privacy

Modify the ``/etc/aperion/settings.yml`` to your needs:

.. tabs::

  .. group-tab:: Use default settings

     .. literalinclude:: ../../utils/templates/etc/aperion/settings.yml
        :language: yaml
        :end-before: # preferences:

     To see the entire file jump to :origin:`utils/templates/etc/aperion/settings.yml`

  .. group-tab:: aperion/settings.yml

     .. literalinclude:: ../../aperion/settings.yml
        :language: yaml
        :end-before: # hostnames:

     To see the entire file jump to :origin:`aperion/settings.yml`

For a *minimal setup* you need to set ``server:secret_key``.

.. kernel-include:: $DOCS_BUILD/includes/aperion.rst
   :start-after: START aperion config
   :end-before: END aperion config


Check
=====

To check your aperion setup, optional enable debugging and start the *webapp*.
aperion looks at the exported environment ``$aperion_SETTINGS_PATH`` for a
configuration file.

.. kernel-include:: $DOCS_BUILD/includes/aperion.rst
   :start-after: START check aperion installation
   :end-before: END check aperion installation

If everything works fine, hit ``[CTRL-C]`` to stop the *webapp* and disable the
debug option in ``settings.yml``. You can now exit aperion user bash session (enter exit
command twice).  At this point aperion is not demonized; uwsgi allows this.
