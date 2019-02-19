# -*- coding: utf-8 -*-
import pprint
import datetime 
import json
import os
from cfdi.cfdi import SATcfdi, CfdiStamp, SATFiles
from cfdi.finkok import PACFinkok
from cfdi import utils
 
# path_cer = join(path_certificates, CERT_NAME.format('cer'))
# path_enc = join(path_certificates, CERT_NAME.format('enc'))

# cer = _read_file(path_cer)
# enc = _read_file(path_enc)
# cert = SATCertificate(cer, enc)

#Definimos las rutas de nuestros archivos
 
cer_path = os.path.join("cfdi/certificados","cert_test.cer")
pem_enc_path = os.path.join("cfdi/certificados","cert_test.pem.enc")
 

#Leemos los archivos
cer = utils._read_file(cer_path)
key_enc = utils._read_file(pem_enc_path)
claves_sat = SATFiles(cer, key_enc)


uuid_factura = raw_input('Ingresa el UUID de la factura: ')
# rfc = raw_input('Ingresa el RFC del Receptor: ')

#uuid_factura = "19E0221C-81C0-4A77-8379-27059CE54CAF"
#rfc_emisor = "LAN7008173R5"

###-Cacenlar la factura
finkok_instance = PACFinkok()


result = finkok_instance.cfdi_cancel(rfc=claves_sat.rfc, uuid=uuid_factura, cer=claves_sat.cer_pem, key=claves_sat.key_pem )

print result
print finkok_instance.error


