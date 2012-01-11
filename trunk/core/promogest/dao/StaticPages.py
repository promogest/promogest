# -*- coding: utf-8 -*-

#    Copyright (C) 2005-2012 by Promotux
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


from sqlalchemy import *
from sqlalchemy.orm import *
from promogest.Environment import *
from promogest.dao.Dao import Dao
from promogest.modules.Multilingua.dao.Language import Language
from promogest.dao.User import User
from migrate import *

try:
    staticpage=Table('static_page',
        params['metadata'],
        schema = params['schema'],
        autoload=True)
except:
    if params["tipo_db"] == "sqlite":
        utenteFK ='utente.id'
        languageFK = 'language.id'
    else:
        utenteFK =params['mainSchema']+'.utente.id'
        languageFK =params['mainSchema']+'.language.id'

    staticpage= Table('static_page', params['metadata'],
            Column('id', Integer, primary_key=True),
            Column('title', String(200), nullable=False),
            Column('abstract', String(400), nullable=True),
            Column('body', Text, nullable=True),
            Column('imagepath', String(400), nullable=True),
            Column('publication_date', DateTime, nullable=True),
            Column('clicks', Integer),
            Column("permalink", String(500), nullable=True),
            Column('active', Boolean, default=0),
            Column('id_user', Integer,ForeignKey(utenteFK)),
            Column('id_language', Integer,ForeignKey(languageFK)),
            schema=params['schema']
            )
    staticpage.create(checkfirst=True)

if 'permalink' not in [c.name for c in staticpage.columns]:
    col = Column('permalink', String(500), nullable=True)
    col.create(staticpage, populate_default=True)

class StaticPages(Dao):

    def __init__(self, req=None):
        Dao.__init__(self, entity=self)

    def filter_values(self,k,v):
        if k=='id_language':
            dic= {  k : staticpage.c.id_language == v}
        elif k == "titlePage":
            dic = { k: staticpage.c.title==v }
        elif k == "permalink":
            dic = { k: staticpage.c.permalink==v }
        return  dic[k]


std_mapper = mapper(StaticPages, staticpage, properties = {
        'lang' : relation(Language),
        'user' : relation(User) }, order_by=staticpage.c.id)
