# -*- coding: utf-8 -*-
import pprint
import datetime 
import json
import os
from cfdi.cfdi import SATcfdi, CfdiStamp, SATFiles
from cfdi.finkok import PACFinkok
from cfdi import utils

PATH = os.path.abspath(os.path.dirname(__file__))
CERT_NUM = '20001000000300022815'
key_path = os.path.join("cfdi/certificados","cert_test.key")
cer_path = os.path.join("cfdi/certificados","cert_test.cer")
pem_enc_path = os.path.join("cfdi/certificados","cert_test.pem.enc")
path_xlst = os.path.join("cfdi/xslt","cadena_3.3_1.2.xslt")
password = "12345678a"
 


def timbrar():
    from suds.client import Client
    import base64

    # Username and Password, assigned by FINKOK
    username = 'pedro'
    password = '08ab5d7ba6c320987f10663806632bac31026e827d24aa3a175f372af7ab'
     
    # Read the xml file and encode it on base64
    invoice_path = "sellado.xml"
    file = open(invoice_path)
    lines = "".join(file.readlines())
    xml = base64.encodestring(lines)
     
    # Consuming the stamp service
    url = "https://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl"
    client = Client(url,cache=None)
    contenido = client.service.stamp(xml,username,password)
    print contenido
    xml = contenido.xml
     
#Generamos un Dic
with open('cfdi_minimo.json') as f:
    datos = json.load(f)


#Generamos XML
cfdi = SATcfdi(datos)
xml_string = cfdi.get_xml()

#Sellamos la factura
cer = utils._read_file(cer_path)
pem_enc = utils._read_file(pem_enc_path)

claves_sat = SATFiles(cer, pem_enc)
#sellamos la factura
cfdistamp = CfdiStamp(xml_string, claves_sat)
xml_sellado = cfdistamp.get_sello() ##Porque mando cfdi?
print "TYPE"
print type(xml_sellado)


#Guardamos el xml sellado para usarlo en timbrar()
res_file = open('sellado.xml', 'w')
res_file.write(str(xml_sellado))
res_file.close()

#timbrar()

timbrar()

 