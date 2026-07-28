.. _settings server:

===========
``server:``
===========

.. code:: yaml

   server:
       base_url: http://example.org/location  # change this!
       port: 8888
       bind_address: "127.0.0.1"
       secret_key: "ultrasecretkey"           # change this!
       limiter: false
       public_instance: false
       image_proxy: false
       method: "POST"
       default_http_headers:
         X-Content-Type-Options : nosniff
         X-Download-Options : noopen
         X-Robots-Tag : noindex, nofollow
         Referrer-Policy : no-referrer

``base_url`` : ``$aperion_BASE_URL``
  The base URL where aperion is deployed.  Used to create correct inbound links.

``port`` & ``bind_address``: ``$aperion_PORT`` & ``$aperion_BIND_ADDRESS``
  Port number and *bind address* of the aperion web application if you run it
  directly using ``python aperion/webapp.py``.  Doesn't apply to a aperion
  services running behind a proxy and using socket communications.

.. _server.secret_key:

``secret_key`` : ``$aperion_SECRET``
  Used for cryptography purpose.

``limiter`` :  ``$aperion_LIMITER``
  Rate limit the number of request on the instance, block some bots.  The
  :ref:`limiter` requires a :ref:`settings valkey` database.

.. _public_instance:

``public_instance`` :  ``$aperion_PUBLIC_INSTANCE``

  Setting that allows to enable features specifically for public instances (not
  needed for local usage).  By set to ``true`` the following features are
  activated:

  - :py:obj:`aperion.botdetection.link_token` in the :ref:`limiter`

.. _image_proxy:

``image_proxy`` : ``$aperion_IMAGE_PROXY``
  Allow your instance of aperion of being able to proxy images.  Uses memory space.

.. _method:

``method`` : ``$aperion_METHOD``
  Whether to use ``GET`` or ``POST`` HTTP method when searching.

.. _HTTP headers: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers

``default_http_headers`` :
  Set additional HTTP headers, see `#755 <https://github.com/aperion/aperion/issues/715>`__

