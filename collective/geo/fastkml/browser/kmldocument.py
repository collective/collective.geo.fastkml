# -*- coding: utf-8 -*-
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
from zope.i18n import translate


class FastKMLBaseDocument(KMLBaseDocument):

    def anchorsnippet(self, link):
        snippettext = self.context.translate(_(u'See the original resource'))
        return '''<p class="placemark-url">
            <a href="%s">%s</a></p>''' % (link, snippettext)

    def get_kml(self):

        k = kml.KML()
        ## make sure description field is encoded properly
        desc = unicode(self.description, \
                       'utf-8').encode('ascii', 'xmlcharrefreplace')
        doc = kml.Document(name=self.name, description=desc)
        k.append(doc)
        docstyle = styles.Style(id="defaultStyle")
        istyle = styles.IconStyle(scale=self.marker_image_size,
                icon_href=self.marker_image,
                color=self.polygoncolor)
        lstyle = styles.LineStyle(color=self.linecolor, width=self.linewidth)
        pstyle = styles.PolyStyle(color=self.polygoncolor)
        docstyle.append_style(istyle)
        docstyle.append_style(lstyle)
        docstyle.append_style(pstyle)
        doc.append_style(docstyle)
        for feature in self.features:
            description =''
            if feature.lead_image():
                description += feature.lead_image()
            if feature.description:
                description += unicode(feature.description, \
                                  'utf-8').encode('ascii', 'xmlcharrefreplace')
            if feature.item_url:
                description += self.anchorsnippet(feature.item_url)
            name = unicode(feature.name, 'utf-8').encode('ascii', 'xmlcharrefreplace')
            pm = kml.Placemark(name=name, description=description)
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
                pms = styles.Style()
                if feature.geom.type in ['Point', 'MultiPoint']:
                    istyle = styles.IconStyle(scale=feature.marker_image_size,
                        icon_href=feature.marker_image,
                        color=feature.polygoncolor)
                    pms.append_style(istyle)
                elif feature.geom.type in ['LineString', 'MultiLineString',
                                            'Polygon', 'MultiPolygon']:
                    lstyle = styles.LineStyle(color=feature.linecolor,
                                    width=feature.linewidth)
                    pms.append_style(lstyle)
                if feature.geom.type in ['Polygon', 'MultiPolygon']:
                    pstyle = styles.PolyStyle(color=feature.polygoncolor)
                    pms.append_style(pstyle)
                pm.append_style(pms)
            else:
                pm.styleUrl = "#defaultStyle"
            doc.append(pm)
        if getConfiguration().debug_mode:
            xml = '<?xml version="1.0" encoding="UTF-8"?>' + \
                    k.to_string(prettyprint=True)
        else:
            xml = '<?xml version="1.0" encoding="UTF-8"?>' + k.to_string()
        return xml

    def __call__(self):
        filename = '%s.kml' % self.context.id
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="%s"' % filename)
        self.request.response.setHeader('Content-Type',
            'application/vnd.google-earth.kml+xml; charset=utf-8')
        xml = self.get_kml()
        try:
            xml = xml.decode('utf-8', 'ignore')
        except:
            pass
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
        for brain in self.context.getFolderContents():
            try:
                if brain.zgeo_geometry['coordinates']:
                    yield FastBrainPlacemark(brain, self.request, self)
            except:
                continue

class KMLTopicDocument(FastKMLBaseDocument):

    @property
    def features(self):
        for brain in self.context.queryCatalog():
            try:
                if brain.zgeo_geometry['coordinates']:
                    yield FastBrainPlacemark(brain, self.request, self)
            except:
                continue

