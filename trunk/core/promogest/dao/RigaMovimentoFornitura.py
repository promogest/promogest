# -*- coding: utf-8 -*-

#    Copyright (C) 2005-2015 by Promotux
#                        di Francesco Meloni snc - http://www.promotux.it/

#    Author: Francesco Meloni  <francesco@promotux.it>

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

from sqlalchemy import *
from sqlalchemy.orm import *
from promogest.Environment import *

from promogest.dao.Dao import Dao, Base
from promogest.dao.Fornitura import Fornitura
from promogest.dao.RigaMovimento import RigaMovimento, t_riga_movimento


class RigaMovimentoFornitura(Base, Dao):
    try:
        __table__ = Table('riga_movimento_fornitura',
                params['metadata'],
                schema = params['schema'],
                autoload=True)
    except:
        from data.rigaMovimentoFornitura import t_riga_movimento_fornitura
        __table__ = t_riga_movimento_fornitura


    forni =  relationship("Fornitura")
    rigamovacq = relationship("RigaMovimento",primaryjoin = (__table__.c.id_riga_movimento_acquisto==t_riga_movimento.c.id), backref="rmfac")
    rigamovven = relationship("RigaMovimento", primaryjoin = (__table__.c.id_riga_movimento_vendita==t_riga_movimento.c.id),backref="rmfve")

    def __init__(self, req=None):
        Dao.__init__(self, entity=self)

    def filter_values(self,k,v):
        if k == "idRigaMovimentoAcquisto":
            dic= {k:RigaMovimentoFornitura.__table__.c.id_riga_movimento_acquisto ==v}
        elif k == 'idFornitura':
            dic = {k:RigaMovimentoFornitura.__table__.c.id_fornitura==v}
        elif k == "idRigaMovimentoVendita":
            dic= {k:RigaMovimentoFornitura.__table__.c.id_riga_movimento_vendita ==v}
        elif k == "idRigaMovimentoVenditaBool":
            dic= {k:RigaMovimentoFornitura.__table__.c.id_riga_movimento_vendita != None}
        elif k == "idRigaMovimentoAcquistoBool":
            dic= {k:RigaMovimentoFornitura.__table__.c.id_riga_movimento_acquisto != None}
        elif k == "idRigaMovimentoVenditaBoolFalse":
            dic= {k:RigaMovimentoFornitura.__table__.c.id_riga_movimento_vendita == None}
        elif k == "idRigaMovimentoAcquistoBoolFalse":
            dic= {k:RigaMovimentoFornitura.__table__.c.id_riga_movimento_acquisto == None}
        elif k == "idArticolo":
            dic= {k:RigaMovimentoFornitura.__table__.c.id_articolo ==v}
        return  dic[k]

#if tipodb=="sqlite":
    #a = session.query(RigaMovimento.id).all()
    #b = session.query(RigaMovimentoFornitura.id_riga_movimento_acquisto).all()
    #fixit =  list(set(b)-set(a))
    #print "fixt-rigamovforni", fixit
    #for f in fixit:
        #if f[0] != "None" and f[0] != None:
            #aa = RigaMovimentoFornitura().select(idRigaMovimentoAcquisto=f[0], batchSize=None)
            #for a in aa:
                #session.delete(a)
    #try:
        #session.commit()
    #except:
        #session.rollback()
        #print "ERRORE SU FIXIT"
