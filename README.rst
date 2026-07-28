.. SPDX-License-Identifier: AGPL-3.0-or-later

----

.. figure:: https://burhanuddin-1.github.io/svg/
   :target: https://docs.aperion.org/
   :alt: Aperion Search
   :width: 100%
   :align: center

----

Privacy-respecting, hackable `metasearch engine`_

https://Aperion-Search.onrender.com/ lists ready-to-use running instances.

A user_, admin_ and developer_ handbook is available on the homepage_.

|Install|
|Homepage|
|Wiki|
|AGPL License|
|Issues|
|commits|
|weblate|
|aperion logo|

----

.. _Aperion Search: https://Aperion-Search.onrender.com/
.. _user: https://Aperion-Search.onrender.com/user
.. _admin: https://Aperion-Search.onrender.com/admin
.. _developer: https://Aperion-Search.onrender.com/dev
.. _homepage: https://Aperion-Search.onrender.com/
.. _metasearch engine: https://en.wikipedia.org/wiki/Metasearch_engine

.. |Aperion Search logo| image:: "C:\Users\lenov\AppData\Aperion-Search\aperion\static\themes\simple\img\aperion.svg"
   :target: https://Aperion-Search.onrender.com/
   :width: 5%

.. |Install| image:: https://img.shields.io/badge/-install-blue
   :target: https://Aperion-Search.onrender.com/admin/installation.html

.. |Homepage| image:: https://img.shields.io/badge/-homepage-blue
   :target: https://Aperion-Search.onrender.com/

.. |Wiki| image:: https://img.shields.io/badge/-wiki-blue
   :target: https://github.com/burhanuddin-1/s/wiki

.. |AGPL License|  image:: https://img.shields.io/badge/license-AGPL-blue.svg
   :target: https://github.com/aperion/aperion/blob/master/LICENSE

.. |Issues| image:: https://img.shields.io/github/issues/aperion/aperion?color=yellow&label=issues
   :target: https://github.com/burhanuddin-1/s/issues

.. |PR| image:: https://img.shields.io/github/issues-pr-raw/aperion/aperion?color=yellow&label=PR
   :target: https://github.com/aperion/aperion/pulls

.. |commits| image:: https://img.shields.io/github/commit-activity/y/aperion/aperion?color=yellow&label=commits
   :target: https://github.com/aperion/aperion/commits/master

.. |weblate| image:: https://translate.codeberg.org/widgets/aperion/-/aperion/svg-badge.svg
   :target: https://translate.codeberg.org/projects/aperion/


Contact
=======

Ask questions or chat with the aperion community (this not a chatbot) on

IRC
  `#aperion on libera.chat <https://web.libera.chat/?channel=#aperion>`_
  which is bridged to Matrix.

Matrix
  `#aperion:matrix.org <https://matrix.to/#/#aperion:matrix.org>`_


Setup
=====

- A well maintained `Docker image`_, also built for ARM64 and ARM/v7
  architectures.
- Alternatively there are *up to date* `installation scripts`_.
- For individual setup consult our detailed `Step by step`_ instructions.
- To fine-tune your instance, take a look at the `Administrator documentation`_.

.. _Administrator documentation: https://docs.aperion.org/admin/index.html
.. _Step by step: https://docs.aperion.org/admin/installation-aperion.html
.. _installation scripts: https://docs.aperion.org/admin/installation-scripts.html
.. _Docker image: https://github.com/aperion/aperion-docker

Translations
============

.. _Weblate: https://translate.codeberg.org/projects/aperion/aperion/

Help translate aperion at `Weblate`_

.. figure:: https://translate.codeberg.org/widgets/aperion/-/multi-auto.svg
   :target: https://translate.codeberg.org/projects/aperion/


Contributing
============

.. _development quickstart: https://docs.aperion.org/dev/quickstart.html
.. _developer documentation: https://docs.aperion.org/dev/index.html

Are you a developer?  Have a look at our `development quickstart`_ guide, it's
very easy to contribute.  Additionally we have a `developer documentation`_.


Codespaces
==========

You can contribute from your browser using `GitHub Codespaces`_:

- Fork the repository
- Click on the ``<> Code`` green button
- Click on the ``Codespaces`` tab instead of ``Local``
- Click on ``Create codespace on master``
- VSCode is going to start in the browser
- Wait for ``git pull && make install`` to appear and then disappear
- You have `120 hours per month`_ (see also your `list of existing Codespaces`_)
- You can start aperion using ``make run`` in the terminal or by pressing ``Ctrl+Shift+B``

.. _GitHub Codespaces: https://docs.github.com/en/codespaces/overview
.. _120 hours per month: https://github.com/settings/billing
.. _list of existing Codespaces: https://github.com/codespaces
