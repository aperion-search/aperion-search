.. _architecture:

============
Architecture
============

.. sidebar:: Further reading

   - Reverse Proxy: :ref:`Apache <apache aperion site>` & :ref:`nginx <nginx
     aperion site>`
   - uWSGI: :ref:`aperion uwsgi`
   - aperion: :ref:`installation basic`

Herein you will find some hints and suggestions about typical architectures of
aperion infrastructures.

.. _architecture uWSGI:

uWSGI Setup
===========

We start with a *reference* setup for public aperion instances which can be build
up and maintained by the scripts from our :ref:`toolboxing`.

.. _arch public:

.. kernel-figure:: arch_public.dot
   :alt: arch_public.dot

   Reference architecture of a public aperion setup.

The reference installation activates ``server.limiter`` and
``server.image_proxy`` (:origin:`/etc/aperion/settings.yml
<utils/templates/etc/aperion/settings.yml>`)

.. literalinclude:: ../../utils/templates/etc/aperion/settings.yml
   :language: yaml
   :end-before: # preferences:
