.. _engine implementations:

======================
Engine Implementations
======================

.. contents::
   :depth: 2
   :local:
   :backlinks: entry


.. toctree::
   :caption: Framework Components
   :maxdepth: 2

   enginelib
   engines
   engine_overview


ResultList and engines
======================

.. autoclass:: aperion.result_types.ResultList

.. autoclass:: aperion.result_types.EngineResults


Engine Types
============

The :py:obj:`engine_type <aperion.enginelib.Engine.engine_type>` of an engine
determines which :ref:`search processor <aperion.search.processors>` is used by
the engine.

In this section a list of the engines that are documented is given, a complete
list of the engines can be found in the source under: :origin:`aperion/engines`.

.. _online engines:

Online Engines
--------------

.. sidebar:: info

   - :py:obj:`processors.online <aperion.search.processors.online>`

.. toctree::
   :maxdepth: 1
   :glob:

   demo/demo_online
   xpath
   mediawiki
   json_engine

.. toctree::
   :maxdepth: 1
   :glob:

   online/*

.. _offline engines:

Offline Engines
---------------

.. sidebar:: info

   - :py:obj:`processors.offline <aperion.search.processors.offline>`

.. toctree::
   :maxdepth: 1
   :glob:

   offline_concept
   demo/demo_offline
   offline/*

.. _online url search:

Online URL Search
-----------------

.. sidebar:: info

   - :py:obj:`processors.online_url_search <aperion.search.processors.online_url_search>`

.. toctree::
   :maxdepth: 1
   :glob:

   online_url_search/*

.. _online currency:

Online Currency
---------------

.. sidebar:: info

   - :py:obj:`processors.online_currency <aperion.search.processors.online_currency>`

*no engine of this type is documented yet / coming soon*

.. _online dictionary:

Online Dictionary
-----------------

.. sidebar:: info

   - :py:obj:`processors.online_dictionary <aperion.search.processors.online_dictionary>`

*no engine of this type is documented yet / coming soon*
