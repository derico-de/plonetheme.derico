Adding and updating locales
---------------------------

For every language you want to translate into you need a
locales/[language]/LC_MESSAGES/plonetheme.derico.po
(e.g. locales/de/LC_MESSAGES/plonetheme.derico.po)

For German

.. code-block:: console

    $ mkdir de

For updating locales

.. code-block:: console

    $ ./bin/update_locale

Note
----

The script uses gettext package for internationalization.

Install it before running the script.

On macOS
--------

.. code-block:: console

    $ brew install gettext

On Windows
----------

see https://mlocati.github.io/articles/gettext-iconv-windows.html

Catalogs for OTHER packages' domains
------------------------------------

``de/LC_MESSAGES/widgets.po`` is not this package's domain: it corrects two
messages in Plone's own ``widgets`` catalog, where pat-livesearch's summary
line ("found" + N + "results") is translated as "gefunden 7 gefunden".
``update.sh`` does not touch it — the script syncs
``*/LC_MESSAGES/plonetheme.derico.po`` and nothing else.

Two things make such a catalog work, and the second is not obvious:

* it must be COMPILED where it runs. ``.mo`` files are gitignored here and
  the instance builds them at startup (``zope_i18n_compile_mo_files true``
  in ``zope.conf``, which the Plone instance template sets; the test layer
  sets the same environment variable).
* it must come FIRST. ``<i18n:registerTranslations>`` appends to a domain
  and every reader takes the first catalog that has the message, so a
  correction registered after Plone's own is never read.
  ``i18n.prefer_this_packages_catalogs``, subscribed to
  ``IDatabaseOpenedWithRoot``, moves this package's catalogs to the front.

``tests/test_i18n_overrides.py`` holds both.
