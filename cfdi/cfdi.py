#!
# -*- coding: utf-8 -*-
import os
from lxml import etree as ET
import datetime
from collections import OrderedDict

import base64
import hashlib
import os
from io import StringIO, BytesIO

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.x509.oid import ExtensionOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

##ROGER

##termina
PATH = os.path.abspath(os.path.dirname(__file__))
class SATcfdi(object):
    CFDI_VERSION = 'cfdi33'
    XSI = 'http://www.w3.org/2001/XMLSchema-instance' ##????
    SAT = {
        'cfdi33': {
            'version': '3.3',
            'prefix': 'cfdi',
            'xmlns': 'http://www.sat.gob.mx/cfd/3',
            'schema': 'http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv33.xsd',
        },
        'nomina12': {
            'version': '1.2',
            'prefix': 'nomina',
            'xmlns': 'http://www.sat.gob.mx/nomina12',
            'schema': 'http://www.sat.gob.mx/nomina12 http://www.sat.gob.mx/sitio_internet/cfd/nomina/nomina12.xsd',
        },
    }

    def __init__(self, data, version=CFDI_VERSION ):
        self._sat_cfdi = self.SAT[version]
        self._name_space = '{{{}}}'.format(self._sat_cfdi['xmlns'])
        self._xsi = self.XSI
        self._pre = self._sat_cfdi['prefix']
        self._cfdi_xml = None
        self.error = ''
        self._data = data


    def _now(self):
        return datetime.datetime.now().isoformat()[:19]

    def get_xml(self):
        self._comprobante()
        self._emisor()
        self._receptor()
        self._conceptos()
        self._impuestos()
        return self._to_xml()

 
    def _to_xml(self):
        self._cfdi_xml = ET.tostring(self._cfdi_xml,
            pretty_print=True, xml_declaration=True, encoding='utf-8')
        
        return self._cfdi_xml.decode('utf-8')


    def _comprobante(self):
        nsmap = {
            'cfdi': self._sat_cfdi['xmlns'],
            'xsi': self.XSI,
            #'schemaLocation': self._sat_cfdi['schema']
        }
        schema_location = ET.QName(self.XSI, 'schemaLocation')

        node_name = '{}Comprobante'.format(self._name_space)
        attrib = self._data['comprobante'] # OrderedDict(self._data['comprobante'])
        attrib[schema_location] = self._sat_cfdi['schema']

        attrib['Version'] = self._sat_cfdi['version']
        attrib['Fecha'] = self._now()

        self._cfdi_xml = ET.Element(node_name, attrib, nsmap=nsmap)
        '''
        porque schemaLocation no lo definiste en nmap si esta como xmlnsi: ya vi es un xsi

        '''
    def _emisor(self):
        self.set_sub_element(key_dic='emisor', name='Emisor')

    def _receptor(self):
        self.set_sub_element(key_dic='receptor', name='Receptor')
    def _receptor2(self):
        attrib = self._data.get("receptor")
        node_name = '{}Receptor'.format(self._name_space)
        emisor = ET.SubElement(self._cfdi_xml, node_name, attrib)
    
    def _conceptos(self):
        conceptos = self._data['conceptos']
        node_name = '{}Conceptos'.format(self._name_space)
        node_parent = ET.SubElement(self._cfdi_xml, node_name)
 
        for c in conceptos:
            #Se quita {"impurestos": {"traslados": {..}}} para que no lo tome como atributo, ya que todos los keys que no tienen dic son una atributo
            complement = c.pop('complemento', {})
            taxes = c.pop('impuestos', {})

            node_name = '{}Concepto'.format(self._name_space)
            node_child = ET.SubElement(node_parent, node_name, OrderedDict(c))

            if taxes:
                node_name = '{}Impuestos'.format(self._name_space)
                node_tax = ET.SubElement(node_child, node_name)
                if taxes.get('traslados', ''):
                    node_name = '{}Traslados'.format(self._name_space)
                    node = ET.SubElement(node_tax, node_name)
                    node_name = '{}Traslado'.format(self._name_space)
                    for t in taxes['traslados']:
                        ET.SubElement(node, node_name, OrderedDict(t))
                if taxes.get('retenciones', ''):
                    node_name = '{}Retenciones'.format(self._name_space)
                    node = ET.SubElement(node_tax, node_name)
                    node_name = '{}Retencion'.format(self._name_space)
                    for t in taxes['retenciones']:
                        ET.SubElement(node, node_name, OrderedDict(t))
    def _impuestos(self):
        node_name = '{}Impuestos'.format(self._name_space)
        taxes = self._data.get('impuestos', False)
        if not taxes:
            ET.SubElement(self._cfdi_xml, node_name)
            return

        traslados = taxes.pop('traslados', False)
        retenciones = taxes.pop('retenciones', False)
        node = ET.SubElement(self._cfdi_xml, node_name, OrderedDict(taxes))

        if traslados:
            node_name = '{}Traslados'.format(self._name_space)
            sub_node = ET.SubElement(node, node_name)
            node_name = '{}Traslado'.format(self._name_space)
            for t in traslados:
                ET.SubElement(sub_node, node_name, OrderedDict(t))

        if retenciones:
            node_name = '{}Retenciones'.format(self._name_space)
            sub_node = ET.SubElement(node, node_name)
            node_name = '{}Retencion'.format(self._name_space)
            for r in retenciones:
                ET.SubElement(sub_node, node_name, OrderedDict(r))
       
    def set_sub_element(self, key_dic, name):

        node_name = '{name_space}{name}'.format(name_space=self._name_space, name=name)
        attrib = self._data.get(key_dic)
        new_sub_element = ET.SubElement(self._cfdi_xml, node_name, attrib)

        return new_sub_element


class SATFiles(object):
    TOKEN = 'c4de672a306cae37117bbba0cf7724a9cdd9c94b31c74272ae'
    def __init__(self, cer, key=b'', password='', token=TOKEN):
        self._error = ''
        self._token = token
        self._init_values()
        #Obtenemos serie, vigencia, cert en base64, si es fiel entre otros
        self._get_data_cer(cer)
        #solo se ejecuta si hay key y password. Solo se va a ejecutar cuando se validan datos y en ese momento generamos el PEM Enc.
        self._get_data_key(key, password)

    def _init_values(self):
        self._rfc = ''
        self._serial_number = ''
        self._not_before = None
        self._not_after = None
        self._is_fiel = False
        self._are_couple = False
        self._is_valid_time = False
        self._cer_txt = ''
        self._key_pem = b''
        self._cer_modulus = 0
        self._key_modulus = 0
        return

    def __str__(self):
        msg = '\tRFC: {}\n'.format(self.rfc)
        msg += '\tNo de Serie: {}\n'.format(self.serial_number)
        msg += '\tVálido desde: {}\n'.format(self.not_before)
        msg += '\tVálido hasta: {}\n'.format(self.not_after)
        msg += '\tEs vigente: {}\n'.format(self.is_valid_time)
        msg += '\tSon pareja: {}\n'.format(self.are_couple)
        msg += '\tEs FIEL: {}\n'.format(self.is_fiel)
        msg += '\tCert base64: {}\n'.format(self._cer_txt)
        return msg

    def _get_hash(self):
        #Genera una contraseña apartir del RFC y numero de serie.
        #para que sirve TOKEN? R= Agregarle un numero aleatorio para la contraseña
        digest = hashes.Hash(hashes.SHA512(), default_backend())

        digest.update(self._rfc.encode())
        digest.update(self._serial_number.encode())
        digest.update(self._token.encode())

        return digest.finalize()

    def _get_data_cer(self, cer):
        #Obtenemos serie, vigencia, cert en base64 entre otros

        obj = x509.load_der_x509_certificate(cer, default_backend())
        self._rfc = obj.subject.get_attributes_for_oid(
            NameOID.X500_UNIQUE_IDENTIFIER)[0].value.split(' ')[0]
        self._serial_number = '{0:x}'.format(obj.serial_number)[1::2]
        self._not_before = obj.not_valid_before
        self._not_after = obj.not_valid_after
        now = datetime.datetime.utcnow()
        self._is_valid_time = (now > self.not_before) and (now < self.not_after)
        if not self._is_valid_time:
            msg = 'El certificado no es vigente'
            self._error = msg

        self._is_fiel = obj.extensions.get_extension_for_oid(
            ExtensionOID.KEY_USAGE).value.key_agreement

        self._cer_txt = ''.join(obj.public_bytes(
            serialization.Encoding.PEM).decode().split('\n')[1:-2])

        self._cer_modulus = obj.public_key().public_numbers().n
        return

    def _get_data_key(self, key, password):
        ''' generamos el PEM y validamos si son pareja
            si no hay password solo asignamos el pem enc. que usaremos para firmar
            si hay password generamos el pem enc y revisamos si son pareja
        '''
        #agregamos el key o pem enc segun la forma en que se llamo.
        self._key_pem = key

        #solo entra cuando se crear el PEM Enc Es decir cuando validamos todos los datos
        if not key or not password:
            #print "---Ninguna Accion en _get_data_key() solo entra cuando se crear el PEM Enc Es decir cuando validamos todos los datos"
            return

        #print "Encriptando PEM.."

        try:
            obj = serialization.load_der_private_key(
                key, password.encode(), default_backend())
        except ValueError:
            msg = 'La contraseña es incorrecta'
            self._error = msg
            return
        #Tal vez aqui se esta generando el pem encriptado? pero donde se guarda? R=, se guarda donde utils.validate_cert 
        #generamos PEM
        p = self._get_hash()
        self._key_pem = obj.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(p)
        )
        #revisamos si son pareja
        self._key_modulus = obj.public_key().public_numbers().n
        self._are_couple = self._cer_modulus == self._key_modulus
        if not self._are_couple:
            msg = 'El CER y el KEY no son pareja'
            self._error = msg
        return

    def _get_key(self, password):
        #si no tenemos pass cargamos el PEM y le pasamos la contraseña generada internamente en el codigo
        #solo la utilizamos para firmar
        if not password:
            password = self._get_hash()
        private_key = serialization.load_pem_private_key(
            self._key_pem, password=password, backend=default_backend())
        return private_key

    def sign(self, data, password=''):
        #firmamos la cadena que nos envio CfdiStamp.get_sello, no le mandamos pass porque internamente esta encriptado. Se va descenriptar en ._get_key

        #obtenemos el pem enc
        private_key = self._get_key(password)
        firma = private_key.sign(data, padding.PKCS1v15(), hashes.SHA256())
        return base64.b64encode(firma).decode()

    @property
    def rfc(self):
        return self._rfc

    @property
    def serial_number(self):
        return self._serial_number

    @property
    def not_before(self):
        return self._not_before

    @property
    def not_after(self):
        return self._not_after

    @property
    def is_fiel(self):
        return self._is_fiel

    @property
    def are_couple(self):
        return self._are_couple

    @property
    def is_valid(self):
        return not bool(self.error)

    @property
    def is_valid_time(self):
        return self._is_valid_time

    @property
    def cer_txt(self):
        return self._cer_txt

    @property
    def key_pem(self):
        return self._key_pem

    @property
    def error(self):
        return self._error



class CfdiStamp(object):
    
    XSLT_PATH=os.path.join(PATH, "xslt","cadena_3.3_1.2.xslt")
    
    def __init__(self, cfdi_xml_string, claves_sat, xslt_path=XSLT_PATH ):
        self.cfdi_xml_string = cfdi_xml_string
        self.xslt_path = xslt_path
        self.claves_sat = claves_sat #cargamos el pem en memoria desencriptado
        self.xml_sellado = ''
        self.xml_parsed = None
        self.element_root_xml = None#Elemento Comprobante del xml
    
    def _to_xml(self, xml_obj):
        xml_string = ET.tostring(xml_obj,
            pretty_print=True, xml_declaration=True, encoding='utf-8')

        xml_string =xml_string.decode('utf-8')
        return xml_string

    def _parse(self, xml_string):
        #utf8_parser = ET.XMLParser(encoding='utf-8')
        xml_parsed =  ET.fromstring(xml_string.encode('utf-8'))

        return xml_parsed #<type 'lxml.etree._Element'>
 

    def _get_cadena(self, xml):
        ''' xml  type ET '''
        #Obtenemos cadena original
        xsl_root = ET.parse(self.XSLT_PATH)
        xsl_transform = ET.XSLT(xsl_root)
        cadena_original = str( xsl_transform(xml) )
        return cadena_original

    def get_sello(self):
        #Leemos el xml que nos enviaron
        
        self.xml_parsed = self._parse(self.cfdi_xml_string)

        #Obtenemos la cadena original
        cadena_original = self._get_cadena(self.xml_parsed)

        #Firmamos la cadena original con el pem
        sello = self.claves_sat.sign(cadena_original)

        #agregamos el sello al Elemento Comprobante
        self.xml_parsed.attrib['Sello'] = sello
 
        #Convertimos a cadena 
        self.xml_sellado = self._to_xml(self.xml_parsed)

        return self.xml_sellado
        

 
    ###Termina



