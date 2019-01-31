# -*- coding: utf-8 -*-
import pprint
import datetime 
import json
import os
from cfdi.cfdi import SATcfdi, CfdiStamp, SATFiles
from cfdi.finkok import PACFinkok
import tempfile

PATH = os.path.abspath(os.path.dirname(__file__))
CERT_NUM = '20001000000300022815'
key_path = os.path.join("cfdi/certificados","cert_test.key")
cert_path = os.path.join("cfdi/certificados","cert_test.cer")
pem_enc_path = os.path.join("cfdi/certificados","cert_test.pem")
path_xlst = os.path.join("cfdi/xslt","cadena_3.3_1.2.xslt")
password = "12345678a"


#Generamos un Dic
with open('cfdi_minimo.json') as f:
    datos = json.load(f)

#generar xml
#Debemos tener guardado noCertificado, certificado en base 64. 
#*vamos a generar cfdi solo con el noCertificado
cfdi = SATcfdi(datos)
xml_string = cfdi.get_xml()

#sellar la factura
# cfdistamp = CfdiStamp(cfdi, key_path, cert_path, pem_enc_path, CERT_NUM)
# xml = cfdistamp.get_sello_fm(xml) ##Porque mando cfdi?

#obtenemos el PEM e info del certificado
claves_sat = SATFiles(cert_path, pem_enc_path)

cfdistamp = CfdiStamp(xml_string, claves_sat)
xml_sellado = cfdistamp.get_sello() ##Porque mando cfdi?


#Timbrar la factura 
# timbrar = PACFinkok()
# result = timbrar.cfdi_stamp(xml)

# if result:
#     print result['xml']
# else:
#     print timbrar.error


