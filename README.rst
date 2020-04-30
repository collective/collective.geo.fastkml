Introduction
============

``collective.geo.fastkml`` replaces the template based generation of
collective.geo.kml_ with the object oriented approach of fastkml_.

``collective.geo.fastkml`` does support Polygons and MultiPolygons with holes.
Depending how many holes your polygons have it may take longer to generate
you KML file with ``collective.geo.fastkml`` (as collective.geo.kml_ ignores
the holes). Generally ``collective.geo.fastkml`` is slightly faster than
collective.geo.kml_ and produces smaller files.

The style for polygons is created from the line style and polygon style so
polygons can have an outline that is different from the polygon fill style.

``collective.geo.fastkml`` does not have an interface of its own, it just
overrides the kml-document view of collective.geo.kml.


Documentation
=============

Full documentation for end users can be found in the "docs" folder.
It is also available online at https://collectivegeo.readthedocs.io/


Translations
============

This product has been translated into

- Dutch.

- Spanish.

You can contribute for any message missing or other new languages, join us at 
`Plone Collective Team <https://www.transifex.com/plone/plone-collective/>`_ 
into *Transifex.net* service with all world Plone translators community.


Installation
============

Add ``collective.geo.fastkml`` to the list of eggs to install, e.g.

::

    [buildout]
    ...
    eggs =
        ...
        collective.geo.fastkml

Re-run buildout, e.g. with

::

    $ ./bin/buildout

Restart Plone and activate the product in Plones Add-on configuration
section.


Tests status
============

This add-on is tested using Travis CI. The current status of the add-on is:

.. image:: https://img.shields.io/travis/collective/collective.geo.fastkml/master.svg
    :target: https://travis-ci.org/collective/collective.geo.fastkml

.. image:: http://img.shields.io/pypi/v/collective.geo.fastkml.svg
   :target: https://pypi.org/project/collective.geo.fastkml


Contribute
==========

Have an idea? Found a bug? Let us know by `opening a ticket`_.

- Issue Tracker: https://github.com/collective/collective.geo.fastkml/issues
- Source Code: https://github.com/collective/collective.geo.fastkml
- Documentation: https://collectivegeo.readthedocs.io/


License
=======

The project is licensed under the GPLv2.

.. _fastkml: https://github.com/cleder/fastkml
.. _collective.geo.kml: https://github.com/collective/collective.geo.kml
.. _`opening a ticket`: https://github.com/collective/collective.geo.bundle/issues
