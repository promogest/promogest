# -*- coding: utf-8 -*-

#    Copyright (C) 2005, 2006, 2007 2008, 2009, 2010 by Promotux
#                        di Francesco Meloni snc - http://www.promotux.it/

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


from promogest.lib.page import Page
from promogest.dao.CategoriaFornitore import CategoriaFornitore

def anagraficaCategoriaFornitore(req, action=None):
    """
    Funzione di gestione delle preview
    """
    def _list_(req, action=None):
        denominazione=None
        if req.form.to_dict():
            denominazione = req.form.get("denominazione")
        chiavi = {"denominazione" : denominazione}
        daos = CategoriaFornitore(req=req).select(batchSize=None, denominazione=denominazione)
        pageData = {'file' : "anagraficaSemplice",
                    "_dao_":"categoria_fornitore",
                    "name": "Categorie Fornitore",
                    "tree":"treeCategoriaFornitore",
                    "fkey":"fk_categoriafornitore",
                    "action":action,
                    "chiavi":chiavi,
                    "daos":daos,
                    "count":len(daos)}
        return Page(req).render(pageData)

    def __add__(req, action=None):
        id = req.form.get("id")
        denominazione = req.form.get("denominazione")
        if action == "add":
            dao = CategoriaFornitore()
        else:
            dao = CategoriaFornitore().getRecord(id=id)
        dao.denominazione = denominazione
        if denominazione:
            dao.persist()
        redirectUrl='/parametri/categoria_fornitore/list'
        return Page(req).redirect(redirectUrl)

    def __del__(req, action=None):
        id = req.form.get("idr")
        dao = CategoriaFornitore().getRecord(id=id)
        if dao:
            dao.delete()
        daos = CategoriaFornitore(req=req).select(batchSize=None)
        pageData = {'file' : "/tree/treeCategoriaFornitore",
                    "action":action,
                    "daos":daos,
                    "count":len(daos)}
        return Page(req).render(pageData)

    def __edit__(req, action=None):
        id = req.form.get("idr")
        dao = CategoriaFornitore().getRecord(id=id)
        pageData = {'file' : "/addedit/ae_categoriafornitore",
                    "action":action,
            "dao":dao}
        return Page(req).render(pageData)

    def __new__(req, action=None):
        pageData = {'file' : "/addedit/ae_categoriafornitore",
                    "_dao_":"categoria_fornitore",
                    "name": "Categoria Fornitore",
                    "tree":"treeCategoriaFornitore",
                    "action":action,
        }
        return Page(req).render(pageData)

    if action=="list":
        return _list_(req, action=action)
    elif action=="add" or action=="fromedit":
        return __add__(req, action=action)
    elif action=="delete":
        return __del__(req, action=action)
    elif action=="edit":
        return __edit__(req, action=action)
    elif action=="new":
        return __new__(req, action=action)
