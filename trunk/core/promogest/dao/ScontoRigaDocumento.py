# -*- coding: utf-8 -*-

#    Copyright (C) 2005, 2006, 2007 2008, 2009, 2010 by Promotux
#                       di Francesco Meloni snc - http://www.promotux.it/

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


from sqlalchemy import Table
from sqlalchemy.orm import mapper, join
from promogest.Environment import *
from Dao import Dao

class ScontoRigaDocumento(Dao):

    def __init__(self, req=None):
        Dao.__init__(self, entity=self)

    def filter_values(self,k,v):
        dic= {'id':sconto_riga_documento.c.id ==v,
            'idRigaDocumento':sconto_riga_documento.c.id_riga_documento==v,}
        return  dic[k]

sconto_riga_documento=Table('sconto_riga_documento',
                        params['metadata'],
                        schema = params['schema'],
                        autoload=True)

sconto=Table('sconto',
            params['metadata'],
            schema = params['schema'],
            autoload=True)

j = join(sconto, sconto_riga_documento)

std_mapper = mapper(ScontoRigaDocumento,j, properties={
    'id':[sconto.c.id, sconto_riga_documento.c.id],
    }, order_by=sconto_riga_documento.c.id)
