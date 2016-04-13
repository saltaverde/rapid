import os
import zipfile
import time

output_path = 'data/input/extracted'

def unzip_from(path):
    print 'unzipping {0}'.format(path)

    zip = zipfile.ZipFile(path)
    filename = os.path.basename(path)
    filename = os.path.splitext(filename)[0]
    print 'filename {0}'.format(filename)
    new_dir = filename + '_' + str(int(time.time()))

    extract_path = output_path + '/' + new_dir

    print 'extracting to {0}'.format(extract_path)
    zip.extractall(extract_path)

    print 'newdir {0}, filename {1}'.format(new_dir, filename)

    return new_dir, filename

