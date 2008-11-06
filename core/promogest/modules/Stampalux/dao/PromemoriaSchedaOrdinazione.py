# -*- coding: iso-8859-15 -*-

# Promogest
#
# Copyright (C) 2005 by Promotux Informatica - http://www.promotux.it/
# Author: Dr astico (Pinna Marco) <zoccolodignu@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import promogest.dao.Dao
from promogest.dao.Dao import Dao
from promogest import Environment

"""
CREATE TABLE promemoria_schede_ordinazioni (
    id                          bigint       NOT NULL PRIMARY KEY REFERENCES promemoria(id) ON UPDATE CASCADE ON DELETE CASCADE
    ,id_scheda                   bigint       NOT NULL REFERENCES schede_ordinazioni(id) ON UPDATE CASCADE ON DELETE CASCADE
);
"""


class PromemoriaSchedaOrdinazione(Dao):

    def __init__(self, connection, idPromemoria = None):
        Dao.__init__(self, connection,
                        'PromemoriaSchedaGet', 'PromemoriaSchedaSet', 'PromemoriaSchedaDel',
                        ('id', ), (idPromemoria, ))


def select(connection, idScheda=None, da_data_inserimento = None,
                    a_data_inserimento = None, da_data_scadenza = None,
                    a_data_scadenza = None, oggetto = None, incaricato = None,
                    autore = None, descrizione = None, annotazione = None,
                    riferimento = None, giorni_preavviso = None, in_scadenza = None,
                    scaduto = None, completato = None, orderBy = 'data_scadenza',
                    offset=0, batchSize=5, immediate=False):
    """ Seleziona le righe del promemoria """
    cursor = connection.execStoredProcedure('PromemoriaSchedaSel',
                                            (orderBy, da_data_inserimento, a_data_inserimento,
                                             da_data_scadenza, a_data_scadenza,
                                             oggetto, incaricato, autore,
                                             descrizione, annotazione, riferimento,
                                             giorni_preavviso,
                                             in_scadenza, scaduto, completato,
                                             idScheda, offset, batchSize),
                                            returnCursor=True)

    if immediate:
        return promogest.dao.Dao.select(cursor=cursor, daoClass=PromemoriaSchedaOrdinazione)
    else:
        return (cursor, PromemoriaSchedaOrdinazione)

def count():
    """
    Do nothing (in this case)
    """
    raise NotImplementedError
