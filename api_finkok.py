# -*- coding: utf-8 -*-

from cfdi.finkok import PACFinkok

FINKOK = {
    'AUTH': {
        'USER': 'pedroz',
        'PASS': '08ab5d7ba6c320987f10663806632bac31026e827d24aa3a175f372af7ab',
    },
    'RESELLER': {
        'USER': 'pedro',
        'PASS': '08ab5d7ba6c320987f10663806632bac31026e827d24aa3a175f372af7ab'
    },
    'WS': 'http://demo-facturacion.finkok.com/servicios/soap/{}.wsdl',
} 

###Agregar Cliente
rfc = "VCI0210053J9"
#rfc = "KUCG9102232Z8"
finkok = PACFinkok(finkok_auth=FINKOK)



cliente_agregado = finkok.client_add(rfc, type_user=True)

if cliente_agregado:
    print finkok.result
else:
    print finkok.error
    


