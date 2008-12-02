# -*- coding: iso-8859-15 -*-

# Promogest
#
# Copyright (C) 2005 by Promotux Informatica - http://www.promotux.it/
# Author: Alessandro Scano <alessandro@promotux.it>


from sqlalchemy import *
from sqlalchemy.orm import *
from promogest.Environment import *
from promogest.dao.Dao import Dao
from promogest.dao.TestataMovimento import TestataMovimento
from promogest.modules.VenditaDettaglio.ui.VenditaDettaglioUtils import rigaScontrinoDel
from promogest.modules.VenditaDettaglio.dao.RigaScontrino import RigaScontrino

class TestataScontrino(Dao):

    def __init__(self, arg=None,isList=False, id=None):
        Dao.__init__(self, entity=self.__class__, isList=isList, id=id)


    def _getRigheScontrino(self):
        self.__dbRigheScontrino = RigaScontrino(isList=True).select(idTestataScontrino=self.id, batchSize=None)
        self.__righeScontrino = self.__dbRigheScontrino[:]
        return self.__righeScontrino

    def _setRigheScontrino(self, value):
        self.__righeScontrino = value

    righe = property(_getRigheScontrino, _setRigheScontrino)

    def _dataMovimento(self):
        if self.testatamovimento: return self.testatamovimento.data_movimento
        else: return ""
    data_movimento=property(_dataMovimento)

    def _numeroMovimento(self):
        if self.testatamovimento: return self.testatamovimento.numero
        else: return ""
    numero_movimento=property(_numeroMovimento)


    def filter_values(self,k,v):
        dic= {'id':testata_scontrino.c.id ==v,
            'idTestataMovimento':testata_scontrino.c.id_testata_movimento==v,
            'daData':testata_scontrino.c.data_inserimento >= v,
            'aData': testata_scontrino.c.data_inserimento <= v,
            'idArticolo': and_(testata_scontrino.c.id==riga_scontrinoo.c.id_testata_scontrino,riga_scontrinoo.c.id_articolo==v)}
        return  dic[k]

    def update(self):
        return

    def persist(self, chiusura=False):

        #salvataggio testata scontrino
        params['session'].add(self)
        params['session'].commit()

        #se siamo in chiusura fiscale non serve che vengano toccati i dati delle righe
        if not chiusura:
            if self.__righeScontrino:
                rigaScontrinoDel(id=self.id)
                #cancellazione righe associate alla testata
                for riga in self.__righeScontrino:
                    #annullamento id della riga
                    riga._resetId()
                    #associazione alla riga della testata
                    riga.id_testata_scontrino = self.id
                    #salvataggio riga
                    riga.persist()
        params['session'].flush()

riga_scontrinoo=Table('riga_scontrino',
                params['metadata'],
                schema = params['schema'],
                autoload=True)


testata_scontrino=Table('testata_scontrino',
                    params['metadata'],
                    schema = params['schema'],
                    autoload=True)

std_mapper = mapper(TestataScontrino, testata_scontrino,properties={
        "testatamovimento": relation(TestataMovimento,primaryjoin=
                (testata_scontrino.c.id_testata_movimento==TestataMovimento.id), backref="testata_scontrino"),
        "riga_scontr":relation(RigaScontrino,primaryjoin=RigaScontrino.id_testata_scontrino==testata_scontrino.c.id, backref="testata_scontrino"),
        }, order_by=testata_scontrino.c.id)