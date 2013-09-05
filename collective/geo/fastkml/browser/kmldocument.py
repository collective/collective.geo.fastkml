# -*- coding: utf-8 -*-
import logging
from functools import partial
from App.config import getConfiguration

from zope.component import queryMultiAdapter

from collective.geo.kml.browser.kmldocument import KMLBaseDocument
from collective.geo.kml.browser.kmldocument import BrainPlacemark
from collective.geo.kml.interfaces import IFeature

from fastkml import kml, styles

try:
    from shapely.geometry import asShape
except:
    from pygeoif import as_shape as asShape


from collective.geo.fastkml import MessageFactory as _

logger = logging.getLogger('collective.geo.fastkml')


class FastKMLBaseDocument(KMLBaseDocument):

    def anchorsnippet(self, link):
        return (
            '<p class="placemark-url">'
                '<a href="%s">%s</a>'
            '</p>'
        ) % (link, self.context.translate(_(u'See the original resource')))

    def get_kml(self):

        # Some programs consuming kml cannot handle kml namespaces. For those
        # programs the supress-kml-namespace parameter may be used.
        # e.g. .../@@kml-document?suppress-kml-prefix
        if self.request.get('supress-kml-prefix', None) is not None:
            namespace = ''  # no kml namespace prefixes
        else:
            namespace = None  # use default

        KML = partial(kml.KML, ns=namespace)
        Document = partial(kml.Document, ns=namespace)
        Placemark = partial(kml.Placemark, ns=namespace)
        Style = partial(styles.Style, ns=namespace)
        IconStyle = partial(styles.IconStyle, ns=namespace)
        LineStyle = partial(styles.LineStyle, ns=namespace)
        PolyStyle = partial(styles.PolyStyle, ns=namespace)
        UntypedExtendedData = partial(kml.UntypedExtendedData, ns=namespace)
        UntypedExtendedDataElement = partial(
            kml.UntypedExtendedDataElement, ns=namespace
        )

        k = KML()

        ## make sure description field is encoded properly
        doc = Document(
            name=unicode(self.name, 'utf-8'),
            description=unicode(self.description, 'utf-8')
        )
        k.append(doc)
        docstyle = Style(id="defaultStyle")
        istyle = IconStyle(scale=self.marker_image_size,
                icon_href=self.marker_image,
                color=self.polygoncolor)
        lstyle = LineStyle(color=self.linecolor, width=self.linewidth)
        pstyle = PolyStyle(color=self.polygoncolor)
        docstyle.append_style(istyle)
        docstyle.append_style(lstyle)
        docstyle.append_style(pstyle)
        doc.append_style(docstyle)
        for feature in self.features:
            description =''
            if feature.lead_image():
                description += feature.lead_image()
            if feature.description:
                description += unicode(feature.description, 'utf-8')
            if feature.item_url:
                description += self.anchorsnippet(feature.item_url)
            name = unicode(feature.name, 'utf-8')
            pm = Placemark(name=name, description=description)
            shape = {'type': feature.geom.type,
                'coordinates': feature.geom.coordinates}
            try:
                pm.geometry = asShape(shape)
            except:
                continue
            pm.author = feature.author['name']
            if feature.item_url:
                pm.link = unicode(feature.item_url, 'utf-8')
            if feature.use_custom_styles:
                pms = Style()
                if feature.geom.type in ['Point', 'MultiPoint']:
                    istyle = IconStyle(scale=feature.marker_image_size,
                        icon_href=feature.marker_image,
                        color=feature.polygoncolor)
                    pms.append_style(istyle)
                elif feature.geom.type in ['LineString', 'MultiLineString',
                                            'Polygon', 'MultiPolygon']:
                    lstyle = LineStyle(color=feature.linecolor,
                                    width=feature.linewidth)
                    pms.append_style(lstyle)
                if feature.geom.type in ['Polygon', 'MultiPolygon']:
                    pstyle = PolyStyle(color=feature.polygoncolor)
                    pms.append_style(pstyle)
                pm.append_style(pms)
            else:
                pm.styleUrl = "#defaultStyle"
            try:
                extended_data = UntypedExtendedData()
                for element in feature.extended_data:
                    extended_data.elements.append(
                        UntypedExtendedDataElement(
                            name=element.name,
                            value=element.value,
                            display_name=element.display_name
                        )
                    )
                if extended_data.elements:
                    pm.extended_data = extended_data
            except AttributeError as e:
                logger.debug(e.message)
            doc.append(pm)

        pretty_print =  any((
            getConfiguration().debug_mode,
            self.request.get('pretty-print', None) is not None
        ))
        
        xml = u'<?xml version="1.0" encoding="UTF-8"?>' + \
                k.to_string(prettyprint=pretty_print)
        
        return xml

    def __call__(self):
        filename = '%s.kml' % self.context.id
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="%s"' % filename)
        self.request.response.setHeader('Content-Type',
            'application/vnd.google-earth.kml+xml; charset=utf-8')
        xml = self.get_kml()
        return xml.encode('utf-8')


class FastBrainPlacemark(BrainPlacemark):

    imagesnippet='''<a class="placemark-image"
    href="%(url)s/view">
    <img src="%(url)s/image_%(scale)s" alt="%(name)s" title="%(name)s"
    class="%(class)s" /></a>'''

    def lead_image(self, scale='thumb', css_class="tileImage"):
        if self.item_type == 'Image':
            return self.imagesnippet % { 'url': self.item_url,
                    'scale': scale, 'name': self.name, 'class': css_class }
        else:
            return ''

    @property
    def item_type(self):
        return self.context.portal_type

    @property
    def item_url(self):
        return self.context.getURL()

    @property
    def extended_data(self):
        return []


class KMLDocument(FastKMLBaseDocument):

    @property
    def features(self):
        feature = queryMultiAdapter((self.context, self.request), IFeature)
        if feature:
            return [feature]
        return []


class KMLFolderDocument(FastKMLBaseDocument):

    @property
    def features(self):
        for item in self.context.values():
            feature = queryMultiAdapter((item, self.request), IFeature)
            if not feature:
                continue
            yield feature


class KMLTopicDocument(FastKMLBaseDocument):

    @property
    def features(self):
        for brain in self.context.queryCatalog():
            yield FastBrainPlacemark(brain, self.request, self)

