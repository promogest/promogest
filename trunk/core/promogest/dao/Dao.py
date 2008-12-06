# -*- coding: utf-8 -*-

# Promogest
#
# Copyright (C) 2008 by Promotux Informatica - http://www.promotux.it/
# Author: Dr astico (Pinna Marco) <marco@promotux.it>
# Author: Francesco Meloni <francesco@promotux.it>


import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
#from sqlalchemy import and_, or_ , in_
from promogest.Environment import *
from UserDict import UserDict
from sqlalchemy.util import OrderedDict
import datetime
import string
from promogest.ui.GtkExceptionHandler import GtkExceptionHandler
a = datetime.datetime


class Dao(object):
    """Astrazione generica di ciò che fu il vecchio dao basata su sqlAlchemy"""
    def __init__(self, entity=None, isList=True, orderBy=None, exceptionHandler=None):
        #self.entity = entity
        self.orderBy = orderBy
        self.isList = isList
        self.session = params["session"]
        self.metadata = params["metadata"]
        self.numRecords = None
        self.DaoModule = entity
        self._exceptionHandler = exceptionHandler
        if isList:
            self.record = []

    def getRecord(self,id=None):
        if id:
            _record = self.session.query(self.DaoModule).get(id)
        else:
            raise Exception, " ATTENZIONE ID MANCANTE"
        return _record

    def select(self, orderBy=None,distinct=False,
                        offset=0, batchSize=15,complexFilter=None, **kwargs):
        if complexFilter:
            filter = complexFilter
        else:
            filter= self.prepareFilter(kwargs)
        try:
            if self.isList and complexFilter:
                if (filter is not None or not []) and (orderBy !=None):
                    self.record = self.session.query(self.DaoModule).filter(filter).order_by(orderBy).limit(batchSize).offset(offset).all()
                elif (filter is None or not []) and (orderBy !=None):
                    self.record = self.session.query(self.DaoModule).order_by(orderBy).offset(offset).limit(batchSize).all()
                elif (filter is not None or not []) and (orderBy ==None):
                    self.record = self.session.query(self.DaoModule).filter(filter).offset(offset).limit(batchSize).all()
            elif self.isList:
                if (filter is not None or not []) and (orderBy != None):
                    self.record = self.session.query(self.DaoModule).filter(filter).order_by(orderBy).limit(batchSize).offset(offset).all()
                elif (filter is  None or not []) and (orderBy != None):
                    self.record = self.session.query(self.DaoModule).order_by(orderBy).offset(offset).limit(batchSize).all()
                elif filter is not None or not []:
                    self.record = self.session.query(self.DaoModule).filter(filter).offset(offset).limit(batchSize).all()
                else:
                    self.record = self.session.query(self.DaoModule).offset(offset).limit(batchSize).all()
            return self.record
        except Exception, e:
            self.raiseException(e)

    def count(self, mapperType="select",complexFilter=None, **kwargs):
        _numRecords = 0
        try:
            if complexFilter:
                filter = complexFilter
            else:
                filter= self.prepareFilter(kwargs)
            if self.isList and complexFilter:
                if filter is not None or not []:
                    _numRecords = self.session.query(self.DaoModule).filter(filter).count()
                else:
                    _numRecords= self.session.query(self.DaoModule).distinct().count()
            elif self.isList:
                if filter is not None or not []:
                    _numRecords = self.session.query(self.DaoModule).filter(filter).count()
                else:
                    _numRecords = self.session.query(self.DaoModule).count()
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
        #import pdb
        #pdb.set_trace()
        if record:
            #try:
            params["session"].add(self)
            params["session"].commit()
             #params["session"].flush()
            return True

    def delete(self, multiple=False, record = True ):
        if record:
            #try:
            params['session'].delete(self)
            params["session"].commit()
            #params['session'].flush()
        return True

    def _resetId(self):
        self.id = None

    def sameRecord(self, dao, record=True):
        """
        Check whether this Dao represents the same SQL DBMS record of
        the given Dao
        """
        if record:
            return True
            #return (self.__class__ == dao.__class__) and (DaoDict(self) == DaoDict(dao))

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
            if __debug__: print "FILTER PARAMETERS:",self.DaoModule.__name__, filter_parameters
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
