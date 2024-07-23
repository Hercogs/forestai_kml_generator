import os, sys
import logging

import pandas as pd
import getopt
import numpy as np

from fastkml import kml
from pygeoif.geometry import Point


from fastkml import styles

import libs.lvmgeo_kml_downloader

# Set up logging system
logger = logging.getLogger('main')
logging.basicConfig(format='%(name)s:%(levelname)s:%(message)s', stream=sys.stderr ,level = logging.INFO)


DEFAULT_INPUT_FILE = "./input/test.xlsx"
DEFAULT_KML_TEMPLATE = "./kml_template.kml"

# Global KML
final_kml = kml.KML()
with open(DEFAULT_KML_TEMPLATE, encoding="utf-8") as kml_file:
    final_kml.from_string(kml_file.read().encode("utf-8"))


def append_kml(placemark):
    global final_kml

    # This corresponds to the single ``Document``
    document_features = list(final_kml.features())

    # Get folder list
    folder_list_features = list(document_features[0].features())

    # Get first folder
    folder_first_features = folder_list_features[0]

    folder_first_features.append(placemark)

    logger.info(f"Appended kml")


def generate_single_kml_file(kml_data, object_id):
    k = kml.KML()
    k.from_string(kml_data.encode("utf-8"))

    # This corresponds to the single ``Document``
    document_features = list(k.features())

    # Get folder list
    folder_list_features = list(document_features[0].features())

    # Get first folder
    folder_first_features = folder_list_features[0]

    # Get placemark list
    placemark_list_features = list(folder_first_features.features())

    # Get first placemark
    placemark_first_features = placemark_list_features[0]


    # Create new kml file
    k_new = kml.KML()
    ns = "{http://www.opengis.net/kml/2.2}"
    d = kml.Document(ns=ns, id=object_id, name=object_id, description=object_id)
    k_new.append(d)
    d.append(placemark_first_features)

    with open("output/kml_files" + '/' + object_id + '.kml', 'w', encoding='utf-8') as kml_new_file:
        kml_new_file.write(k_new.to_string(prettyprint=True))
        #print(k_new.to_string(prettyprint=True))

        logger.info(f"Single kml generated: {object_id}")


def process_kml(kml_string, object_id, suga):
    global final_kml

    lvm_geo_data = None

    k = kml.KML()
    k.from_string(kml_string.encode("utf-8"))

    # This corresponds to the single ``Document``
    document_features = list(k.features())

    # Get folder list
    folder_list_features = list(document_features[0].features())

    # Get first folder
    folder_first_features = folder_list_features[0]

    # Get placemark list
    placemark_list_features = list(folder_first_features.features())

    # Get first placemark
    placemark_first_features = placemark_list_features[0]

    # Set name
    placemark_first_features.name = object_id

    # Set color
    if suga == "Egle":
        placemark_first_features.styleUrl = "#eglePolyStyle"
    elif suga == "Priede":
        placemark_first_features.styleUrl = "#priedePolyStyle"
    else:
        placemark_first_features.styleUrl = "#otherPolyStyle"

    # Get all extended data
    lvm_geo_data = placemark_first_features.extended_data.elements[0].data

    properties = ["kadastrs", "kvart", "nog", "atj_gads"]
    for pr in properties:
        status, value = read_lvm_geo_data(lvm_geo_data, pr)
        if status:
            write_placemark_data(pr, value, placemark_first_features)
        else:
            write_placemark_data(pr, "", placemark_first_features)

    # Write suga
    write_placemark_data("suga", str(suga), placemark_first_features)

    # Check if main KML is empty
    if not final_kml:
        logger.debug(f"Writing KML for the first time")
        final_kml = k
    else:
        append_kml(placemark_first_features)

    # Generate placemark for point object to better see polygon
    p = generate_point_placemark(placemark_first_features, suga)
    append_kml(p)

    return True, lvm_geo_data


def generate_point_placemark(polygon_placemark, suga):
    # Get coordinates
    coordinates = polygon_placemark.geometry.bounds
    x = (coordinates[0] + coordinates[2]) / 2
    y = (coordinates[1] + coordinates[3]) / 2

    p = kml.Placemark()
    p.geometry = Point(x, y, 0.0)

    # Set color
    if suga == "Egle":
        p.styleUrl = "#eglePolyStyle"
        p.name = suga
    elif suga == "Priede":
        p.styleUrl = "#priedePolyStyle"
        p.name = suga
    else:
        p.styleUrl = "#otherPolyStyle"
        p.name = "Cits"

    return p


def write_placemark_data(name, value, placemark):
    d = kml.Data(name=name, value=value)
    placemark.extended_data.elements.append(d)


def read_lvm_geo_data(lvm_geo_data, name):
    for d in lvm_geo_data:
        if d["name"] == name:
            return True, d["value"]
    return False, None


def append_to_log(msg):
    with open("./output/log.txt", "a") as f:
        f.write(msg)
        f.write("\n")


def is_row_valid(kad, kvart, nog):
    row = [kad, kvart, nog]
    return True
    for i in row:
        # Check if type is float
        if type(i) is str:
            return False
        # CHeck if does not contain nNaN
        if i is np.nan:
            return False
        if np.isnan(i):
            return False
    return True


def parse_arguments(argv):
    arg_input_file = DEFAULT_INPUT_FILE
    arg_help = f'Pass argument as -> {argv[0]} -i <input_filename.csv>'

    if len(argv) != 1:
        try:
            opts, args = getopt.getopt(argv[1:], 'hi:', ['help', 'input='])
        except:
            logger.info(arg_help)
            sys.exit(-1)

        if len(opts) == 0:
            logger.info(arg_help)
            sys.exit()

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                logger.info(arg_help)
                sys.exit()
            elif opt in ('-i', '--input'):
                arg_input_file = arg
            else:
                logger.info(arg_help)
                sys.exit()
        logger.info(f'CSV data will be read from {arg_input_file}')
    else:
        logger.info(f'Using default filename: {arg_input_file}')
    return arg_input_file


def main(argv):
    input_file = parse_arguments(argv)

    # Init log file
    with open("./output/log.txt", "w") as f:
        f.write(f"Info about rows, which could not be processed!\n\n")

    # Create downloader
    kml_downloader = libs.lvmgeo_kml_downloader.KMLDownloader()

    df = pd.read_excel(input_file, converters={"KADAST": str, "KV": str, "NOG": str})

    # Add extra column for VMD atj_gads
    df.insert(8, "atj_gads", np.nan)
    lines = df.shape[0]

    for index, row in df.iterrows():
        kad, kvar, nog = row["KADAST"], row["KV"], row["NOG"]

        logger.info(f"Processing row index ({index}) out of {lines}")

        if not is_row_valid(kad, kvar, nog):
            logger.error(f"Row index({index}) {kad}_{kvar}_{nog} is not valid")
            append_to_log(f"Row index({index}) {kad}_{kvar}_{nog} is not valid")
            continue

        object_id = f"{kad}_{kvar}_{nog}"

        status, kml_data = kml_downloader.download_kml(kad, kvar, nog)
        if not status:
            logger.error(f"Row index({index}) {object_id} not found in LVMGEO VMD database")
            append_to_log(f"Row index({index}) {object_id} not found in LVMGEO VMD database")
            continue

        # Generate KML file with this specific geometry only
        generate_single_kml_file(kml_data, object_id)

        # Append this geometry to overall kml file
        status, lvm_geo_data = process_kml(kml_data, object_id, row["SUG"])
        if not status:
            logger.error(f"process_kml() failed for {object_id}")

        status, value = read_lvm_geo_data(lvm_geo_data, "atj_gads")
        if status:
            df.at[index, "atj_gads"] = float(value)
        # else:
        #     df.at[row, "atj_gads"] = ""

        # if index > 1:
        #     break

    # Save main kml
    with open("./output/main.kml", "w") as mykml:
        out_kml = final_kml.to_string(prettyprint=True)
        mykml.write(out_kml)

    # Save df
    df.to_csv("./output/output.csv", encoding='utf-8')


if __name__ == "__main__":
    main(sys.argv)