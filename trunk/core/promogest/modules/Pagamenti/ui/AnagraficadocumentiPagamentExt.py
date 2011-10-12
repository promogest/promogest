# -*- coding: utf-8 -*-

#    Copyright (C) 2005, 2006, 2007 2008, 2009, 2010, 2011 by Promotux
#                        di Francesco Meloni snc - http://www.promotux.it/

#    Author: Francesco Meloni  <francesco@promotux.it>
#    Author: Andrea Argiolas <andrea@promotux.it>
#    Author: JJDaNiMoTh <jjdanimoth@gmail.com>
#    Author: Dr astico <zoccolodignu@gmail.com>
#    Author: Francesco Marella <francesco.marella@gmail.com>

#    This file is part of Promogest.

#    Promogest is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.

#    Promogest is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Promogest.  If not, see <http://www.gnu.org/licenses/>.

from decimal import *
from promogest.dao.Pagamento import Pagamento
from promogest.dao.TestataDocumento import TestataDocumento
from promogest.modules.PrimaNota.dao.TestataPrimaNota import TestataPrimaNota
from promogest.modules.PrimaNota.dao.RigaPrimaNota import RigaPrimaNota
from promogest.modules.PrimaNota.dao.RigaPrimaNotaTestataDocumentoScadenza import RigaPrimaNotaTestataDocumentoScadenza
from promogest.modules.Pagamenti.dao.TestataDocumentoScadenza import TestataDocumentoScadenza
from promogest.ui.utils import *


def IsPagamentoMultiplo(combobox):
    """
    Controlla la scadenza contenuta nel combobox, restituendo una lista con questi valori:
    valore_di_ritorno = [ 'nome_pagamento', 'giorni_prima_scad', 'separatore', ..., 'FM']
    al posto di ... ci sono 3 ulteriori valori ( fino ad un totale di quattro scadenze )
    e 3 ulteriori separatori. Il valore dell'ultimo campo e` FM se e` una scadenza da
    intendersi a fine mese o '' se non e` da intendersi a fine mese. Nel caso in cui
    il pagamento non sia riconosciuto, o non contenga scadenze, ritorna solo il nome
    del pagamento.
    """

    stringaCombobox = findStrFromCombobox(combobox, 2)
    controllascadenza = re.compile('^.* [0-9]?(.[0-9]+)+.*$')
    r = controllascadenza.match(stringaCombobox)
    finemese = re.compile('^.* [(F|f).(M|m)]*.$')
    if r:
        var = re.split('([0-9]+)', stringaCombobox)
        p = finemese.match(var[len(var)-1])
        if p:
            var[len(var)-1] = "FM"
            return var
        else:
            return var
    else:
        return stringaCombobox





def getDocumentoCollegato(anaedit, numerodocumento):
    """
    Trova il documento in base al numero e ritorna un cursore al documento stesso.
    """

    if anaedit._tipoPersonaGiuridica == "cliente":
        idCliente = anaedit.id_persona_giuridica_customcombobox.getId()
        idFornitore = None
        tipoDocumento = "Nota di credito a cliente"
    elif anaedit._tipoPersonaGiuridica == "fornitore":
        idCliente = None
        idFornitore = anaedit.id_persona_giuridica_customcombobox.getId()
        tipoDocumento = "Nota di credito da fornitore"

    result = TestataDocumento().select(daNumero=numerodocumento,
                                        aNumero=numerodocumento,
                                        daParte=None,
                                        aParte=None,
                                        daData=None,
                                        aData=None,
                                        protocollo=None,
                                        idOperazione=tipoDocumento,
                                        idMagazzino=None,
                                        idCliente=idCliente,
                                        idFornitore=idFornitore)

    if len(result) > 1:
        messageInfo(msg= "Sono stati trovati piu` di un documento. Hai scovato un bug :D")
        return False
    elif len(result) == 0:
        messageInfo(msg="Non e' stato trovato nessun documento con il numero specificato")
        return False
    else:
        return result

def impostaDocumentoCollegato(numerodocumento):
    """
    Imposta il documento indicato dall'utente come collegato al documento
    in creazione.
    """

    documento = getDocumentoCollegato(numerodocumento)
    if documento == False:
        return False
    daoTestata = TestataDocumento().getRecord(id=documento[0].id)
    tipo_documento = daoTestata.operazione
    totale_pagato = daoTestata.totale_pagato
    totale_sospeso = daoTestata.totale_sospeso
    numero_documento = daoTestata.numero
    data_documento = daoTestata.data_documento

    if totale_sospeso != 0:
        messageError(msg="""Attenzione. Risulta che il documento da Lei scelto abbia ancora
un importo in sospeso. Il documento, per poter essere collegato, deve essere completamente saldato""")
        return False

    return totale_pagato

