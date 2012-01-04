# -*- coding: utf-8 -*-

#    Copyright (C) 2005-2012 by Promotux
#                        di Francesco Meloni snc - http://www.promotux.it/

#    Author: Francesco Marella <francesco.marella@gmail.com>

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

from promogest.ui.AnagraficaSemplice import Anagrafica, AnagraficaDetail, AnagraficaFilter
from promogest.modules.ADR.dao.Galleria import Galleria
from promogest.ui.utils import *


class AnagraficaGalleria(Anagrafica):
    """ Anagrafica galleria """

    def __init__(self):
        Anagrafica.__init__(self, _('Promogest - Anagrafica galleria'),
                            _('_Galleria'),
                            AnagraficaGalleriaFilter(self),
                            AnagraficaGalleriaDetail(self))


    def draw(self):
        self.filter.denominazione_column.get_cells()[0].set_data('max_length', 200)
        self._treeViewModel = self.filter.filter_listore
        self.refresh()


    def refresh(self):
        # Aggiornamento TreeView
        denominazione = prepareFilterString(self.filter.denominazione_filter_entry.get_text())
        self.numRecords = Galleria().count(denominazione=denominazione)

        self._refreshPageCount()

        # Let's save the current search as a closure
        def filterClosure(offset, batchSize):
            return Galleria().select(denominazione=denominazione,
                                            orderBy=self.orderBy,
                                            offset=self.offset,
                                            batchSize=self.batchSize)

        self._filterClosure = filterClosure

        cats = self.runFilter()

        self._treeViewModel.clear()

        for c in cats:
            self._treeViewModel.append((c,
                                        (c.denominazione or ''),
                                        ))


class AnagraficaGalleriaFilter(AnagraficaFilter):
    """ Filtro per la ricerca nell'anagrafica galleria """

    def __init__(self, anagrafica):
        AnagraficaFilter.__init__(self,
                                  anagrafica,
                                  'anagrafica_galleria_filter_table',
                                  gladeFile='ADR/gui/_anagrafica_galleria_elements.glade',
                                  module=True)
        self._widgetFirstFocus = self.denominazione_filter_entry



    def clear(self):
        # Annullamento filtro
        self.denominazione_filter_entry.set_text('')
        self.denominazione_filter_entry.grab_focus()
        self._anagrafica.refresh()



class AnagraficaGalleriaDetail(AnagraficaDetail):
    """ Dettaglio dell'anagrafica galleria """

    def __init__(self, anagrafica):
        AnagraficaDetail.__init__(self,
                                  anagrafica,
                                  gladeFile='ADR/gui/_anagrafica_galleria_elements.glade',
                                  module=True)

    def setDao(self, dao):
        if dao is None:
            self.dao = Galleria()
            self._anagrafica._newRow((self.dao, ''))
            self._refresh()
        else:
            self.dao = dao
        return self.dao

    def updateDao(self):
        if self.dao:
            self.dao = Galleria().getRecord(id=self.dao.id)
        self._refresh()

    def _refresh(self):
        sel = self._anagrafica.anagrafica_treeview.get_selection()
        (model, iterator) = sel.get_selected()
        if iterator and self.dao:
            model.set_value(iterator, 0, self.dao)
            model.set_value(iterator, 1, self.dao.denominazione)

    def saveDao(self):
        sel = self._anagrafica.anagrafica_treeview.get_selection()
        (model, iterator) = sel.get_selected()
        denominazione = model.get_value(iterator, 1) or ''
        if (denominazione == ''):
            obligatoryField(self._anagrafica.getTopLevel(), self._anagrafica.anagrafica_treeview)
        self.dao.denominazione = denominazione
        self.dao.persist()
