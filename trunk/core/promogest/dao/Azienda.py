#-*- coding: utf-8 -*-

# Promogest
#
# Copyright (C) 2005 by Promotux Informatica - http://www.promotux.it/
# Author: Francesco Meloni <francesco@promotux.it>

from promogest.lib.sqlalchemy import *
from promogest.lib.sqlalchemy.orm import *
from promogest.Environment import *
from Dao import Dao
import promogest.lib.sqlalchemy
from promogest.lib.sqlalchemy import and_, or_

class Azienda(Dao):
    """ User class provides to make a Users dao which include more used"""

    def __init__(self, arg=None, isList=False, id=None):
        Dao.__init__(self, entity=self.__class__, isList=isList, id=id)
        #pass

    def filter_values(self, k,v):
        dic= {  'denominazione' : azienda.c.denominazione.ilike("%"+v+"%")}
        return  dic[k]

azienda=Table('azienda',
        params['metadata'],
        autoload=True,
        schema = params['mainSchema'])

std_mapper = mapper(Azienda, azienda, order_by=azienda.c.schemaa)


