# -*- coding: utf-8 -*-
import pprint
import datetime 
import json
import os
from cfdi.cfdi import SATcfdi, CfdiStamp, SATFiles
from cfdi.finkok import PACFinkok
from cfdi import utils
 


PATH = os.path.abspath(os.path.dirname(__file__))

key_path = os.path.join("cfdi/certificados","cert_test.key")
cer_path = os.path.join("cfdi/certificados","cert_test.cer")
pem_enc_path = os.path.join("cfdi/certificados","cert_test.pem.enc")
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

###sellar la factura

#obtenemos el PEM e info del certificado
cer = utils._read_file(cer_path)
pem_enc = utils._read_file(pem_enc_path)
claves_sat = SATFiles(cer, pem_enc)

#sellamos la factura
cfdistamp = CfdiStamp(xml_string, claves_sat)
xml_sellado = cfdistamp.get_sello() ##Porque mando cfdi?
print "TYPE"
print type(xml_sellado)
#print xml_sellado


#Timbrar la factura 
timbrar = PACFinkok()
result = timbrar.cfdi_stamp(xml_sellado)

if result:
    print result["xml"]
else:
    print timbrar.error


