class OgcFilter:
    def __init__(self):
        self.filter_template = '<ogc:And xmlns:ogc="http://www.opengis.net/ogc">' \
                               '<ogc:PropertyIsEqualTo xmlns:ogc="http://www.opengis.net/ogc">' \
                               '<ogc:PropertyName>kadastrs</ogc:PropertyName>' \
                               '<ogc:Literal>{kadastrs}</ogc:Literal>' \
                               '</ogc:PropertyIsEqualTo>' \
                               '<ogc:PropertyIsEqualTo xmlns:ogc="http://www.opengis.net/ogc">' \
                               '<ogc:PropertyName>kvart</ogc:PropertyName>' \
                               '<ogc:Literal>{kvart}</ogc:Literal>' \
                               '</ogc:PropertyIsEqualTo>' \
                               '<ogc:PropertyIsEqualTo xmlns:ogc="http://www.opengis.net/ogc">' \
                               '<ogc:PropertyName>nog</ogc:PropertyName>' \
                               '<ogc:Literal>{nog}</ogc:Literal>' \
                               '</ogc:PropertyIsEqualTo>' \
                               '</ogc:And>'

    def generate_filter(self, kadastrs, kvart, nog):
        filter = self.filter_template.format(kadastrs=kadastrs, kvart=kvart, nog=nog)
        return filter