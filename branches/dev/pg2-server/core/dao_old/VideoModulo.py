#-*- coding: utf-8 -*-
#
# Promogest - Janas
#
# Copyright (C) 2005 by Promotux Informatica - http://www.promotux.it/
# Author: Francesco Meloni <francesco@promotux.it>

from sqlalchemy import *
from sqlalchemy.orm import *
from core.Environment import *
from core.dao.Modulo import Modulo
from Dao import Dao

moduloTable = Table('modulo', params["metadata"], autoload=True, schema=params["schema"])

if tipo_db == "sqlite":
    moduloFK= 'modulo.id'
else:
    moduloFK = params["schema"]+'.modulo.id'

videomoduloTable = Table('video_modulo', params["metadata"],
        Column('id', Integer, primary_key=True),
        Column('testo_alternativo', String(150), nullable=False),
        Column('imagepath',String(700), nullable=False),
        Column('numero',  Integer, nullable=False),
        Column('id_modulo',Integer ,ForeignKey(moduloFK,onupdate="CASCADE",ondelete="CASCADE"),nullable=False),
        schema=params["schema"]
        )
videomoduloTable.create(checkfirst=True)


class VideoModulo(Dao):

    def __init__(self, req= None,arg=None):
        Dao.__init__(self, entity=self)

    def filter_values(self, k,v):
        dic= {
            'idModulo':videomodulo.c.id_modulo == v,
                }
        return  dic[k]

videomodulo=Table('video_modulo', params['metadata'],schema = params['schema'],autoload=True)
std_mapper = mapper(VideoModulo, videomodulo)