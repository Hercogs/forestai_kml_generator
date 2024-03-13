#! /usr/bin/python

import os, sys
import logging

import owslib.wfs
import json

from fastkml import kml

from . import ogc_filter

#import ogc_filter


# Set up logging system
logger = logging.getLogger('main')
logging.basicConfig(format='%(name)s:%(levelname)s:%(message)s', stream=sys.stderr ,level = logging.INFO)


class KMLDownloader:
    def __init__(self):
        self._service_link = 'https://lvmgeoserver.lvm.lv/geoserver/publicwfs/ows?service=wfs&'\
            'version=2.0.0&request=GetCapabilities&layer=publicwfs:vmdpubliccompartments'
        self._layer_name = 'publicwfs:vmdpubliccompartments'
        self._wfs = owslib.wfs.WebFeatureService(self._service_link, timeout=10, version = '1.1.0')
        self._filter_generator = ogc_filter.OgcFilter()

    def download_kml(self, kadastrs, kvartals, nogabals):
        filter = self._filter_generator.generate_filter(kadastrs, kvartals, nogabals)

        # Check if it exists in lvmgeo
        if not self.exists_in_lvmgeo(filter):
            return False, None

        # Generate KML file
        feature = self._wfs.getfeature(
            typename=[self._layer_name],
            maxfeatures=10,
            filter=filter,
            outputFormat='KML',
        )

        res = feature.read().decode()
        return True, res

    def exists_in_lvmgeo(self, filter):
        feature = self._wfs.getfeature(
            typename=[self._layer_name],
            maxfeatures=10,
            filter=filter,
            outputFormat='application/json',
        )

        res = json.loads(feature.read())
        if not(res['numberMatched'] == 1 and res['numberReturned'] == 1):
            return False
        return True

    def read_simple_data(self, placemark, name):
        if len(placemark.extended_data.elements) != 1:
            return False, None
        # Get all dictionary of Simple data
        data = placemark.extended_data.elements[0].data
        for d in data:
            if d["name"] == name:
                return True, d["value"]
        return False, None


def main():
    kml_d = KMLDownloader()

    kadastrs = 44460020389
    kvartals = 2
    nogabals = 2

    status, kml_data = kml_d.download_kml(kadastrs, kvartals, nogabals)

    k = kml.KML()
    k.from_string(kml_data.encode("utf-8"))
    # This corresponds to the single ``Document``
    features = list(k.features())

    # Get folder
    f2 = list(features[0].features())

    # Get placemark
    f3 = list(f2[0].features())[0]

    st, val = kml_d.read_simple_data(f3, "atj_gads")
    print(val)

    # name = str(kadastrs) + str("_") + str(kvartals) + str("_") + str(nogabals)
    # with open(name, "w") as myfile:
    #     myfile.write(res)

if __name__ == "__main__":
    main()
