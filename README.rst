Introduction
============

collective.geo.fastkml replaces the template based generation of
collective.geo.kml_ with the objectoriented approch of fastkml_

collective.geo.fastkml does support Polygons and MultiPolygons with holes.
Depending how many holes your polygons have it may take longer to generate
you KML file with collective.geo.fastkml (as collective.geo.kml_ ignores
the holes). Generally collective.geo.fastkml is slightly faster than
collective.geo.kml_ and produces smaller files.

The style for polygons is created from the linestyle and polygonstyle so
polygons can have an outline that is diffrent from the polygon fill style

collective.geo.fastkml does not have an interface of its own, it just
overrides the kml-document view of collective.geo.kml.

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

.. _fastkml: https://github.com/cleder/fastkml
.. _collective.geo.kml: https://github.com/collective/collective.geo.kml
