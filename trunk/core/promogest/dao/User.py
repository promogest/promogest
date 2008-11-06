# -*- coding: utf-8 -*-

"""
 Promogest
 Copyright (C) 2005-2008 by Promotux Informatica - http://www.promotux.it/
 Author: Francesco Meloni <francesco@promotux.it>
 License: GNU GPLv2
"""

from promogest.lib.sqlalchemy import *
from promogest.lib.sqlalchemy.orm import *
from promogest.Environment import *
from Dao import Dao
from promogest.lib.sqlalchemy import and_, or_
from Role import Role
from Language import Language

class User(Dao):
    """ User class provides to make a Users dao which include more used"""

    def __init__(self, arg=None,isList=False, id=None):
        Dao.__init__(self, entity=self.__class__, isList=isList, id=id)

    def filter_values(self,k,v):
        if k == 'username':
            dic = {k:user.c.username == v}
        elif k == 'password':
            dic = {k:user.c.password == v}
        elif k == 'usern':
            dic = {k:user.c.username.ilike("%"+v+"%")}
        elif k == 'email':
            dic = {k:user.c.email.ilike("%"+v+"%")}
        elif k == 'role':
            dic = {k:user.c.id_role == v}
        elif k == 'active':
            dic = {k:user.c.active == v}
        return  dic[k]

    def _ruolo(self):
        if self.role: return self.role.name
        else: return ""
    ruolo = property(_ruolo)

    def _language(self):
        if self.lang: return self.lang.denominazione
        else: return ""
    lingua = property(_language)

user=Table('utente', params['metadata'],
    schema = params['mainSchema'],
    autoload=True)

std_mapper = mapper(User, user, properties={
    "role":relation(Role,primaryjoin=
            user.c.id_role==Role.id),
    'lang':relation(Language, primaryjoin=
            user.c.id_language==Language.id)
        }, order_by=user.c.username)
