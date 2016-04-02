from django.db import connection
from rapid.settings import TEMP_DATA_DIR
import jsonpickle
import logging
import os
import requests
import shortuuid
import traceback
import zipfile

# generates a new random UID
import sys


def get_uid(hint=None):
    uid = shortuuid.uuid()
    return uid

def transform_wkt(geom, source_srid, target_srid=4326):
    if source_srid == target_srid:
        return geom

    cursor = connection.cursor()
    cursor.execute("SELECT ST_ASTEXT(ST_TRANSFORM('SRID={0};{1}'::geometry, {2}));".format(source_srid, geom, target_srid))
    row = cursor.fetchone()[0]

    return row

# creates WKT from shapefile shape record components
def create_wkt(geom_type, coords, parts):
    result = '{0}({1})'
    coords_string = ''

    if not parts or geom_type.lower() == 'LineString'.lower():
        index = 0
        while index < len(coords):
            if index > 0:
                coords_string += ', '
            coords_string += '{0} {1}'.format(str(coords[index][0]), str(coords[index][1]))
            index += 1
    else:
        for i in xrange(len(parts)):
            index = parts[i]

            if index == 0:
                coords_string += '('
                if geom_type.lower() == 'MultiPolygon'.lower():
                    coords_string += '('
            else:
                coords_string += ',('
                if geom_type.lower() == 'MultiPolygon'.lower():
                    coords_string += '('

            while index < len(coords):
                if i + 1 < len(parts) and index >= parts[i + 1]:
                    break
                else:
                    if index > parts[i]:
                        coords_string += ', '
                    coords_string += '{0} {1}'.format(str(coords[index][0]), str(coords[index][1]))
                    index += 1
            coords_string += ')'
            if geom_type.lower() == 'MultiPolygon'.lower():
                coords_string += ')'

    result = result.format(geom_type.upper(), coords_string)
    return result

# zips a directory to a specified location
def dir_zip(src, dst):
    zf = zipfile.ZipFile("%s.zip" % (dst), "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            zf.write(absname, arcname)
    zf.close()
    return zf

def prj_content_to_srid(content):
    try:
        params = {'mode': 'wkt', 'terms': content}
        response = requests.get('http://prj2epsg.org/search.json', params=params)
        srid = response.json()['codes'][0]['code']
        return srid
    except:
        raise Exception('Unable to determine Shapefile\'s projection')

def to_json(params):
    jsonpickle.load_backend('json', 'dumps', 'loads', ValueError)
    jsonpickle.set_preferred_backend('json')
    jsonpickle.set_encoder_options('json', ensure_ascii=False)
    out = jsonpickle.encode(params, unpicklable=False)
    out = out.replace(': None', ': null')
    return out

def json_error(msg):
    return to_json({"status": str(msg)})

def unzip_from(path, output_path=TEMP_DATA_DIR):
    import os
    import zipfile
    import time
    from shutil import rmtree

    filename = os.path.basename(path)
    filename = os.path.splitext(filename)[0]

    if (zipfile.is_zipfile(path)):

        zip = zipfile.ZipFile(path)

        new_dir = filename + '_' + str(int(time.time()))

        extract_path = output_path + '/' + new_dir

        zip.extractall(extract_path)

        return new_dir, filename

    else:
        os.remove(path)
        raise Exception(filename + ' was not a .zip archive!')
        return


def setup_logging_to_file(filename):
    logging.basicConfig( filename=filename,
                         filemode='a',
                         level=logging.DEBUG,
                         format= '%(asctime)s - %(levelname)s - %(message)s',
                       )

def extract_function_name():
    """Extracts failing function name from Traceback
    by Alex Martelli
    http://stackoverflow.com/questions/2380073/\
    how-to-identify-what-function-call-raise-an-exception-in-python
    """
    tb = sys.exc_info()[-1]
    stk = traceback.extract_tb(tb, 1)
    fname = stk[0][3]
    return fname

def log_exception(e):
    logging.error(
    "Function {function_name} raised {exception_class} ({exception_docstring}): {exception_message}".format(
    function_name = extract_function_name(), #this is optional
    exception_class = e.__class__,
    exception_docstring = e.__doc__,
    exception_message = e.message))