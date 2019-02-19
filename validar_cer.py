# -*- coding: utf-8 -*-
import pprint
import datetime 
import json
import os
from cfdi.cfdi import SATFiles
from cfdi import utils
import tempfile

PATH = os.path.abspath(os.path.dirname(__file__))
key_path = os.path.join("cfdi/certificados","cert_test.key")
cer_path = os.path.join("cfdi/certificados","cert_test.cer")
pem_enc_path = os.path.join("cfdi/certificados","cert_test.pem.enc")
password = "12345678a"

 
cer = utils._read_file(cer_path)
key = utils._read_file(key_path)

claves_sat = SATFiles(cer, key, password)

print str(claves_sat)

if claves_sat.is_valid:
    with open(pem_enc_path, 'wb') as f:
        f.write(claves_sat.key_enc)
    msg = 'Los certificados son válidos\n'
    print msg
else:
    print(claves_sat.error)


'''

 

'''

