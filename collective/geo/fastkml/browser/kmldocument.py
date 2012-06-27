# -*- coding: utf-8 -*-
from App.config import getConfiguration

from zope.component import queryMultiAdapter

from collective.geo.kml.browser.kmldocument import KMLBaseDocument
from collective.geo.kml.browser.kmldocument import BrainPlacemark
from collective.geo.kml.interfaces import IFeature

from fastkml import kml, styles

from shapely.geometry import asShape

class FastKMLBaseDocument(KMLBaseDocument):

    anchorsnippet = '''<p class="placemark-url">
    <a href="%s">See the original resource</a>
    </p>'''

    def get_kml(self):
        k = kml.KML()
        doc = kml.Document(name = self.name, description=self.description)
        k.append(doc)
        docstyle = styles.Style(id="defaultStyle")
        istyle = styles.IconStyle(scale=self.marker_image_size,
                icon_href=self.marker_image,
                color=self.polygoncolor)
        lstyle = styles.LineStyle(color=self.linecolor, width=self.linewidth )
        pstyle = styles.PolyStyle(color=self.polygoncolor)
        docstyle.append_style(istyle)
        docstyle.append_style(lstyle)
        docstyle.append_style(pstyle)
        doc.append_style(docstyle)
        for feature in self.features:
            description=feature.description
            if feature.item_url:
                description += self.anchorsnippet % feature.item_url
            pm = kml.Placemark(name = feature.name, description=description)
            shape = { 'type': feature.geom.type,
                'coordinates': feature.geom.coordinates}
            try:
                pm.geometry = asShape(shape)
            except:
                continue
            if feature.use_custom_styles:
                pms = styles.Style()
                if feature.geom.type in ['Point', 'MultiPoint']:
                    istyle= styles.IconStyle(scale=feature.marker_image_size,
                        icon_href=feature.marker_image,
                        color=feature.polygoncolor)
                    pms.append_style(istyle)
                elif feature.geom.type in ['LineString', 'MultiLineString',
                                            'Polygon', 'MultiPolygon']:
                    lstyle = styles.LineStyle(color=feature.linecolor,
                                    width=feature.linewidth )
                    pms.append_style(lstyle)
                if feature.geom.type in ['Polygon', 'MultiPolygon']:
                    pstyle = styles.PolyStyle(color=feature.polygoncolor)
                    pms.append_style(pstyle)
                pm.append_style(pms)
            else:
                pm.styleUrl = "#defaultStyle"
            doc.append(pm)
        if getConfiguration().debug_mode:
            xml = '<?xml version="1.0" encoding="UTF-8"?>' + k.to_string(prettyprint=True)
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
            xml= xml.decode('utf-8', 'ignore')
        except:
            pass
        return xml.encode('utf-8')

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
            yield BrainPlacemark(brain, self.request, self)
