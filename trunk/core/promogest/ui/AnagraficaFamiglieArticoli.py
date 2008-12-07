# -*- coding: iso-8859-15 -*-

"""
 Promogest
 Copyright (C) 2005-2008 by Promotux Informatica - http://www.promotux.it/
 Author: Andrea Argiolas <andrea@promotux.it>
 Author: Francesco Meloni <francesco@promotux.it>
 License: GNU GPLv2
 """

import gtk
import gobject

from AnagraficaComplessa import Anagrafica, AnagraficaFilter, AnagraficaHtml, AnagraficaReport, AnagraficaEdit

from promogest import Environment
from promogest.dao.Dao import Dao
import promogest.dao.FamigliaArticolo
from promogest.dao.FamigliaArticolo import FamigliaArticolo

from utils import *
from utilsCombobox import *



class AnagraficaFamiglieArticoli(Anagrafica):
    """ Anagrafica famiglie degli articoli """

    def __init__(self):
        Anagrafica.__init__(self,
                            windowTitle='Promogest - Anagrafica famiglie articoli',
                            recordMenuLabel='_Famiglie',
                            filterElement=AnagraficaFamiglieArticoliFilter(self),
                            htmlHandler=AnagraficaFamiglieArticoliHtml(self),
                            reportHandler=AnagraficaFamiglieArticoliReport(self),
                            editElement=AnagraficaFamiglieArticoliEdit(self))
        self.hideNavigator()



class AnagraficaFamiglieArticoliFilter(AnagraficaFilter):
    """ Filtro per la ricerca nell'anagrafica delle famiglie articoli """

    def __init__(self, anagrafica):
        AnagraficaFilter.__init__(self,
                                  anagrafica,
                                  'anagrafica_famiglie_articoli_filter_table',
                                  gladeFile='_anagrafica_famiglie_articoli_elements.glade')
        self._widgetFirstFocus = self.denominazione_filter_entry
        self.orderBy = 'denominazione'


    def draw(self):
        # Colonne della Treeview per il filtro
        treeview = self._anagrafica.anagrafica_filter_treeview

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Codice', renderer, text=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Descrizione breve', renderer, text=2)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Descrizione', renderer, text=3)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(True)
        treeview.append_column(column)

        renderer = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn('', renderer, pixbuf=4)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(False)
        column.set_expand(False)
        treeview.append_column(column)

        treeview.set_search_column(1)

        self._treeViewModel = gtk.TreeStore(gobject.TYPE_PYOBJECT, str, str, str, gtk.gdk.Pixbuf)
        self._anagrafica.anagrafica_filter_treeview.set_model(self._treeViewModel)

        self.refresh()


    def clear(self):
        # Annullamento filtro
        self.codice_filter_entry.set_text('')
        self.denominazione_filter_entry.set_text('')
        self.refresh()


    def refresh(self):
        # Aggiornamento TreeView
        def filterCountClosure():
            return FamigliaArticolo().count()

        self._filterCountClosure = filterCountClosure

        self.numRecords = self.countFilterResults()

        self._refreshPageCount()

        # Let's save the current search as a closure
        def filterClosure(offset, batchSize):
            return  FamigliaArticolo().select(offset=None,batchSize=None)

        self._filterClosure = filterClosure

        fams = self.runFilter()

        self._treeViewModel.clear()


        def recurse_tree(id_padre, parent_iter=None, max_depth=None, ):
            if parent_iter is None :
                padre = None
                path = 0
                for row in self._treeViewModel:
                    if row[0].id == id_padre:
                        padre = self._treeViewModel.get_iter(path)
                    else:
                        iter = self._treeViewModel.get_iter(path)
                        if self._treeViewModel.iter_has_child(iter):
                            new_depth = self._treeViewModel.iter_n_children(iter) or 0
                            if new_depth > 0:
                                padre = recurse_tree(id_padre, iter, new_depth)
                    if padre is not None:
                        break
                    else:
                        path += 1
            else:
                padre = None
                child_index = 0
                #if self._treeViewModel.iter_has_child(parent_iter):
                while child_index < max_depth:
                    child_iter = self._treeViewModel.iter_nth_child(parent_iter, child_index)
                    if self._treeViewModel[child_iter][0].id == id_padre:
                        padre = child_iter
                        break
                    else:
                        if self._treeViewModel.iter_has_child(child_iter):
                            new_depth = self._treeViewModel.iter_n_children(parent_iter) or 0
                            if new_depth > 0:
                                padre = recurse_tree(id_padre, child_iter, new_depth)
                        if padre is not None:
                            break
                    child_index += 1
            return padre

        for f in fams:
            if f.id_padre is None:
                node = self._treeViewModel.append(None, (f,
                                                    (f.codice or ''),
                                                    (f.denominazione_breve or ''),
                                                    (f.denominazione or ''),
                                                    None))
        for f in fams:
            if f.id_padre is not None:
                padre = recurse_tree(f.id_padre)
                node = self._treeViewModel.append(padre, (f,
                                                    (f.codice or ''),
                                                    (f.denominazione_breve or ''),
                                                    (f.denominazione or ''),
                                                    None))

        self._anagrafica.anagrafica_filter_treeview.collapse_all()

        denominazione = emptyStringToNone(self.denominazione_filter_entry.get_text())
        codice = emptyStringToNone(self.codice_filter_entry.get_text())
        if not (denominazione is None) or not (codice is None):
            self._treeViewModel.foreach(self.selectFilter, (denominazione, codice))


    def selectFilter(self, model, path, iter, (denominazione, codice)):
        #Seleziona elementi che concordano con il filtro
        c = model.get_value(iter, 0)
        found = False
        if denominazione is not None:
            found = (denominazione.upper() in c.denominazione.upper())
        if codice is not None:
            found = found or (codice.upper() in c.codice.upper())
        if found:
            image = gtk.Image()
            anagPixbuf = image.render_icon(gtk.STOCK_GO_BACK,
                                           gtk.ICON_SIZE_BUTTON)
            model.set_value(iter, 4, anagPixbuf)
            self._anagrafica.anagrafica_filter_treeview.expand_to_path(path)
        else:
            model.set_value(iter, 4, None)



class AnagraficaFamiglieArticoliHtml(AnagraficaHtml):
    def __init__(self, anagrafica):
        AnagraficaHtml.__init__(self, anagrafica, 'famiglia_articolo',
                                'Informazioni sulla famiglia articoli')



class AnagraficaFamiglieArticoliReport(AnagraficaReport):
    def __init__(self, anagrafica):
        AnagraficaReport.__init__(self, anagrafica=anagrafica,
                                  description='Elenco delle famiglie articoli',
                                  defaultFileName='famiglie_articoli',
                                  htmlTemplate='famiglie_articoli',
                                  sxwTemplate='famiglie_articoli')



class AnagraficaFamiglieArticoliEdit(AnagraficaEdit):
    """ Modifica un record dell'anagrafica delle famiglie articoli """

    def __init__(self, anagrafica):
        AnagraficaEdit.__init__(self,
                                anagrafica,
                                'anagrafica_famiglie_articoli_detail_table',
                                'Dati famiglia articolo',
                                gladeFile='_anagrafica_famiglie_articoli_elements.glade')
        self._widgetFirstFocus = self.codice_entry


    def draw(self):
        #Popola combobox famiglie articoli
        fillComboboxFamiglieArticoli(self.id_padre_combobox)


    def setDao(self, dao):
        if dao is None:
            # Crea un nuovo Dao vuoto
            self.dao = FamigliaArticolo()
        else:
            # Ricrea il Dao con una connessione al DBMS SQL
            self.dao = FamigliaArticolo().getRecord(id = dao.id)
        self._refresh()


    def _refresh(self):
        self.codice_entry.set_text(self.dao.codice or '')
        self.denominazione_entry.set_text(self.dao.denominazione or '')
        self.denominazione_breve_entry.set_text(self.dao.denominazione_breve or '')
        fillComboboxFamiglieArticoli(self.id_padre_combobox, ignore=[self.dao.id])
        findComboboxRowFromId(self.id_padre_combobox, self.dao.id_padre)


    def saveDao(self):
        if (self.codice_entry.get_text() == ''):
            obligatoryField(self.dialogTopLevel, self.codice_entry)
            self.dao.codice = omogeneousCode(section="Famiglie", string=self.dao.codice )

        if (self.denominazione_entry.get_text() == ''):
            obligatoryField(self.dialogTopLevel, self.denominazione_entry)

        if (self.denominazione_breve_entry.get_text() == ''):
            obligatoryField(self.dialogTopLevel, self.denominazione_breve_entry)

        self.dao.codice = self.codice_entry.get_text()
        self.dao.denominazione = self.denominazione_entry.get_text()
        self.dao.denominazione_breve =self.denominazione_breve_entry.get_text()
        self.dao.id_padre = findIdFromCombobox(self.id_padre_combobox)
        self.dao.persist()
