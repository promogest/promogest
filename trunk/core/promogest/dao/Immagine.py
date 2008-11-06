#-*- coding: utf-8 -*-
#
# Promogest
#
# Copyright (C) 2005 by Promotux Informatica - http://www.promotux.it/
# Author: Francesco Meloni <francesco@promotux.it>


from promogest.lib.sqlalchemy import *
from promogest.lib.sqlalchemy.orm import *
from promogest.Environment import *
from Dao import Dao

class Immagine(Dao):

    def __init__(self, arg=None,isList=False, id=None):
        Dao.__init__(self, entity=self.__class__, isList=isList, id=id)

    def filter_values(self,k,v):
        dic= {'filename' : operazione.c.filename==v}
        return  dic[k]

immagine=Table('image',
        params['metadata'],
        schema = params['schema'],
        autoload=True)

std_mapper = mapper(Immagine, immagine, order_by=immagine.c.id)

