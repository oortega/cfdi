# -*- coding: utf-8 -*-
import pprint
import datetime 
import json
import os
from cfdi.cfdi import SATcfdi, CfdiStamp, SATFiles
from cfdi.finkok import PACFinkok
from cfdi import utils
 


PATH = os.path.abspath(os.path.dirname(__file__))

#Definimos las rutas de nuestros archivos
key_path = os.path.join("cfdi/certificados","cert_test.key")
cer_path = os.path.join("cfdi/certificados","cert_test.cer")
pem_enc_path = os.path.join("cfdi/certificados","cert_test.pem.enc")
path_xlst = os.path.join("cfdi/xslt","cadena_3.3_1.2.xslt")



###-Generamos un Dic
#Debemos tener guardado noCertificado, certificado en base 64 en el json
with open('cfdi_varios_articulos.json') as f:
    datos = json.load(f)

###-Generar xml

cfdi = SATcfdi(datos)
xml_string = cfdi.get_xml()

###-sellar la factura

#obtenemos el PEM e info del certificado
cer = utils._read_file(cer_path)
pem_enc = utils._read_file(pem_enc_path)
claves_sat = SATFiles(cer=cer, key=pem_enc, password='')
#mandamos a sellar
cfdistamp = CfdiStamp(xml_string, claves_sat)
xml_sellado = cfdistamp.get_sello() 


###-Timbrar la factura 
timbrar = PACFinkok()
result = timbrar.cfdi_stamp(xml_sellado)

if result:
    print result["xml"]
else:
 
    print timbrar.error



