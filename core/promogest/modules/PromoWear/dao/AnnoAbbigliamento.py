# -*- coding: utf-8 -*-

# Promogest
#
# Copyright (C) 2005-2008 by Promotux Informatica - http://www.promotux.it/
# Author: Francesco Meloni <francesco@promotux.it>

from sqlalchemy import *
from sqlalchemy.orm import *
from promogest.Environment import *
from promogest.dao.Dao import Dao

class AnnoAbbigliamento(Dao):

    def __init__(self, arg=None,isList=False, id=None):
        Dao.__init__(self, entity=self.__class__, isList=isList, id=id)


    def filter_values(self,k,v):
        dic= {'id':annoabbigliamento.c.id ==v}
        return  dic[k]

annoabbigliamento=Table('anno_abbigliamento',
    params['metadata'],
    schema = params['mainSchema'],
    autoload=True)

std_mapper = mapper(AnnoAbbigliamento, annoabbigliamento, properties={},
                order_by=annoabbigliamento.c.id)