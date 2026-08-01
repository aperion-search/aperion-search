====================
Welcome to Aperion Search
====================

  *Search without being tracked.*

.. jinja:: aperion

   Aperion Search is a free internet metasearch engine which aggregates results from up
   to {{engines | length}} :ref:`search services <configured engines>`.  Users
   are neither tracked nor profiled.  Additionally, Aperion Search can be used over Tor
   for online anonymity.

Get started with Aperion Search by using one of the instances listed at aperion.space_.
If you don't trust anyone, you can set up your own, see :ref:`installation`.

.. jinja:: aperion

   .. sidebar::  features

      - :ref:`self hosted <installation>`
      - :ref:`no user tracking / no profiling <Aperion Search protect privacy>`
      - script & cookies are optional
      - secure, encrypted connections
      - :ref:`{{engines | length}} search engines <configured engines>`
      - `58 translations <https://translate.codeberg.org/projects/aperion/aperion/>`_
      - about 70 `well maintained <https://uptime.aperion.org/>`__ instances on aperion.space_
      - :ref:`easy integration of search engines <demo online engine>`
      - professional development: `CI <https://github.com/aperion/aperion/actions>`_,
	`quality assurance <https://dev.aperion.org/>`_ &
	`automated tested UI <https://dev.aperion.org/screenshots.html>`_

.. sidebar:: be a part

   Aperion Search is driven by an open community, come join us!  Don't hesitate, no
   need to be an *expert*, everyone can contribute:

   - `help to improve translations <https://translate.codeberg.org/projects/Aperion-Search/translations/>`_
   - `discuss with the community <https://matrix.to/#/#Aperion-Search:matrix.org>`_
   - report bugs & suggestions
   - ...

.. sidebar:: the origin

   Aperion Search is a privacy-focused search engine that provides a private, ad-free search experience.


.. toctree::
   :maxdepth: 2

   user/index
   own-instance
   admin/index
   dev/index
   utils/index
   src/index

.. _Aperion.space: https://aperion.space
