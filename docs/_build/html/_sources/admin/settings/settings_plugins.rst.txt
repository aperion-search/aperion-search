.. _settings plugins:

============
``plugins:``
============

.. attention::

   The ``enabled_plugins:`` section in aperion's settings no longer exists.
   There is no longer a distinction between built-in and external plugin, all
   plugins are registered via the settings in the ``plugins:`` section.

.. sidebar:: Further reading ..

   - :ref:`plugins admin`
   - :ref:`dev plugin`

In aperion, plugins can be registered in the :py:obj:`PluginStore
<aperion.plugins.PluginStorage>` via a fully qualified class name.

A configuration (:py:obj:`PluginCfg <aperion.plugins.PluginCfg>`) can be
transferred to the plugin, e.g. to activate it by default / *opt-in* or
*opt-out* from user's point of view.

Please note that some plugins, such as the :ref:`hostnames plugin` plugin,
require further configuration before they can be made available for selection.

By default the :ref:`settings built in plugins` are loaded.  To change the list
of plugins to be loaded, the value for ``plugins:`` in
``/etc/aperion/settings.yml`` must be overwritten.

Following is an example that uses :ref:`settings use_default_settings` and only
two plugins are registered: the calculator can be activated by the user and the
unit converter is active by default.


.. code:: yaml

    use_default_settings: true

    plugins:

      aperion.plugins.calculator.SXNGPlugin:
        active: false

      aperion.plugins.unit_converter.SXNGPlugin:
        active: true

To prevent any plugins from loading, the following setting can be used:

.. code:: yaml

    use_default_settings: true

    plugins: {}


.. _settings built in plugins:

built-in plugins
================

The built-in plugins are all located in the namespace `aperion.plugins`.

.. code:: yaml

    plugins:

      aperion.plugins.calculator.SXNGPlugin:
        active: true

      aperion.plugins.hash_plugin.SXNGPlugin:
        active: true

      aperion.plugins.self_info.SXNGPlugin:
        active: true

      aperion.plugins.tracker_url_remover.SXNGPlugin:
        active: true

      aperion.plugins.unit_converter.SXNGPlugin:
        active: true

      aperion.plugins.ahmia_filter.SXNGPlugin:
        active: true

      aperion.plugins.hostnames.SXNGPlugin:
        active: true

      aperion.plugins.oa_doi_rewrite.SXNGPlugin:
        active: false

      aperion.plugins.tor_check.SXNGPlugin:
        active: false


.. _settings external_plugins:

external plugins
================

.. _Only show green hosted results:
   https://github.com/return42/tgwf-aperion-plugins/

aperion supports *external plugins* / there is no need to install one, aperion
runs out of the box.

- `Only show green hosted results`_
- ..
