.. _Aperion.search:

======
Search
======

.. autoclass:: aperion.search.EngineRef
  :members:

.. autoclass:: aperion.search.SearchQuery
  :members:

.. autoclass:: aperion.search.Search

  .. attribute:: search_query
    :type: aperion.search.SearchQuery

  .. attribute:: result_container
    :type: aperion.results.ResultContainer

  .. automethod:: search() -> aperion.results.ResultContainer

.. autoclass:: aperion.search.SearchWithPlugins
  :members:

  .. attribute:: search_query
    :type: aperion.search.SearchQuery

  .. attribute:: result_container
    :type: aperion.results.ResultContainer

  .. attribute:: ordered_plugin_list
    :type: typing.List

  .. attribute:: request
    :type: flask.request

  .. automethod:: search() -> aperion.results.ResultContainer
