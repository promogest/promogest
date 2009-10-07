# -*- coding: utf-8 -*-

"""
 Promogest
 Copyright (C) 2005-2008 by Promotux Informatica - http://www.promotux.it/
 Author: Andrea Argiolas <andrea@promotux.it>
 Author: Francesco Meloni <francesco@promotux.it>
 License: GNU GPLv2
 """

import gtk
import gobject
from GladeWidget import GladeWidget
from AnagraficaComplessa import Anagrafica, AnagraficaFilter, AnagraficaHtml, AnagraficaReport, AnagraficaEdit
from AnagraficaArticoliEdit import AnagraficaArticoliEdit
from promogest import Environment

import promogest.dao.Articolo
from promogest.dao.Articolo import Articolo
import promogest.dao.Fornitura

from utils import *
from utilsCombobox import *
if "PromoWear" in Environment.modulesList:
    from promogest.modules.PromoWear.ui.PromowearUtils import *
    from promogest.modules.PromoWear.dao.ArticoloTagliaColore import ArticoloTagliaColore
    from promogest.modules.PromoWear.dao.GruppoTaglia import GruppoTaglia
    from promogest.modules.PromoWear.dao.Taglia import Taglia
    from promogest.modules.PromoWear.dao.Colore import Colore
    from promogest.modules.PromoWear.dao.AnnoAbbigliamento import AnnoAbbigliamento
    from promogest.modules.PromoWear.ui import AnagraficaArticoliPromoWearExpand

class AnagraficaArticoli(Anagrafica):
    """ Anagrafica articoli """

    def __init__(self, aziendaStr=None):
        Anagrafica.__init__(self,
                            windowTitle='Promogest - Anagrafica articoli',
                            recordMenuLabel='_Articoli',
                            filterElement=AnagraficaArticoliFilter(self),
                            htmlHandler=AnagraficaArticoliHtml(self),
                            reportHandler=AnagraficaArticoliReport(self),
                            editElement=AnagraficaArticoliEdit(self),
                            aziendaStr=aziendaStr)
        checkCodBarOrphan = removeCodBarorphan()
        self.record_duplicate_menu.set_property('visible', True)

    def on_record_edit_activate(self, widget, path=None, column=None):
        dao = self.filter.getSelectedDao()
        if dao.cancellato:
            msg = "L'articolo risulta eliminato.\nSi desidera riattivare l'articolo ?"
            dialog = gtk.MessageDialog(self.getTopLevel(), gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                       gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                daoArticolo = Articolo().getRecord(id= dao.id)
                daoArticolo.cancellato = False
                daoArticolo.persist()

                # toglie l'evidenziatura rossa
                sel = self.anagrafica_filter_treeview.get_selection()
                (model, iterator) = sel.get_selected()
                model.set_value(iterator, 1, None)
            else:
                return
        Anagrafica.on_record_edit_activate(self, widget, path, column)

    def duplicate(self,dao):
        """ Duplica le informazioni relative ad un articolo scelto su uno nuovo (a meno del codice) """
        if dao is None:
            return

        self.editElement._duplicatedDaoId = dao.id
        self.editElement.dao = Articolo()

        if "PromoWear" in Environment.modulesList:
                # le varianti non si possono duplicare !!!
                #articoloTagliaColore = dao.articoloTagliaColore
                if dao.id_articolo_padre is not None:
                    msg = "Attenzione !\n\n Le varianti non sono duplicabili !"
                    dialog = gtk.MessageDialog(self.getTopLevel(), gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                            gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK, msg)
                    response = dialog.run()
                    dialog.destroy()
                    return

        #copia dei dati del vecchio articolo nel nuovo
        self.editElement.dao.denominazione = dao.denominazione
        self.editElement.dao.id_aliquota_iva = dao.id_aliquota_iva
        self.editElement.dao.id_famiglia_articolo = dao.id_famiglia_articolo
        self.editElement.dao.id_categoria_articolo = dao.id_categoria_articolo
        self.editElement.dao.id_unita_base = dao.id_unita_base
        self.editElement.dao.produttore = dao.produttore
        self.editElement.dao.unita_dimensioni = dao.unita_dimensioni
        self.editElement.dao.lunghezza = dao.lunghezza
        self.editElement.dao.larghezza = dao.larghezza
        self.editElement.dao.altezza = dao.altezza
        self.editElement.dao.unita_volume = dao.unita_volume
        self.editElement.dao.volume = dao.volume
        self.editElement.dao.unita_peso = dao.unita_peso
        self.editElement.dao.peso_lordo = dao.peso_lordo
        self.editElement.dao.id_imballaggio = dao.id_imballaggio
        self.editElement.dao.peso_imballaggio = dao.peso_imballaggio
        self.editElement.dao.stampa_etichetta = dao.stampa_etichetta
        self.editElement.dao.codice_etichetta = dao.codice_etichetta
        self.editElement.dao.descrizione_etichetta = dao.descrizione_etichetta
        self.editElement.dao.stampa_listino = dao.stampa_listino
        self.editElement.dao.descrizione_listino = dao.descrizione_listino
        self.editElement.dao.aggiornamento_listino_auto = dao.aggiornamento_listino_auto
        self.editElement.dao.timestamp_variazione = dao.timestamp_variazione
        self.editElement.dao.note = dao.note
        self.editElement.dao.url_immagine = dao.url_immagine
        self.editElement.dao.cancellato = dao.cancellato
        self.editElement.dao.sospeso = dao.sospeso
        self.editElement.dao.id_stato_articolo = dao.id_stato_articolo
        self.editElement.dao.quantita_minima = dao.quantita_minima

        if self.editElement._codiceByFamiglia:
            self.editElement.dao.codice = promogest.dao.Articolo.getNuovoCodiceArticolo(idFamiglia=dao.id_famiglia_articolo)
        else:
            self.editElement.dao.codice = promogest.dao.Articolo.getNuovoCodiceArticolo(idFamiglia=None)

        self.editElement.setVisible(True)
        self.editElement._refresh()

        msg = 'Si desidera duplicare anche tutti i listini dell\' articolo scelto ?'
        dialog = gtk.MessageDialog(self.editElement.dialogTopLevel,
                                   gtk.DIALOG_MODAL
                                   | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_QUESTION,
                                   gtk.BUTTONS_YES_NO, msg)

        response = dialog.run()
        dialog.destroy()
        if response != gtk.RESPONSE_YES:
            self.editElement._duplicatedDaoId = None


class AnagraficaArticoliFilter(AnagraficaFilter):
    """ Filtro per la ricerca nell'anagrafica degli articoli """

    def __init__(self, anagrafica):
        AnagraficaFilter.__init__(self,
                                  anagrafica,
                                  'anagrafica_articoli_filter_table',
                                  #'anagrafica_articoli_filter_vbox',
                                  gladeFile='_anagrafica_articoli_elements.glade')
        self._widgetFirstFocus = self.denominazione_filter_entry
        self.ricerca_avanzata_articoli_filter_vbox.set_no_show_all(True)
        self.ricerca_avanzata_articoli_filter_vbox.hide()
        self.ricerca_semplice_articoli_filter_vbox.show()

    def draw(self):
        treeview = self._anagrafica.anagrafica_filter_treeview

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Codice', renderer, text=2, background=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(True)
        column.connect("clicked", self._changeOrderBy, (None,Articolo.codice))
        column.set_resizable(True)
        column.set_expand(False)
        column.set_min_width(100)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Descrizione', renderer, text=3, background=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(True)
        column.connect("clicked", self._changeOrderBy, (None,Articolo.denominazione))
        column.set_resizable(True)
        column.set_expand(True)
        column.set_min_width(100)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Produttore', renderer, text=4, background=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(True)
        column.connect("clicked", self._changeOrderBy, (None,Articolo.produttore))
        column.set_resizable(True)
        column.set_expand(False)
        column.set_min_width(100)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Codice a barre', renderer, text=5, background=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(True)
        from promogest.dao.CodiceABarreArticolo import CodiceABarreArticolo
        column.connect("clicked", self._changeOrderBy, (CodiceABarreArticolo,CodiceABarreArticolo.codice))
        column.set_resizable(True)
        column.set_expand(False)
        column.set_min_width(100)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Codice articolo fornitore', renderer, text=6, background=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(True)
        from promogest.dao.Fornitura import Fornitura
        column.connect("clicked", self._changeOrderBy, (Fornitura,Fornitura.codice_articolo_fornitore))
        column.set_resizable(True)
        column.set_expand(False)
        column.set_min_width(100)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Famiglia', renderer, text=7, background=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(True)
        from promogest.dao.FamigliaArticolo import FamigliaArticolo
        column.connect("clicked", self._changeOrderBy, (FamigliaArticolo,FamigliaArticolo.denominazione))
        column.set_resizable(True)
        column.set_expand(False)
        column.set_min_width(100)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Categoria', renderer, text=8, background=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(True)
        from promogest.dao.CategoriaArticolo import CategoriaArticolo
        column.connect("clicked", self._changeOrderBy, (CategoriaArticolo,CategoriaArticolo.denominazione))
        column.set_resizable(True)
        column.set_expand(False)
        column.set_min_width(100)
        treeview.append_column(column)
        if "PromoWear" in Environment.modulesList:
            AnagraficaArticoliPromoWearExpand.treeViewExpand(self, treeview, renderer)
        else:
            self._treeViewModel = gtk.ListStore(object, str, str, str, str, str, str, str, str)
            self.promowear_filter_frame.destroy()
        treeview.set_search_column(2)

        self._anagrafica.anagrafica_filter_treeview.set_model(self._treeViewModel)
        self.id_famiglia_articolo_filter_combobox.set_wrap_width(Environment.conf.combo_columns)
        self.id_categoria_articolo_filter_combobox.set_wrap_width(Environment.conf.combo_columns)

        self.clear()


    def _refresh_filter_comboboxes(self, widget=None):
        self.refresh()


    def clear(self):
        # Annullamento filtro
        self.denominazione_filter_entry.set_text('')
        self.codice_filter_entry.set_text('')
        self.codice_a_barre_filter_entry.set_text('')
        #self.url_articolo_entry.set_text('')
        self.codice_articolo_fornitore_filter_entry.set_text('')
        self.produttore_filter_entry.set_text('')
        fillComboboxFamiglieArticoli(self.id_famiglia_articolo_filter_combobox, filter=True)
        fillComboboxCategorieArticoli(self.id_categoria_articolo_filter_combobox, True)
        fillComboboxStatiArticoli(self.id_stato_articolo_filter_combobox, True)
        self.id_famiglia_articolo_filter_combobox.set_active(0)
        self.id_categoria_articolo_filter_combobox.set_active(0)
        self.id_stato_articolo_filter_combobox.set_active(0)
        self.cancellato_filter_checkbutton.set_active(False)
        if "PromoWear" in Environment.modulesList:
            AnagraficaArticoliPromoWearExpand.clear(self)
        self.refresh()


    def refresh(self):
        # Aggiornamento TreeView

        denominazione = prepareFilterString(self.denominazione_filter_entry.get_text())
        produttore = prepareFilterString(self.produttore_filter_entry.get_text())
        codice = prepareFilterString(self.codice_filter_entry.get_text())
        codiceABarre = prepareFilterString(self.codice_a_barre_filter_entry.get_text())
        codiceArticoloFornitore = prepareFilterString(self.codice_articolo_fornitore_filter_entry.get_text())
        idFamiglia = findIdFromCombobox(self.id_famiglia_articolo_filter_combobox)
        idCategoria = findIdFromCombobox(self.id_categoria_articolo_filter_combobox)
        idStato = findIdFromCombobox(self.id_stato_articolo_filter_combobox)
        if self.cancellato_filter_checkbutton.get_active():
            cancellato = False
        else:
            cancellato = True
        self.filterDict = { "denominazione":denominazione,
                            "codice":codice,
                            "codiceABarre":codiceABarre,
                            "codiceArticoloFornitore":codiceArticoloFornitore,
                            "produttore":produttore,
                            "idFamiglia":idFamiglia,
                            "idCategoria":idCategoria,
                            "idStato":idStato,
                            "cancellato":cancellato}

        if "PromoWear" in Environment.modulesList:
            AnagraficaArticoliPromoWearExpand.refresh(self)
        
        def filterCountClosure():
            return Articolo().count(filterDict = self.filterDict)

        self._filterCountClosure = filterCountClosure

        self.numRecords = self.countFilterResults()
        self._refreshPageCount()

        # Let's save the current search as a closure
        def filterClosure(offset, batchSize):
            return Articolo().select(orderBy=self.orderBy,
                                        join=self.join,
                                        offset=offset,
                                        batchSize=batchSize,
                                        filterDict=self.filterDict)

        self._filterClosure = filterClosure

        arts = self.runFilter()
        self._treeViewModel.clear()
        for a in arts:
            modelRowPromoWear = []
            modelRow = []
            col = None
            if a.cancellato:
                col = 'red'
            modelRow = [a,col,(a.codice or ''),(a.denominazione or ''),
                        (a.produttore or ''),(a.codice_a_barre or ''),
                        (a.codice_articolo_fornitore or ''),
                        (a.denominazione_famiglia or ''),
                        (a.denominazione_categoria or '')]
            if "PromoWear" in Environment.modulesList:
                modelRowPromoWear = [(a.denominazione_gruppo_taglia or ''),
                                    (a.denominazione_modello or ''),
                                    (a.denominazione_taglia or ''),
                                    (a.denominazione_colore or ''),
                                    (a.anno or ''),
                                    (a.stagione or ''),
                                    (a.genere or '')]
            if modelRowPromoWear:
                self._treeViewModel.append(modelRow +modelRowPromoWear)
            else:
                self._treeViewModel.append(modelRow)


    def on_taglie_colori_filter_combobox_changed(self, combobox):
        AnagraficaArticoliPromoWearExpand.on_taglie_colori_filter_combobox_changed(self,combobox)


class AnagraficaArticoliHtml(AnagraficaHtml):
    def __init__(self, anagrafica):
        AnagraficaHtml.__init__(self, anagrafica,
                                'articolo',
                                'Dettaglio articolo')


class AnagraficaArticoliReport(AnagraficaReport):
    def __init__(self, anagrafica):
        AnagraficaReport.__init__(self, anagrafica=anagrafica,
                                  description='Elenco degli articoli',
                                  defaultFileName='articoli',
                                  htmlTemplate='articoli',
                                  sxwTemplate='articoli')