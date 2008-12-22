# -*- coding: utf-8 -*-

# Promogest
#
# Copyright (C) 2008 by Promotux Informatica - http://www.promotux.it/
# Author: Dr astico (Pinna Marco) <marco@promotux.it>
# Author: Francesco Meloni <francesco@promotux.it>

import gtk
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.interfaces import ConnectionProxy
from promogest.Environment import *
import datetime
import time
from promogest.ui.GtkExceptionHandler import GtkExceptionHandler
a = datetime.datetime
import logging


class Dao(object):
    """Astrazione generica di ciò che fu il vecchio dao basata su sqlAlchemy"""
    def __init__(self, entity=None, exceptionHandler=None):
        self.session = params["session"]
        self.metadata = params["metadata"]
        self.numRecords = None
        self.DaoModule = entity.__class__
        self._exceptionHandler = exceptionHandler
        #ch = logging.basicConfig()
        #ch = logging.StreamHandler()
        #logger = logging.getLogger('sqlalchemy.orm')
        #logger.setLevel(logging.DEBUG)
        #ch.setLevel(logging.DEBUG)
        #formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        #ch.setFormatter(formatter)
        #logger.addHandler(ch)
        #logger2.addHandler(ch)
        #"application" code

    def getRecord(self,id=None):
        if id:
            _record = self.session.query(self.DaoModule).get(id)
        else:
            return None
        return _record

    def select(self, orderBy=None, distinct=False, groupBy=None,join=None, offset=0,
                batchSize=15,complexFilter=None,isList = "all", **kwargs):
        if complexFilter:
            filter = complexFilter
        else:
            filter= self.prepareFilter(kwargs)
        try:
            dao = self.session.query(self.DaoModule)
            if join:
                dao = dao.join(join)
            if filter:
                dao = dao.filter(filter)
            if orderBy:
                dao = dao.order_by(orderBy)
            if batchSize:
                dao = dao.limit(batchSize)
            if offset:
                dao = dao.offset(offset)
            if distinct:
                dao = dao.distinct()
            if isList == "all":
                self.record = dao.all()
            elif isList == "one":
                self.record = dao.one()
            elif isList =="first":
                self.record = dao.first()
            elif isList == "noList":
                self.record = dao
            return self.record
        except Exception, e:
            self.raiseException(e)

    def count(self, complexFilter=None,distinct =None, **kwargs):
        _numRecords = 0
        if complexFilter:
            filter = complexFilter
        else:
            filter= self.prepareFilter(kwargs)
        try:
            dao = self.session.query(self.DaoModule)
            if filter:
                dao = dao.filter(filter)
            if distinct:
                dao = dao.distinct()
            _numRecords = dao.count()
            if _numRecords > 0:
                self.numRecords = _numRecords
            return self.numRecords
        except Exception, e:
            self.raiseException(e)

    def commit(self):
        #params["session"].add(self)
        params["session"].commit()
        return True

    def persist(self,multiple=False, record=True):
        #try:
        if record:
            #try:
                params["session"].add(self)
                params["session"].commit()
                self.saveToAppLogTable(data=self)
                else:
                    self.saveToAppLogTable(data=self,message=message, whatstr=pk)
                return True
            #except Exception,e:
                #msg = """ATTENZIONE ERRORE nel salvataggio dei dati
#probabilmente a causa di un dato mancante:
#Qui sotto viene riportato l'errore di sistema:
#%s
#( normalmente il campo in errore è tra "virgolette")
#Dovrebbe essere sufficiente reinserire i dato nella loro
#completezza o integrita """ %e
                #overDialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL
                                                #| gtk.DIALOG_DESTROY_WITH_PARENT,
                                                    #gtk.MESSAGE_ERROR,
                                                    #gtk.BUTTONS_CANCEL, msg)
                #response = overDialog.run()
                #overDialog.destroy()
                #params["session"].rollback()
                #return False

    def delete(self, multiple=False, record = True ):
        try:
            if record:
                #try:
                params['session'].delete(self)
                params["session"].commit()
                
                return True
        except Exception,e:
            msg = """ATTENZIONE ERRORE nella cancellazione dei dati
probabilmente a causa di un dato errato o di una
procedura non correttamente gestita:
Qui sotto viene riportato l'errore di sistema:
%s
( normalmente il campo in errore è tra "virgolette")
""" %e
            overDialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL
                                                | gtk.DIALOG_DESTROY_WITH_PARENT,
                                                    gtk.MESSAGE_ERROR,
                                                    gtk.BUTTONS_CANCEL, msg)
            response = overDialog.run()
            overDialog.destroy()
            params["session"].rollback()
            return False

    def _resetId(self):
        self.id = None

    def sameRecord(self, dao):
        """
        Check whether this Dao represents the same SQL DBMS record of
        the given Dao
        """
        if dao and self:
            return (self.__hash__ == dao.__hash__ )
        return True

    def dictionary(self, complete=False):
        """
        Return a dictionary containing DAO data.  'complete' tells
        whether we should return *all* the data, even the one that's
        not SQL-related
        """
        sqlDict = {}
        for k in self.__dict__.keys():
            sqlDict[k] = getattr(self, k)

        if not complete:
            return sqlDict

        props = {}
        for att in self.__class__.__dict__.keys():
            if isinstance(getattr(self.__class__, att), property):
                value = getattr(self.__class__, att).__get__(self)
                if isinstance(value, list):
                    # Let's recurse
                    value = [d.dictionary(complete=complete) for d in value
                             if isinstance(d, Dao)]
                    #if isinstance(value, Dao):
                    for xx in value:
                        for k,v in xx.items():
                            if isinstance(v.__class__, Dao):
                                xx[k] = v
                props[att] = value

        attrs = {}
        for att in (x for x in self.__dict__.keys() if x not in sqlDict.keys()):
            # Let's filter boring stuff
            if '__' in att: # Private data
                continue
            elif att[0]=='_':
                continue
            attrs[att] = getattr(self, att)

        sqlDict.update(props)
        sqlDict.update(attrs)

        return sqlDict

    def saveToAppLogTable(self, data):
            if params["session"].dirty:
                message = "UPDATE"
            elif params["session"].new:
                message = "INSERT"
            elif not params["session"].dirty and not params["session"].new:
                message = "UNKNOWN"
            mapper = object_mapper(self)
            params["session"].commit()
            pk = mapper.primary_key_from_instance(self)
            if len(pk) ==1:
                self.saveToAppLogTable(data=self,message=message, whatid=pk[0])
            else:
                self.saveToAppLogTable(data=self,message=message, whatstr=pk)
        when = datetime.datetime.now()
        what = data
        where = params['schema']
        message = message
        #userid
        whoID = params['usernameLoggedList'][0]
        utentedb = params['usernameLoggedList'][2]
        utente = params['usernameLoggedList'][1]
        # Failed? ...
        how = how
        if how: how = "I"
        else: hoW = "E"
        whatid = whatid
        whatstr = whatstr
        appLogTable = Table('application_log', params['metadata'], autoload=True, schema=params['mainSchema'])
        app = appLogTable.insert()
        app.execute(id_utente=whoID,
                    utentedb = utentedb,
                    schema = where,
                    level=how,
                    object = str(data),
                    message = message,
                    value = whatid,
                    strvalue = whatstr)
        print "%s : %s %s fatta su schema %s  da %s" %(str(when),message,str(data),str(where),utente)


    def resolveProperties(self):
        """
        Resolve all the object properties.  This method expects all
        the properties to keep an internal cache that will avoid
        further SQL DBMS accesses.
        """
        pass

    def raiseException(self, exception):
        """
        Pump an exception instance or type through the object exception
        handler (if any)
        """
        #if self._exceptionHandler is not None:
        GtkExceptionHandler().handle(exception)

        # Now let's raise the exception, in order to stop further processing
        #raise exception

    def prepareFilter(self, kwargs):
        filter_parameters = []
        for key,value in kwargs.items():
            if value:
                if type(value)==list:
                    filter_parameters.append((value,key,"Lista"))
                else:
                    filter_parameters.append((value,key,"s"))
        if filter_parameters != []:
            #if __debug__: print "FILTER PARAMETERS:",self.DaoModule.__name__, filter_parameters
            filter = self.getFilter(filter_parameters)
            return filter
        return

    def getFilter(self,filter_parameters):
        filters = []
        for elem in filter_parameters:
            if elem[0] and elem[2]=="Lista":
                arg= self.filter_values(str(elem[1]+"List"),elem[0])
            elif elem[0]:
                arg= self.filter_values(str(elem[1]),elem[0])
            filters.append(arg)
        return and_(*filters)
