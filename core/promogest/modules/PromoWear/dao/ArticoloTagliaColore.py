# -*- coding: iso-8859-15 -*-

# Promogest
#
# Copyright (C) 2005-2008 by Promotux Informatica - http://www.promotux.it/
# Author: Andrea Argiolas <andrea@promotux.it>
# Author: Francesco Meloni <francesco@promotux.it>


from sqlalchemy import *
from sqlalchemy.orm import *
from promogest.Environment import *
from promogest.dao.Dao import Dao
from promogest.modules.PromoWear.dao.GruppoTaglia import GruppoTaglia
from promogest.modules.PromoWear.dao.Taglia import Taglia
from promogest.modules.PromoWear.dao.Colore import Colore
from promogest.modules.PromoWear.dao.AnnoAbbigliamento import AnnoAbbigliamento
from promogest.modules.PromoWear.dao.StagioneAbbigliamento import StagioneAbbigliamento
from promogest.modules.PromoWear.dao.GenereAbbigliamento import GenereAbbigliamento
#from promogest.modules.PromoWear.dao.ArticoloPromowear import ArticoloPromowear



class ArticoloTagliaColore(Dao):

    def __init__(self, arg=None,isList=False, id=None):
        Dao.__init__(self, entity=self.__class__, isList=isList, id=id)


    def _getGruppoTaglia(self):
        """ Restituisce il Dao GruppoTaglia collegato al Dao ArticoloTagliaColore """
        if self.id_gruppo_taglia is None:
            return None
        return GruppoTaglia(self._connection, self.id_gruppo_taglia)

    gruppoTaglia = property(_getGruppoTaglia)


    def _getTaglia(self):
        """ Restituisce il Dao Taglia collegato al Dao ArticoloTagliaColore """
        if self.id_taglia is None:
            return None
        return Taglia(self._connection, self.id_taglia)

    taglia = property(_getTaglia)


    def _getColore(self):
        """ Restituisce il Dao Colore collegato al Dao ArticoloTagliaColore """
        if self.id_colore is None:
            return None
        return Colore(self._connection, self.id_colore)

    colore = property(_getColore)


    def articoloPadre(self):
        """ Restituisce il Dao Articolo padre del Dao ArticoloTagliaColore """
        #we can't make a property because of recusion articolotagliacolore - articolo
        #resolveProperties goes in loop
        if self.id_articolo_padre is None:
            return None
        #from Articolo import Articolo
        return Articolo(id=self.id_articolo_padre).getRecord()



    def articolo(self):
        """ Restituisce il Dao Articolo collegato al Dao ArticoloTagliaColore """
        #we can't make a property because of recusion articolotagliacolore - articolo
        #resolveProperties goes in loop
        if self.id_articolo is None:
            return None
        from Articolo import Articolo
        return Articolo(Environment.connection, self.id_articolo)


    #def delete(self, conn=None):
        #""" Elimina fisicamente o logicamente un articolo """
        #def isMovimentato(id):
            #"""Verifica se l'articolo e' presente almeno una riga di movimento/documento"""
            #queryString = ('SELECT COUNT(*) FROM ' +
                           #Environment.connection._schemaAzienda + '.riga ' +
                           #'WHERE id_articolo = ' + str(id_articolo))
            #argList = []
            #self._connection._cursor.execute(queryString, argList)
            #res = Environment.connection._cursor.fetchall()

            #return res[0][0] > 0


        #conn = conn or self._connection

        #if conn is None:
        #    conn = Environment.connection

        if conn is None:
            self.raiseException(NotImplementedError('Object is read-only '
                                                    + '(no connection has '
                                                    + 'been associated)'))

        # se l'articolo e' presente tra le righe di un movimento o documento
        # si esegue la cancellazione logica, altrimenti fisica

        if self.id_articolo_padre is not None:
            articolo = self.articolo
            if articolo is not None:
                if isMovimentato(self.id_articolo):
                    articolo.cancellato = True
                    articolo.persist(conn=conn)
                else:
                    articolo.delete(self, conn=conn)



    def filter_values(self,k,v):
        if k =='idArticolo':
            dic= {k:articolotagliacolore.c.id_articolo ==v}
        elif k == "idTaglia":
            dic = {k:articolotagliacolore.c.id_taglia ==v}
        elif k == "idGruppoTaglia":
            dic = {k:articolotagliacolore.c.id_gruppo_taglia ==v}
        elif k == "idColore":
            dic = {k:articolotagliacolore.c.id_colore ==v}
        elif k == "idArticoloPadre":
            dic = {k:articolotagliacolore.c.id_articolo_padre ==v}
        return  dic[k]

articolo=Table('articolo',params['metadata'],schema = params['schema'],autoload=True)
articolotagliacolore=Table('articolo_taglia_colore',params['metadata'],schema = params['schema'],autoload=True)

#j = join(articolo, articolotagliacolore, onclause=articolo.c.id)
#j = join(articolo, articolotagliacolore, onclause=articolo.c.id==articolotagliacolore.c.id_articolo)
std_mapper = mapper(ArticoloTagliaColore, articolotagliacolore,properties={
    #'id':[articolo.c.id, articolotagliacolore.c.id_articolo],
    "GT":relation(GruppoTaglia,primaryjoin=
                    (GruppoTaglia.id==articolotagliacolore.c.id_gruppo_taglia), backref="ATCGT"),
    "TA":relation(Taglia,primaryjoin=
                    (Taglia.id==articolotagliacolore.c.id_taglia), backref="ATCTA"),
    "CO":relation(Colore,primaryjoin=
                    (Colore.id==articolotagliacolore.c.id_colore), backref="ATCCO"),
    "AA":relation(AnnoAbbigliamento,primaryjoin=
                    (AnnoAbbigliamento.id==articolotagliacolore.c.id_anno), backref="ATCAA"),
    "SA":relation(StagioneAbbigliamento,primaryjoin=
                    (StagioneAbbigliamento.id==articolotagliacolore.c.id_stagione), backref="ATCSA"),
    "GA":relation(GenereAbbigliamento,primaryjoin=
                    (GenereAbbigliamento.id==articolotagliacolore.c.id_genere), backref="ATCGA"),
        },
                order_by=articolotagliacolore.c.id_taglia)


