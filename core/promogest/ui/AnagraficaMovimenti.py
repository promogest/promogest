# -*- coding: iso-8859-15 -*-

# Promogest
#
# Copyright (C) 2005 by Promotux Informatica - http://www.promotux.it/
# Author: Andrea Argiolas <andrea@promotux.it>
# Author: Dr astico <zoccolodignu@gmail.com>


import os
import gtk
import gobject
import datetime
from AnagraficaComplessa import Anagrafica, AnagraficaFilter, AnagraficaHtml, AnagraficaReport, AnagraficaEdit

from promogest import Environment
from promogest.dao.Dao import Dao
import promogest.dao.TestataMovimento
from promogest.dao.TestataMovimento import TestataMovimento
from promogest.dao.TestataDocumento import TestataDocumento
import promogest.dao.RigaMovimento
from promogest.dao.RigaMovimento import RigaMovimento
import promogest.dao.ScontoRigaMovimento
from promogest.dao.ScontoRigaMovimento import ScontoRigaMovimento
from promogest.dao.Articolo import Articolo
from utils import *
from utilsCombobox import *



class AnagraficaMovimenti(Anagrafica):
    """ Anagrafica movimenti """

    def __init__(self, idMagazzino=None, aziendaStr=None):
        self._magazzinoFissato = (idMagazzino <> None)
        self._idMagazzino=idMagazzino
        Anagrafica.__init__(self,
                            windowTitle='Promogest - Registrazione movimenti',
                            recordMenuLabel='_Movimenti',
                            filterElement=AnagraficaMovimentiFilter(self),
                            htmlHandler=AnagraficaMovimentiHtml(self),
                            reportHandler=AnagraficaMovimentiReport(self),
                            editElement=AnagraficaMovimentiEdit(self),
                            aziendaStr=aziendaStr)
        self.record_duplicate_menu.set_property('visible', True)
        self.records_file_export.set_sensitive(True)

    def LoadFieldsListData(self):
        """Returns a tuple wich contains  a list of headers of the xls spreadsheet table fields,
        a flag that indicates what kind of source of data we are messing with and
        width and alignment values to complete cells markup."""

        return (FieldsList, colData, colWidth_Align)

    def set_data_list(self, data):
        rowlist=[]
        for d in data:
            soggetto = ''
            if d.id_cliente is not None:
                soggetto = d.ragione_sociale_cliente or ''
                if soggetto == '':
                    soggetto = (d.cognome_cliente or '') + ' ' + (d.nome_cliente or '')
            elif d.id_fornitore is not None:
                soggetto = d.ragione_sociale_fornitore or ''
                if soggetto == '':
                    soggetto = (d.cognome_fornitore or '') + ' ' + (d.nome_fornitore or '')
            data = dateToString(d.data_movimento)
            numero = str(d.numero or 0)
            operazione = d.operazione or ''
            note_interne = d.note_interne or ''
            lista_articoli = d.righe

            if lista_articoli:
                for riga in lista_articoli:
                    codice_articolo = riga.codice_articolo or ''
                    descrizione = riga.descrizione or ''
                    id_testata_movimento = str(riga.id_testata_movimento) or ''
                    magazzino = riga.magazzino or ''
                    moltiplicatore = str(('%.2f') % float(riga.moltiplicatore)) or ''
                    percentuale_iva = str(('%.2f') % float(riga.percentuale_iva)) or ''
                    quantita = str(('%.2f') % float(riga.quantita)) or ''
                    if riga.sconti:
                        sconti = ''
                        for s in riga.sconti:
                            if s.tipo_sconto == 'percentuale':
                                sconti = sconti+str(('%.2f') % float(s.valore))+'%, '
                            elif s.tipo_sconto == 'valore':
                                sconti = sconti+str(('%.2f') % float(s.valore))+u'�'+', '
                        sconti = sconti[:-2]
                    else:
                        sconti = ''
                    valore_unitario_lordo = ('%.2f') % float(riga.valore_unitario_lordo or 0)
                    valore_unitario_netto = ('%.2f') % float(riga.valore_unitario_netto or 0)
                    datalist=[data,operazione,soggetto, codice_articolo, descrizione, magazzino, moltiplicatore, percentuale_iva, quantita, sconti, valore_unitario_lordo, valore_unitario_netto]#lista dei campi del dao da caricare. esempio: d.nome_campo
                    rowlist.append(datalist)
            else:
                codice_articolo = ''
                descrizione = ''
                id = ''
                id_articolo = ''
                id_magazzino = ''
                id_testata_movimento = ''
                magazzino = ''
                moltiplicatore = ''
                percentuale_iva = ''
                quantita = ''
                sconti = ''
                valore_unitario_lordo = 0
                valore_unitario_netto = 0
                datalist=[data,operazione,soggetto, codice_articolo, descrizione, magazzino, moltiplicatore, percentuale_iva, quantita, sconti, valore_unitario_lordo, valore_unitario_netto]#lista dei campi del dao da caricare. esempio: d.nome_campo
                rowlist.append(datalist)
        return rowlist

    def set_export_data(self):
        """
        Raccoglie informazioni specifiche per l'anagrafica restituite all'interno di un dizionario
        """
        data_details = {}
        data = datetime.datetime.now()
        curr_date = string.zfill(str(data.day), 2) + '-' + string.zfill(str(data.month),2) + '-' + string.zfill(str(data.year),4)
        data_details['curr_date'] = curr_date
        data_details['currentName'] = 'Lista_Movimenti_aggiornata_al_'+curr_date+'.xml'

        FieldsList = ['Data Movimento','Causale Movimento','Cliente/Fornitore','Codice Articolo','Descrizione','Magazzino','Moltiplicatore','% IVA','Quantit�','Sconti','Valore Unitario Lordo','Valore Unitario Netto']
        colData = [0,0,0,0,0,0,0,0,0,1,2,2]# 0=None, 1=Totali, 2=valore_somma
        colWidth_Align = [('100','c'),('150','l'),('150','l'),('100','c'),('250','l'),('150','c'),('100','c'),('70','c'),('70','c'),('70','c'),('140','r'),('140','r')] # (larghezza colonna, allineamento)__c=center,l=left,r=right
        data_details['XmlMarkup'] = (FieldsList, colData, colWidth_Align)

        return data_details

    def duplicate(self, dao):
        """ Duplica le informazioni relative ad un movimento scelto su uno nuovo """
        if dao is None:
            return

        from DuplicazioneMovimento import DuplicazioneMovimento
        anag = DuplicazioneMovimento(dao)
        showAnagraficaRichiamata(self.getTopLevel(), anag.getTopLevel(), None, self.filter.refresh)



class AnagraficaMovimentiFilter(AnagraficaFilter):
    """ Filtro per la ricerca nei movimenti """

    def __init__(self, anagrafica):
        AnagraficaFilter.__init__(self,
                                  anagrafica,
                                  'anagrafica_movimenti_filter_table',
                                  gladeFile='_anagrafica_movimenti_elements.glade')
        self._widgetFirstFocus = self.da_data_filter_entry
        self.orderBy = 'id'


    def draw(self):
        # Colonne della Treeview per il filtro
        treeview = self._anagrafica.anagrafica_filter_treeview
        renderer = gtk.CellRendererText()

        column = gtk.TreeViewColumn('Data movimento', renderer, text=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(True)
        column.connect("clicked", self._changeOrderBy, 'data_movimento')
        column.set_resizable(True)
        column.set_expand(False)
        column.set_min_width(100)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Numero movimento', renderer, text=2)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(True)
        column.connect("clicked", self._changeOrderBy, 'numero')
        column.set_resizable(True)
        column.set_expand(False)
        column.set_min_width(100)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Causale movimento', renderer, text=3)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(True)
        column.connect("clicked", self._changeOrderBy, 'operazione')
        column.set_resizable(True)
        column.set_expand(False)
        column.set_min_width(150)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Cliente / Fornitore', renderer, text=4)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        column.set_min_width(250)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Note interne', renderer, text=5)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(True)
        column.set_min_width(200)
        treeview.append_column(column)

        self._treeViewModel = gtk.ListStore(object, str, str, str, str, str)
        self._anagrafica.anagrafica_filter_treeview.set_model(self._treeViewModel)

        fillComboboxOperazioni(self.id_operazione_filter_combobox, 'movimento',
                               True)
        self.id_operazione_filter_combobox.set_active(0)
        fillComboboxMagazzini(self.id_magazzino_filter_combobox, True)
        if self._anagrafica._magazzinoFissato:
            findComboboxRowFromId(self.id_magazzino_filter_combobox,
                                  self._anagrafica._idMagazzino)
        else:
            self.id_magazzino_filter_combobox.set_active(0)
        self.cliente_filter_radiobutton.connect('toggled',
                                                self.on_filter_radiobutton_toggled)
        self.fornitore_filter_radiobutton.connect('toggled',
                                                  self.on_filter_radiobutton_toggled)
        self.cliente_filter_radiobutton.set_active(True)
        self.on_filter_radiobutton_toggled()
        self.clear()


    def clear(self):
        # Annullamento filtro
        self.da_data_filter_entry.set_text('01/01/' + Environment.workingYear)
        self.a_data_filter_entry.set_text('')
        self.da_numero_filter_entry.set_text('')
        self.a_numero_filter_entry.set_text('')
        self.id_operazione_filter_combobox.set_active(0)
        if not self._anagrafica._magazzinoFissato:
            fillComboboxMagazzini(self.id_magazzino_filter_combobox, True)
            self.id_magazzino_filter_combobox.set_active(0)
        self.id_cliente_filter_customcombobox.set_active(0)
        self.id_fornitore_filter_customcombobox.set_active(0)
        self.refresh()


    def refresh(self):
        # Aggiornamento TreeView
        daData = stringToDate(self.da_data_filter_entry.get_text())
        aData = stringToDate(self.a_data_filter_entry.get_text())
        daNumero = prepareFilterString(self.da_numero_filter_entry.get_text())
        aNumero = prepareFilterString(self.a_numero_filter_entry.get_text())
        idOperazione = prepareFilterString(findIdFromCombobox(self.id_operazione_filter_combobox))
        idMagazzino = findIdFromCombobox(self.id_magazzino_filter_combobox)
        idCliente = self.id_cliente_filter_customcombobox.getId()
        idFornitore = self.id_fornitore_filter_customcombobox.getId()

        def filterCountClosure():
            return TestataMovimento(isList=True).count(daNumero=daNumero,
                                                    aNumero=aNumero,
                                                    daParte=None,
                                                    aParte=None,
                                                    daData=daData,
                                                    aData=aData,
                                                    idOperazione=idOperazione,
                                                    idMagazzino=idMagazzino,
                                                    idCliente=idCliente,
                                                    idFornitore=idFornitore)

        self._filterCountClosure = filterCountClosure

        self.numRecords = self.countFilterResults()

        self._refreshPageCount()

        # Let's save the current search as a closure
        def filterClosure(offset, batchSize):
            return TestataMovimento(isList=True).select(orderBy=self.orderBy,
                                                         daNumero=daNumero,
                                                         aNumero=aNumero,
                                                         daParte=None,
                                                         aParte=None,
                                                         daData=daData,
                                                         aData=aData,
                                                         idOperazione=idOperazione,
                                                         idMagazzino=idMagazzino,
                                                         idCliente=idCliente,
                                                         idFornitore=idFornitore,
                                                         offset=offset,
                                                         batchSize=batchSize)

        self._filterClosure = filterClosure

        tdos = self.runFilter()
        self.xptDaoList = self.runFilter(offset=None, batchSize=None)

        self._treeViewModel.clear()

        for t in tdos:
            soggetto = ''
            if t.id_cliente is not None:
                soggetto = t.ragione_sociale_cliente or ''
                if soggetto == '':
                    soggetto = (t.cognome_cliente or '') + ' ' + (t.nome_cliente or '')
            elif t.id_fornitore is not None:
                soggetto = t.ragione_sociale_fornitore or ''
                if soggetto == '':
                    soggetto = (t.cognome_fornitore or '') + ' ' + (t.nome_fornitore or '')
            self._treeViewModel.append((t,
                                        dateToString(t.data_movimento),
                                        (t.numero or 0),
                                        (t.operazione or ''),
                                        (soggetto or ''),
                                        (t.note_interne or '')))


    def on_filter_radiobutton_toggled(self, widget=None):
        if self.cliente_filter_radiobutton.get_active():
            self.id_cliente_filter_customcombobox.set_sensitive(True)
            self.id_cliente_filter_customcombobox.grab_focus()
            self.id_fornitore_filter_customcombobox.set_active(0)
            self.id_fornitore_filter_customcombobox.set_sensitive(False)
        elif self.fornitore_filter_radiobutton.get_active():
            self.id_fornitore_filter_customcombobox.set_sensitive(True)
            self.id_fornitore_filter_customcombobox.grab_focus()
            self.id_cliente_filter_customcombobox.set_active(0)
            self.id_cliente_filter_customcombobox.set_sensitive(False)



class AnagraficaMovimentiHtml(AnagraficaHtml):
    def __init__(self, anagrafica):
        AnagraficaHtml.__init__(self, anagrafica, 'movimento',
                                'Informazioni sul movimento merce')



class AnagraficaMovimentiReport(AnagraficaReport):
    def __init__(self, anagrafica):
        AnagraficaReport.__init__(self, anagrafica=anagrafica,
                                  description='Elenco dei movimenti',
                                  defaultFileName='movimenti',
                                  htmlTemplate='movimenti',
                                  sxwTemplate='movimenti')



class AnagraficaMovimentiEdit(AnagraficaEdit):
    """ Modifica un record dei movimenti """

    def __init__(self, anagrafica):
        AnagraficaEdit.__init__(self,
                                anagrafica,
                                'anagrafica_movimenti_detail_vbox',
                                'Dati movimento',
                                gladeFile='_anagrafica_movimenti_elements.glade')
        self._widgetFirstFocus = self.data_movimento_entry

        # contenitore (dizionario) righe (riga 0 riservata per
        # variazioni in corso)
        self._righe = []
        self._righe.append({})
        # numero riga corrente
        self._numRiga = 0
        # modello righe: magazzino, codice articolo,
        # descrizione, percentuale iva, unita base, multiplo, listino,
        # quantita, prezzo lordo, sconti, prezzo netto, totale
        self.modelRiga = gtk.ListStore(str, str, str, str, str, str, str,
                                       str, str, str, str, str)
        # iteratore riga corrente
        self._iteratorRiga = None
        # cliente o fornitore ?
        self._tipoPersonaGiuridica = None
        self._operazione = None
        # prezzo vendita/acquisto, ivato/non ivato
        self._fonteValore = None
        # carico (+) o scarico (-)
        self._segno = None
        # caricamento movimento (interrompe l'azione degli eventi on_changed nelle combobox)
        self._loading = False


    def azzeraRiga(self, numero = 0):
        """
        Azzera i campi del dizionario privato delle righe, alla riga
        indicata (o alla 0-esima)
        """
        self._righe[numero] = {"idRiga": None,
                               "idMagazzino": None,
                               "magazzino": '',
                               "idArticolo": None,
                               "codiceArticolo": '',
                               "descrizione": '',
                               "percentualeIva": 0,
                               "idUnitaBase": None,
                               "unitaBase": '',
                               "idMultiplo": None,
                               "multiplo": '',
                               "idListino": None,
                               "listino": '',
                               "quantita": 0,
                               "moltiplicatore": 0,
                               "prezzoLordo": 0,
                               "applicazioneSconti": '',
                               "sconti": [],
                               "prezzoNetto": 0,
                               "totale": 0,
                               "codiceArticoloFornitore": '',
                               "prezzoNettoUltimo": 0}


    def nuovaRiga(self):
        """ prepara per l'inserimento di una nuova riga """
        self._numRiga = 0
        self.azzeraRiga(0)

        self.articolo_entry.set_text('')
        self.descrizione_entry.set_text('')
        self.codice_articolo_fornitore_entry.set_text('')
        self.percentuale_iva_entry.set_text('0')
        self.id_multiplo_customcombobox.combobox.clear()
        self.id_listino_customcombobox.combobox.clear()
        self.prezzo_lordo_entry.set_text('0')
        self.quantita_entry.set_text('0')
        self.prezzo_netto_label.set_text('0')
        self.sconti_widget.clearValues()
        self.totale_riga_label.set_text('0')

        if len(self._righe) > 1:
            self.data_movimento_entry.set_sensitive(False)
            self.id_operazione_combobox.set_sensitive(False)
            self.id_persona_giuridica_customcombobox.set_sensitive(False)
            self.articolo_entry.grab_focus()
        else:
            self.data_movimento_entry.set_sensitive(True)
            self.id_persona_giuridica_customcombobox.set_sensitive(self.id_operazione_combobox.get_active() != -1)
            self.id_operazione_combobox.set_sensitive(True)
            if self._anagrafica._magazzinoFissato:
                findComboboxRowFromId(self.id_magazzino_combobox, self._anagrafica._idMagazzino)
            else:
                self.id_magazzino_combobox.set_active(-1)
            self.id_magazzino_combobox.grab_focus()


    def clearRows(self):
        """ pulisce i campi per il trattamento e la conservazione delle righe """
        self._righe = []
        self._righe.append({})
        self._numRiga = 0
        self.modelRiga.clear()
        self._iteratorRiga = None
        self.nuovaRiga()


    def draw(self):
        treeview = self.righe_treeview
        rendererSx = gtk.CellRendererText()
        rendererDx = gtk.CellRendererText()
        rendererDx.set_property('xalign', 1)

        column = gtk.TreeViewColumn('Magazzino', rendererSx, text=0)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Codice articolo', rendererSx, text=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Descrizione', rendererSx, text=2)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(True)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('% IVA', rendererDx, text=3)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('U.M.', rendererSx, text=4)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Multiplo', rendererSx, text=5)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Listino', rendererSx, text=6)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Quantita''', rendererDx, text=7)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Prezzo lordo', rendererDx, text=8)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Sconti', rendererSx, text=9)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Prezzo netto', rendererDx, text=10)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        column = gtk.TreeViewColumn('Totale', rendererDx, text=11)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        fillComboboxOperazioni(self.id_operazione_combobox, 'movimento')
        fillComboboxMagazzini(self.id_magazzino_combobox)

        self.nuovaRiga()

        # preferenza ricerca articolo ?
        if hasattr(Environment.conf,'Documenti'):
            if hasattr(Environment.conf.Documenti,'ricerca_per'):
                if Environment.conf.Documenti.ricerca_per == 'codice':
                    self.ricerca_codice_button.set_active(True)
                elif Environment.conf.Documenti.ricerca_per == 'codice_a_barre':
                    self.ricerca_codice_a_barre_button.set_active(True)
                elif Environment.conf.Documenti.ricerca_per == 'descrizione':
                    self.ricerca_descrizione_button.set_active(True)
                elif Environment.conf.Documenti.ricerca_per == 'codice_articolo_fornitore':
                    self.ricerca_codice_articolo_fornitore_button.set_active(True)

        self.id_operazione_combobox.connect('changed',
                                            self.on_id_operazione_combobox_changed)
        self.id_persona_giuridica_customcombobox.setSingleValue()
        self.id_persona_giuridica_customcombobox.setOnChangedCall(self.persona_giuridica_changed)
        self.id_magazzino_combobox.connect('changed',
                                            self.on_id_magazzino_combobox_changed)
        self.id_multiplo_customcombobox.connect('clicked',
                                                self.on_id_multiplo_customcombobox_button_clicked)
        self.id_multiplo_customcombobox.combobox.connect('changed',
                                                         self.on_id_multiplo_customcombobox_changed)
        self.id_listino_customcombobox.connect('clicked',
                                               self.on_id_listino_customcombobox_button_clicked)
        self.id_listino_customcombobox.combobox.connect('changed',
                                                        self.on_id_listino_customcombobox_changed)
        self.id_listino_customcombobox.button.connect('toggled',
                                                      self.on_id_listino_customcombobox_button_toggled)
        self.sconti_widget.button.connect('toggled',
                                          self.on_sconti_widget_button_toggled)
        self.variazione_listini_button.connect('clicked',
                                               self.on_variazione_listini_button_clicked)
        self.storico_costi_button.connect('clicked',
                                          self.on_storico_costi_button_clicked)
        self.storico_listini_button.connect('clicked',
                                            self.on_storico_listini_button_clicked)
        self.edit_date_and_number_button.connect('clicked',
                                                 self.on_edit_date_and_number_button_clicked)
        self.ricerca_codice_button.connect('clicked',
                                           self.on_ricerca_codice_button_clicked)
        self.ricerca_codice_a_barre_button.connect('clicked',
                                                   self.on_ricerca_codice_a_barre_button_clicked)
        self.ricerca_descrizione_button.connect('clicked',
                                                self.on_ricerca_descrizione_button_clicked)
        self.ricerca_codice_articolo_fornitore_button.connect('clicked',
                                                              self.on_ricerca_codice_articolo_fornitore_button_clicked)

        #Castelletto iva
        rendererText = gtk.CellRendererText()

        column = gtk.TreeViewColumn('Aliquota I.V.A.', rendererText, text=0)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(True)
        self.riepiloghi_iva_treeview.append_column(column)

        rendererText = gtk.CellRendererText()
        rendererText.set_property('xalign', 1)

        column = gtk.TreeViewColumn('Imponibile', rendererText, text=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(True)
        self.riepiloghi_iva_treeview.append_column(column)

        column = gtk.TreeViewColumn('Imposta', rendererText, text=2)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(True)
        self.riepiloghi_iva_treeview.append_column(column)

        model = gtk.ListStore(str, str, str)
        self.riepiloghi_iva_treeview.set_model(model)


    def on_id_operazione_combobox_changed(self, combobox):
        self._operazione = findIdFromCombobox(self.id_operazione_combobox)
        operazione = leggiOperazione(self._operazione)
        if self._tipoPersonaGiuridica != operazione["tipoPersonaGiuridica"]:
            self.id_persona_giuridica_customcombobox.refresh(clear=True, filter=False)
        self._tipoPersonaGiuridica = operazione["tipoPersonaGiuridica"]
        self._fonteValore = operazione["fonteValore"]
        self._segno = operazione["segno"]

        if (self._tipoPersonaGiuridica == "fornitore"):
            self.persona_giuridica_label.set_text('Fornitore')
            self.id_persona_giuridica_customcombobox.setType(self._tipoPersonaGiuridica)
            self.id_persona_giuridica_customcombobox.set_sensitive(True)
            self.label_listino.set_property('visible', False)
            self.id_listino_customcombobox.set_property('visible', False)
            self.prz_lordo_label.set_text('Costo')
            self.prz_netto_label.set_text('Costo netto')
            self.codice_articolo_fornitore_label.set_property('visible', True)
            self.codice_articolo_fornitore_entry.set_property('visible', True)
        elif (self._tipoPersonaGiuridica == "cliente"):
            self.persona_giuridica_label.set_text('Cliente')
            self.id_persona_giuridica_customcombobox.setType(self._tipoPersonaGiuridica)
            self.id_persona_giuridica_customcombobox.set_sensitive(True)
            self.label_listino.set_property('visible', True)
            self.id_listino_customcombobox.set_property('visible', True)
            self.prz_lordo_label.set_text('Prezzo')
            self.prz_netto_label.set_text('Prezzo netto')
            self.codice_articolo_fornitore_label.set_property('visible', False)
            self.codice_articolo_fornitore_entry.set_property('visible', False)
        else:
            self.persona_giuridica_label.set_text('Cliente/Fornitore ?')
            self.id_persona_giuridica_customcombobox.set_sensitive(False)
            self.label_listino.set_property('visible', True)
            self.id_listino_customcombobox.set_property('visible', True)
            self.prz_lordo_label.set_text('Prezzo')
            self.prz_netto_label.set_text('Prezzo netto')
            self.codice_articolo_fornitore_label.set_property('visible', False)
            self.codice_articolo_fornitore_entry.set_property('visible', False)
        self.persona_giuridica_changed()
        self.data_movimento_entry.grab_focus()


    def persona_giuridica_changed(self):
        if self._tipoPersonaGiuridica == "cliente":
            self.refresh_combobox_listini()


    def on_id_magazzino_combobox_changed(self, combobox):
        if self._loading:
            return

        self._righe[0]["idMagazzino"] = findIdFromCombobox(self.id_magazzino_combobox)
        magazzino = leggiMagazzino(self._righe[0]["idMagazzino"])
        self._righe[0]["magazzino"] = magazzino["denominazione"]
        self.refresh_combobox_listini()


    def refresh_combobox_listini(self):
        if self._righe[0]["idArticolo"] is None:
            self.id_listino_customcombobox.combobox.clear
        else:
            fillComboboxListiniFiltrati(self.id_listino_customcombobox.combobox,
                                        self._righe[0]["idArticolo"],
                                        self._righe[0]["idMagazzino"],
                                        self.id_persona_giuridica_customcombobox.getId())


    def on_id_multiplo_customcombobox_button_clicked(self, widget, toggleButton):
        on_id_multiplo_customcombobox_clicked(widget, toggleButton, self._righe[0]["idArticolo"])


    def on_id_multiplo_customcombobox_changed(self, combobox):
        if self._loading:
            return

        self._righe[0]["idMultiplo"] = findIdFromCombobox(self.id_multiplo_customcombobox.combobox)
        multiplo = leggiMultiplo(self._righe[0]["idMultiplo"])
        self._righe[0]["multiplo"] = multiplo["denominazioneBreve"] + ' ( ' + str('%.2f' % multiplo["moltiplicatore"]) + ' X )'
        self._righe[0]["moltiplicatore"] = multiplo["moltiplicatore"]
        self.calcolaTotaleRiga()


    def on_id_listino_customcombobox_button_clicked(self, widget, toggleButton):
        on_id_listino_customcombobox_clicked(widget, toggleButton, self._righe[0]["idArticolo"], None)


    def on_id_listino_customcombobox_button_toggled(self, button):
        if button.get_property('active') is True:
            return

        self.refresh_combobox_listini()


    def on_id_listino_customcombobox_changed(self, combobox):
        if self._loading:
            return

        idListino = findIdFromCombobox(self.id_listino_customcombobox.combobox)
        idArticolo = self._righe[0]["idArticolo"]
        self.getPrezzoVenditaLordo(idListino, idArticolo)
        self.prezzo_lordo_entry.set_text(Environment.conf.number_format % float(self._righe[0]["prezzoLordo"]))
        self.on_show_totali_riga()


    def getPrezzoVenditaLordo(self, idListino, idArticolo):
        """ cerca il prezzo di vendita """
        prezzoLordo = 0
        if idListino is not None and idArticolo is not None:
            listino = leggiListino(idListino, idArticolo)
            self._righe[0]["listino"] = listino["denominazione"]
            if (self._fonteValore == "vendita_iva"):
                prezzoLordo = listino["prezzoDettaglio"]
            elif (self._fonteValore == "vendita_senza_iva"):
                prezzoLordo = listino["prezzoIngrosso"]
        self._righe[0]["prezzoLordo"] = prezzoLordo
        self._righe[0]["idListino"] = idListino


    def getPrezzoNetto(self):
        """ calcola il prezzo netto dal prezzo lordo e dagli sconti """
        prezzoLordo = float(self._righe[0]["prezzoLordo"])
        prezzoNetto = float(self._righe[0]["prezzoLordo"])
        applicazione = self._righe[0]["applicazioneSconti"]
        sconti = self._righe[0]["sconti"]
        for s in sconti:
            if s["tipo"] == 'percentuale':
                if applicazione == 'scalare':
                    prezzoNetto = prezzoNetto * (1 - float(s["valore"]) / 100)
                elif applicazione == 'non scalare':
                    prezzoNetto = prezzoNetto - prezzoLordo * float(s["valore"]) / 100
            elif s["tipo"] == 'valore':
                prezzoNetto = prezzoNetto - float(s["valore"])
        self._righe[0]["prezzoNetto"] = prezzoNetto


    def getTotaleRiga(self):
        segnoIva = 1
        percentualeIva = float(self._righe[0]["percentualeIva"])
        prezzoNetto = float(self._righe[0]["prezzoNetto"])
        quantita = float(self._righe[0]["quantita"])
        moltiplicatore = float(self._righe[0]["moltiplicatore"])
        #if (self._fonteValore == "vendita_iva" or self._fonteValore == "acquisto_iva"):
        #    segnoIva = -1
        #    prezzoNetto = calcolaPrezzoIva(prezzoNetto, segnoIva * percentualeIva)

        self._righe[0]["totale"] = prezzoNetto * quantita * moltiplicatore


    def on_sconti_widget_button_toggled(self, button):
        if button.get_property('active') is True:
            return

        self._righe[0]["sconti"] = self.sconti_widget.getSconti()
        self._righe[0]["applicazioneSconti"] = self.sconti_widget.getApplicazione()
        self.on_show_totali_riga()


    def on_notebook_switch_page(self, notebook, page, page_num):
        if page_num == 2:
            self.calcolaTotale()


    def _refresh(self):
        self._loading = True

        self._tipoPersonaGiuridica = None
        self._operazione = None
        self._fonteValore = None
        self._segno = None

        self.data_movimento_entry.set_sensitive(self.dao.id is None)
        self.edit_date_and_number_button.set_sensitive(self.dao.id is not None)
        self.numero_movimento_entry.set_sensitive(False)

        self.id_operazione_combobox.set_sensitive(self.dao.id is None)
        self.id_persona_giuridica_customcombobox.set_sensitive(self.dao.id is None)

        self.id_operazione_combobox.set_active(-1)
        self.id_persona_giuridica_customcombobox.set_active(-1)

        self._operazione = self.dao.operazione
        findComboboxRowFromId(self.id_operazione_combobox, self.dao.operazione)
        self.on_id_operazione_combobox_changed(self.id_operazione_combobox)
        self.id_persona_giuridica_customcombobox.refresh(clear=True, filter=False)
        if self._tipoPersonaGiuridica == "fornitore":
            self.id_persona_giuridica_customcombobox.setId(self.dao.id_fornitore)
        elif self._tipoPersonaGiuridica == "cliente":
            self.id_persona_giuridica_customcombobox.setId(self.dao.id_cliente)

        self.data_movimento_entry.set_text(dateToString(self.dao.data_movimento))
        self.numero_movimento_entry.set_text(str(self.dao.numero or '0'))
        self.showDatiDocumento()

        textBuffer = self.note_interne_textview.get_buffer()
        if self.dao.note_interne is not None:
            textBuffer.set_text(self.dao.note_interne)
        else:
            textBuffer.set_text('')
        self.note_interne_textview.set_buffer(textBuffer)

        self.clearRows()
        for i in range(0, len(self.dao.righe)):
            self.azzeraRiga(0)
            j = i + 1
            magazzino = leggiMagazzino(self.dao.righe[i].id_magazzino)
            articolo = leggiArticolo(self.dao.righe[i].id_articolo)
            listino = leggiListino(self.dao.righe[i].id_listino)
            multiplo = leggiMultiplo(self.dao.righe[i].id_multiplo)
            (sconti, applicazione) = getScontiFromDao(self.dao.righe[i].sconti, self.dao.righe[i].applicazione_sconti)

            self._righe[0]["idRiga"] = self.dao.righe[i].id
            self._righe[0]["idMagazzino"] = self.dao.righe[i].id_magazzino
            self._righe[0]["magazzino"] = magazzino["denominazione"]
            self._righe[0]["idArticolo"] = self.dao.righe[i].id_articolo
            self._righe[0]["codiceArticolo"] = articolo["codice"]
            self._righe[0]["descrizione"] = self.dao.righe[i].descrizione
            self._righe[0]["percentualeIva"] = self.dao.righe[i].percentuale_iva
            self._righe[0]["idUnitaBase"] = articolo["idUnitaBase"]
            self._righe[0]["unitaBase"] = articolo["unitaBase"]
            self._righe[0]["idMultiplo"] = self.dao.righe[i].id_multiplo
            if multiplo["moltiplicatore"] != 0:
                self._righe[0]["multiplo"] = multiplo["denominazioneBreve"] + ' ( ' + str('%.2f' % multiplo["moltiplicatore"]) + ' X )'
            else:
                self._righe[0]["multiplo"] = ''
            self._righe[0]["idListino"] = self.dao.righe[i].id_listino
            self._righe[0]["listino"] = listino["denominazione"]
            self._righe[0]["quantita"] = self.dao.righe[i].quantita
            self._righe[0]["moltiplicatore"] = self.dao.righe[i].moltiplicatore
            self._righe[0]["prezzoLordo"] = self.dao.righe[i].valore_unitario_lordo
            self._righe[0]["sconti"] = sconti
            self._righe[0]["applicazioneSconti"] = applicazione
            self._righe[0]["prezzoNetto"] = self.dao.righe[i].valore_unitario_netto
            self._righe[0]["prezzoNettoUltimo"] = self.dao.righe[i].valore_unitario_netto
            self._righe[0]["totale"] = 0
            self.getTotaleRiga()

            if self._tipoPersonaGiuridica == "fornitore":
                fornitura = leggiFornitura(self.dao.righe[i].id_articolo, self.dao.id_fornitore, self.dao.data_movimento, True)
                self._righe[0]["codiceArticoloFornitore"] = fornitura["codiceArticoloFornitore"]

            self._righe.append(self._righe[0])

            self.modelRiga.append((self._righe[j]["magazzino"],
                                   self._righe[j]["codiceArticolo"],
                                   self._righe[j]["descrizione"],
                                   '%5.2f' % float(self._righe[j]["percentualeIva"]),
                                   self._righe[j]["unitaBase"],
                                   self._righe[j]["multiplo"],
                                   self._righe[j]["listino"],
                                   '%9.3f' % float(self._righe[j]["quantita"]),
                                   ('%14.' + Environment.conf.decimals + 'f') % float(self._righe[j]["prezzoLordo"]),
                                   self._righe[j]["applicazioneSconti"] + ' ' + getStringaSconti(self._righe[j]["sconti"]),
                                   ('%14.' + Environment.conf.decimals + 'f') % float(self._righe[j]["prezzoNetto"]),
                                   ('%14.2f') % round(float(self._righe[j]["totale"]), 2)))

        self.righe_treeview.set_model(self.modelRiga)
        self._loading = False
        self.calcolaTotale()
        self.label_numero_righe.set_text(str(len(self.dao.righe)))
        self.notebook.set_current_page(0)
        self.nuovaRiga()
        if self.dao.id is None or self.numero_movimento_entry.get_text() == '0':
            self.id_operazione_combobox.grab_focus()
        else:
            self.id_magazzino_combobox.grab_focus()


    def setDao(self, dao):
        if dao is None:
            # Crea un nuovo Dao vuoto
            self.dao = TestataMovimento().getRecord()
            # Suggerisce la data odierna
            self.dao.data_movimento = datetime.datetime.today()
        else:
            # Ricrea il Dao con una connessione al DBMS SQL
            self.dao = TestataMovimento(id=dao.id).getRecord()
        self._refresh()


    def saveDao(self):
        if not(len(self._righe) > 1):
            return

        if (self.data_movimento_entry.get_text() == ''):
            obligatoryField(self.dialogTopLevel,
                            self.data_movimento_entry,
                            'Inserire la data del documento !')

        if (findIdFromCombobox(self.id_operazione_combobox) is None):
            obligatoryField(self.dialogTopLevel,
                            self.id_operazione_combobox,
                            'Inserire il tipo di documento !')

        self.dao.data_movimento = stringToDate(self.data_movimento_entry.get_text())
        if self.dao.id is not None and self.numero_movimento_entry.get_text() != '0':
            self.dao.numero = self.numero_movimento_entry.get_text()

        self.dao.operazione = self._operazione
        if self._tipoPersonaGiuridica == "fornitore":
            self.dao.id_fornitore = self.id_persona_giuridica_customcombobox.getId()
            self.dao.id_cliente = None
        elif self._tipoPersonaGiuridica == "cliente":
            self.dao.id_cliente = self.id_persona_giuridica_customcombobox.getId()
            self.dao.id_fornitore = None

        textBuffer = self.note_interne_textview.get_buffer()
        self.dao.note_interne = textBuffer.get_text(textBuffer.get_start_iter(), textBuffer.get_end_iter())
        righeMovimento = {}
        scontiRigheMovimento= {}
        righe = []
        for i in range(1, len(self._righe)):
            daoRiga = RigaMovimento().getRecord()
            daoRiga.id_testata_movimento = self.dao.id
            daoRiga.id_articolo = self._righe[i]["idArticolo"]
            daoRiga.id_magazzino = self._righe[i]["idMagazzino"]
            daoRiga.descrizione = self._righe[i]["descrizione"]
            daoRiga.codiceArticoloFornitore = self._righe[i]["codiceArticoloFornitore"]
            daoRiga.id_listino = self._righe[i]["idListino"]
            daoRiga.percentuale_iva = self._righe[i]["percentualeIva"]
            daoRiga.applicazione_sconti = self._righe[i]["applicazioneSconti"]
            daoRiga.quantita = self._righe[i]["quantita"]
            daoRiga.id_multiplo = self._righe[i]["idMultiplo"]
            daoRiga.moltiplicatore = self._righe[i]["moltiplicatore"]
            daoRiga.valore_unitario_lordo = self._righe[i]["prezzoLordo"]
            daoRiga.valore_unitario_netto = self._righe[i]["prezzoNetto"]

            sconti = []
            if self._righe[i]["sconti"] is not None:
                for j in range(0, len(self._righe[i]["sconti"])):
                    daoSconto = ScontoRigaMovimento().getRecord()
                    daoSconto.valore = float(self._righe[i]["sconti"][j]["valore"])
                    daoSconto.tipo_sconto = self._righe[i]["sconti"][j]["tipo"]
                    sconti.append(daoSconto)
            scontiRigheMovimento[daoRiga] = sconti

            daoRiga.sconti = sconti
            righeMovimento[i] = daoRiga
            righe.append(daoRiga)

        #self.dao.righe = righe

        self.dao.persist(scontiRigaMovimento= scontiRigheMovimento, righeMovimento=righeMovimento )
        self.label_numero_righe.hide()
        text = str(len(self.dao.righe))
        self.label_numero_righe.set_text(text)
        self.label_numero_righe.show()


    def on_righe_treeview_row_activated(self, treeview, path, column):
        """ riporta la rica selezionata in primo piano per la modifica """
        sel = treeview.get_selection()
        (model, self._iteratorRiga) = sel.get_selected()
        (selRow, ) = path
        self._numRiga = selRow + 1

        self.azzeraRiga(0)
        self._loading = True

        self._righe[0]["idRiga"] = self._righe[self._numRiga]["idRiga"]
        self._righe[0]["idMagazzino"] = self._righe[self._numRiga]["idMagazzino"]
        self._righe[0]["magazzino"] = self._righe[self._numRiga]["magazzino"]
        self._righe[0]["idArticolo"] = self._righe[self._numRiga]["idArticolo"]
        self._righe[0]["codiceArticolo"] = self._righe[self._numRiga]["codiceArticolo"]
        self._righe[0]["descrizione"] = self._righe[self._numRiga]["descrizione"]
        self._righe[0]["codiceArticoloFornitore"] = self._righe[self._numRiga]["codiceArticoloFornitore"]
        self._righe[0]["idUnitaBase"] = self._righe[self._numRiga]["idUnitaBase"]
        self._righe[0]["unitaBase"] = self._righe[self._numRiga]["unitaBase"]
        self._righe[0]["idMultiplo"] = self._righe[self._numRiga]["idMultiplo"]
        self._righe[0]["multiplo"] = self._righe[self._numRiga]["multiplo"]
        self._righe[0]["idListino"] = self._righe[self._numRiga]["idListino"]
        self._righe[0]["listino"] = self._righe[self._numRiga]["listino"]
        self._righe[0]["quantita"] = self._righe[self._numRiga]["quantita"]
        self._righe[0]["moltiplicatore"] = self._righe[self._numRiga]["moltiplicatore"]
        self._righe[0]["prezzoLordo"] = self._righe[self._numRiga]["prezzoLordo"]
        self._righe[0]["percentualeIva"] = self._righe[self._numRiga]["percentualeIva"]
        self._righe[0]["applicazioneSconti"] = self._righe[self._numRiga]["applicazioneSconti"]
        self._righe[0]["sconti"] = self._righe[self._numRiga]["sconti"]
        self._righe[0]["prezzoNetto"] = float(self._righe[self._numRiga]["prezzoNetto"])
        self._righe[0]["totale"] = self._righe[self._numRiga]["totale"]
        self._righe[0]["prezzoNettoUltimo"] = self._righe[self._numRiga]["prezzoNettoUltimo"]

        findComboboxRowFromId(self.id_magazzino_combobox, self._righe[0]["idMagazzino"])
        fillComboboxMultipli(self.id_multiplo_customcombobox.combobox, self._righe[0]["idArticolo"], True)
        findComboboxRowFromId(self.id_multiplo_customcombobox.combobox, self._righe[0]["idMultiplo"])
        self.refresh_combobox_listini()
        findComboboxRowFromId(self.id_listino_customcombobox.combobox, self._righe[0]["idListino"])

        self.articolo_entry.set_text(self._righe[0]["codiceArticolo"])
        self.descrizione_entry.set_text(self._righe[0]["descrizione"])
        self.codice_articolo_fornitore_entry.set_text(self._righe[0]["codiceArticoloFornitore"])
        self.percentuale_iva_entry.set_text('%-5.2f' % self._righe[0]["percentualeIva"])
        self.sconti_widget.setValues(self._righe[0]["sconti"], self._righe[0]["applicazioneSconti"], False)
        self.quantita_entry.set_text('%-9.3f' % float(self._righe[0]["quantita"]))
        self.prezzo_lordo_entry.set_text(Environment.conf.number_format % float(self._righe[0]["prezzoLordo"]))
        self.prezzo_netto_label.set_text(('%14.' + Environment.conf.decimals + 'f') % float(self._righe[0]["prezzoNetto"]))
        self.totale_riga_label.set_text(('%14.2f') % round(float(self._righe[0]["totale"]), 2))

        self._loading = False
        self.articolo_entry.grab_focus()


    def on_new_row_button_clicked(self, widget):
        self.nuovaRiga()


    def on_confirm_row_button_clicked(self, widget):
        """ memorizza la riga inserita o modificata """
        self._righe[0]["idMagazzino"] = findIdFromCombobox(self.id_magazzino_combobox)
        magazzino = leggiMagazzino(self._righe[0]["idMagazzino"])
        self._righe[0]["magazzino"] = magazzino["denominazione"]

        if (self.data_movimento_entry.get_text() == ''):
            self.showMessage('Inserire da data del movimento !')
            return

        if (findIdFromCombobox(self.id_operazione_combobox) is None):
            self.showMessage('Inserire il tipo di movimento !')
            return

        if ((self._righe[0]["idMagazzino"] is not None) and
            (self._righe[0]["idArticolo"] is None)):
            self.showMessage('Inserire l''articolo !')
            return

        if ((self._righe[0]["idArticolo"] is not None) and
            (self._righe[0]["idMagazzino"] is None)):
            self.showMessage('Inserire il magazzino !')
            return

        costoVariato = (self._tipoPersonaGiuridica == "fornitore" and self._righe[0]["idArticolo"] is not None and
                        (float(self._righe[0]["prezzoNetto"]) != float(self._righe[0]["prezzoNettoUltimo"])))

        if self._numRiga == 0:
            self._numRiga = len(self._righe)
            self._righe.append(self._righe[0])
            inserisci = True
        else:
            inserisci = False

        # memorizzazione delle parti descrittive (liberamente modificabili)
        self._righe[0]["descrizione"] = self.descrizione_entry.get_text()
        self._righe[0]["codiceArticoloFornitore"] = self.codice_articolo_fornitore_entry.get_text()

        self._righe[self._numRiga]["idRiga"] = self._righe[0]["idRiga"]
        self._righe[self._numRiga]["idMagazzino"] = self._righe[0]["idMagazzino"]
        self._righe[self._numRiga]["magazzino"] = self._righe[0]["magazzino"]
        self._righe[self._numRiga]["idArticolo"] = self._righe[0]["idArticolo"]
        self._righe[self._numRiga]["codiceArticolo"] = self._righe[0]["codiceArticolo"]
        self._righe[self._numRiga]["descrizione"] = self._righe[0]["descrizione"]
        self._righe[self._numRiga]["codiceArticoloFornitore"] = self._righe[0]["codiceArticoloFornitore"]
        self._righe[self._numRiga]["percentualeIva"] = self._righe[0]["percentualeIva"]
        self._righe[self._numRiga]["idUnitaBase"] = self._righe[0]["idUnitaBase"]
        self._righe[self._numRiga]["unitaBase"] = self._righe[0]["unitaBase"]
        self._righe[self._numRiga]["idMultiplo"] = self._righe[0]["idMultiplo"]
        self._righe[self._numRiga]["multiplo"] = self._righe[0]["multiplo"]
        self._righe[self._numRiga]["idListino"] = self._righe[0]["idListino"]
        self._righe[self._numRiga]["listino"] = self._righe[0]["listino"]
        self._righe[self._numRiga]["quantita"] = float(self._righe[0]["quantita"])
        self._righe[self._numRiga]["moltiplicatore"] = float(self._righe[0]["moltiplicatore"])
        self._righe[self._numRiga]["prezzoLordo"] = float(self._righe[0]["prezzoLordo"])
        self._righe[self._numRiga]["applicazioneSconti"] = self._righe[0]["applicazioneSconti"]
        self._righe[self._numRiga]["sconti"] = self._righe[0]["sconti"]
        self._righe[self._numRiga]["prezzoNetto"] = float(self._righe[0]["prezzoNetto"])
        self._righe[self._numRiga]["totale"] = float(self._righe[0]["totale"])
        if not inserisci:
            if self._iteratorRiga is None:
                return
            self.modelRiga.set_value(self._iteratorRiga, 0, self._righe[self._numRiga]["magazzino"])
            self.modelRiga.set_value(self._iteratorRiga, 1, self._righe[self._numRiga]["codiceArticolo"])
            self.modelRiga.set_value(self._iteratorRiga, 2, self._righe[self._numRiga]["descrizione"])
            self.modelRiga.set_value(self._iteratorRiga, 3, '%5.2f' % float(self._righe[self._numRiga]["percentualeIva"]))
            self.modelRiga.set_value(self._iteratorRiga, 4, self._righe[self._numRiga]["unitaBase"])
            self.modelRiga.set_value(self._iteratorRiga, 5, self._righe[self._numRiga]["multiplo"])
            self.modelRiga.set_value(self._iteratorRiga, 6, self._righe[self._numRiga]["listino"])
            self.modelRiga.set_value(self._iteratorRiga, 7, '%9.3f' % float(self._righe[self._numRiga]["quantita"]))
            self.modelRiga.set_value(self._iteratorRiga, 8, ('%14.' + Environment.conf.decimals + 'f') % float(self._righe[self._numRiga]["prezzoLordo"]))
            self.modelRiga.set_value(self._iteratorRiga, 9, self._righe[self._numRiga]["applicazioneSconti"] + ' ' + getStringaSconti(self._righe[self._numRiga]["sconti"]))
            self.modelRiga.set_value(self._iteratorRiga, 10, ('%14.' + Environment.conf.decimals + 'f') % float(self._righe[self._numRiga]["prezzoNetto"]))
            self.modelRiga.set_value(self._iteratorRiga, 11, ('%14.2f') % round(float(self._righe[self._numRiga]["totale"]), 2))
        else:
            self.modelRiga.append((self._righe[self._numRiga]["magazzino"],
                                   self._righe[self._numRiga]["codiceArticolo"],
                                   self._righe[self._numRiga]["descrizione"],
                                   '%5.2f' % float(self._righe[self._numRiga]["percentualeIva"]),
                                   self._righe[self._numRiga]["unitaBase"],
                                   self._righe[self._numRiga]["multiplo"],
                                   self._righe[self._numRiga]["listino"],
                                   '%9.3f' % float(self._righe[self._numRiga]["quantita"]),
                                   ('%14.' + Environment.conf.decimals + 'f') % float(self._righe[self._numRiga]["prezzoLordo"]),
                                   self._righe[self._numRiga]["applicazioneSconti"] + ' ' + getStringaSconti(self._righe[self._numRiga]["sconti"]),
                                   ('%14.' + Environment.conf.decimals + 'f') % float(self._righe[self._numRiga]["prezzoNetto"]),
                                   ('%14.2f') % round(float(self._righe[self._numRiga]["totale"]), 2)))
        self.calcolaTotale()

        if costoVariato:
            msg = "Il prezzo di acquisto e' stato variato:\n si desidera aggiornare i listini di vendita ?"
            dialog = gtk.MessageDialog(self.dialogTopLevel, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                       gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                self.on_variazione_listini_button_clicked(self.variazione_listini_button)
        self._righe[self._numRiga]["prezzoNettoUltimo"] = float(self._righe[0]["prezzoNetto"])
        self.nuovaRiga()


    def on_undo_row_button_clicked(self, widget):
        """ annulla l'inserimento o la modifica della riga in primo piano """
        self.nuovaRiga()


    def on_delete_row_button_clicked(self, widget):
        """ elimina la riga in primo piano """
        if not(self._numRiga == 0):
            del(self._righe[self._numRiga])
            self.modelRiga.remove(self._iteratorRiga)
        self.calcolaTotale()
        self.nuovaRiga()


    # ---


    def on_ricerca_codice_button_clicked(self, widget):
        if self.ricerca_codice_button.get_active():
            self.ricercaArticolo()


    def on_ricerca_codice_a_barre_button_clicked(self, widget):
        if self.ricerca_codice_a_barre_button.get_active():
            self.ricercaArticolo()


    def on_ricerca_descrizione_button_clicked(self, widget):
        if self.ricerca_descrizione_button.get_active():
            self.ricercaArticolo()


    def on_ricerca_codice_articolo_fornitore_button_clicked(self, widget):
        if self.ricerca_codice_articolo_fornitore_button.get_active():
            self.ricercaArticolo()


    def on_articolo_entry_key_press_event(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        if keyname == 'Return' or keyname == 'KP_Enter':
            self.ricercaArticolo()

    def on_search_row_button_clicked(self, widget):
        self.ricercaArticolo()

    def ricercaArticolo(self):

        def on_ricerca_articolo_hide(anagWindow, anag):
            if anag.dao is None:
                anagWindow.destroy()
                return

            anagWindow.destroy()
            self.mostraArticolo(anag.dao.id)


        if (self.data_movimento_entry.get_text() == ''):
            self.showMessage('Inserire da data del movimento !')
            return

        if (findIdFromCombobox(self.id_operazione_combobox) is None):
            self.showMessage('Inserire il tipo di movimento !')
            return

        if (findIdFromCombobox(self.id_magazzino_combobox) is None):
            self.showMessage('Inserire il magazzino !')
            return

        codice = None
        codiceABarre = None
        denominazione = None
        codiceArticoloFornitore = None

        if self.ricerca_codice_button.get_active():
            codice = self.articolo_entry.get_text()
            orderBy = "codice"
        elif self.ricerca_codice_a_barre_button.get_active():
            codiceABarre = self.articolo_entry.get_text()
            orderBy = "codice_a_barre"
        elif self.ricerca_descrizione_button.get_active():
            denominazione = self.articolo_entry.get_text()
            orderBy = "denominazione"
        elif self.ricerca_codice_articolo_fornitore_button.get_active():
            codiceArticoloFornitore = self.articolo_entry.get_text()
            orderBy = "codice_articolo_fornitore"

        arts = Articolo(isList=True).select(orderBy=orderBy,
                                denominazione=prepareFilterString(denominazione),
                                codice=prepareFilterString(codice),
                                codiceABarre=prepareFilterString(codiceABarre),
                                codiceArticoloFornitore=prepareFilterString(codiceArticoloFornitore),
                                idFamiglia=None,
                                idCategoria=None,
                                idStato=None,
                                offset=None,
                                batchSize=None)


        if (len(arts) == 1):
            self.mostraArticolo(arts[0].id)
        else:
            from RicercaComplessaArticoli import RicercaComplessaArticoli
            anag = RicercaComplessaArticoli(denominazione=denominazione,
                                            codice=codice,
                                            codiceABarre=codiceABarre,
                                            codiceArticoloFornitore=codiceArticoloFornitore)
            anag.setTreeViewSelectionType(gtk.SELECTION_SINGLE)
            anagWindow = anag.getTopLevel()
            anagWindow.connect("hide",
                               on_ricerca_articolo_hide,
                               anag)
            anagWindow.set_transient_for(self.dialogTopLevel)
            anagWindow.show_all()


    def mostraArticolo(self, id):
        self.articolo_entry.set_text('')
        self.descrizione_entry.set_text('')
        self.codice_articolo_fornitore_entry.set_text('')
        self.percentuale_iva_entry.set_text('')
        self.id_multiplo_customcombobox.combobox.clear()
        self.id_listino_customcombobox.combobox.clear()
        self.prezzo_lordo_entry.set_text('0')
        self.quantita_entry.set_text('0')
        self.prezzo_netto_label.set_text('0')
        self.sconti_widget.clearValues()

        self._righe[0]["idArticolo"] = None
        self._righe[0]["codiceArticolo"] = ''
        self._righe[0]["descrizione"] = ''
        self._righe[0]["codiceArticoloFornitore"] = ''
        self._righe[0]["percentualeIva"] = 0
        self._righe[0]["idUnitaBase"] = None
        self._righe[0]["idMultiplo"] = None
        self._righe[0]["moltiplicatore"] = 1
        self._righe[0]["idListino"] = None
        self._righe[0]["prezzoLordo"] = 0
        self._righe[0]["prezzoNetto"] = 0
        self._righe[0]["sconti"] = []
        self._righe[0]["applicazioneSconti"] = 'scalare'
        data = stringToDate(self.data_movimento_entry.get_text())

        fillComboboxMultipli(self.id_multiplo_customcombobox.combobox, id, True)

        if id is not None:
            articolo = leggiArticolo(id)
            self._righe[0]["idArticolo"] = id
            self._righe[0]["codiceArticolo"] = articolo["codice"]
            self._righe[0]["descrizione"] = articolo["denominazione"]
            self._righe[0]["percentualeIva"] = articolo["percentualeAliquotaIva"]
            self._righe[0]["idUnitaBase"] = articolo["idUnitaBase"]
            self._righe[0]["unitaBase"] = articolo["unitaBase"]
            self._righe[0]["idMultiplo"] = None
            self._righe[0]["moltiplicatore"] = 1
            self._righe[0]["prezzoLordo"] = 0
            self._righe[0]["prezzoNetto"] = 0
            self._righe[0]["sconti"] = []
            self._righe[0]["applicazioneSconti"] = 'scalare'
            self._righe[0]["codiceArticoloFornitore"] = ''

            if ((self._fonteValore == "acquisto_iva") or
                (self._fonteValore == "acquisto_senza_iva")):
                fornitura = leggiFornitura(id, self.id_persona_giuridica_customcombobox.getId(), data)
                costoLordo = fornitura["prezzoLordo"]
                costoNetto = fornitura["prezzoNetto"]
                if self._fonteValore == "acquisto_iva":
                    costoLordo = calcolaPrezzoIva(costoLordo, self._righe[0]["percentualeIva"])
                    costoNetto = calcolaPrezzoIva(costoNetto, self._righe[0]["percentualeIva"])
                self._righe[0]["prezzoLordo"] = costoLordo
                self._righe[0]["prezzoNettoUltimo"] = costoNetto
                self._righe[0]["sconti"] = fornitura["sconti"]
                self._righe[0]["applicazioneSconti"] = fornitura["applicazioneSconti"]
                self._righe[0]["codiceArticoloFornitore"] = fornitura["codiceArticoloFornitore"]
            elif ((self._fonteValore == "vendita_iva") or
                  (self._fonteValore == "vendita_senza_iva")):
                self.refresh_combobox_listini()

        self.articolo_entry.set_text(self._righe[0]["codiceArticolo"])
        self.descrizione_entry.set_text(self._righe[0]["descrizione"])
        self.percentuale_iva_entry.set_text('%-5.2f' % self._righe[0]["percentualeIva"])
        self.codice_articolo_fornitore_entry.set_text(self._righe[0]["codiceArticoloFornitore"])
        self.prezzo_lordo_entry.set_text(Environment.conf.number_format % float(self._righe[0]["prezzoLordo"]))
        self.on_show_totali_riga()
        if self._tipoPersonaGiuridica == "cliente":
            self.id_listino_customcombobox.combobox.grab_focus()
        elif self._tipoPersonaGiuridica == "fornitore":
            self.codice_articolo_fornitore_entry.grab_focus()
        else:
            self.descrizione_entry.grab_focus()


    def on_show_totali_riga(self, widget = None, event = None):
        """ calcola il prezzo netto """
        self._righe[0]["quantita"] = float(self.quantita_entry.get_text() or 0)
        self._righe[0]["prezzoLordo"] = float(self.prezzo_lordo_entry.get_text() or 0)
        self._righe[0]["percentualeIva"] = float(self.percentuale_iva_entry.get_text() or 0)
        self._righe[0]["applicazioneSconti"] = self.sconti_widget.getApplicazione()
        self._righe[0]["prezzoNetto"] = self._righe[0]["prezzoLordo"]
        self._righe[0]["sconti"] = self.sconti_widget.getSconti()
        self._righe[0]["applicazioneSconti"] = self.sconti_widget.getApplicazione()

        self.getPrezzoNetto()
        self.prezzo_netto_label.set_text(('%14.' + Environment.conf.decimals + 'f') % float(self._righe[0]["prezzoNetto"]))
        self.calcolaTotaleRiga()
        return False


    def calcolaTotaleRiga(self):
        """ calcola il totale riga """
        if self._righe[0]["prezzoNetto"] is None:
            self._righe[0]["prezzoNetto"] = 0
        if self._righe[0]["quantita"] is None:
            self._righe[0]["quantita"] = 0
        if self._righe[0]["moltiplicatore"] is None:
            self._righe[0]["moltiplicatore"] = 1
        elif float(self._righe[0]["moltiplicatore"]) == 0:
            self._righe[0]["moltiplicatore"] = 1

        self.getTotaleRiga()
        self.totale_riga_label.set_text(('%14.2f') % round(float(self._righe[0]["totale"]), 2))


    def calcolaTotale(self):
        """ calcola i totali movimento """

        totaleImponibile = float(0)
        totaleImposta = float(0)
        totaleNonScontato = float(0)

        castellettoIva = {}

        for i in range(1, len(self._righe)):
            prezzoNetto = float(self._righe[i]["prezzoNetto"])
            quantita = float(self._righe[i]["quantita"])
            moltiplicatore = float(self._righe[i]["moltiplicatore"])
            percentualeIva = float(self._righe[i]["percentualeIva"])

            totaleRiga = prezzoNetto * quantita * moltiplicatore
            percentualeIvaRiga = percentualeIva

            if (self._fonteValore == "vendita_iva" or
                self._fonteValore == "acquisto_iva"):
                totaleImponibileRiga = calcolaPrezzoIva(totaleRiga, -1 * percentualeIvaRiga)
            else:
                totaleImponibileRiga = float(totaleRiga)
                totaleRiga = calcolaPrezzoIva(totaleRiga, percentualeIvaRiga)

            totaleRiga = round(totaleRiga, 2)
            totaleImponibileRiga = round(totaleImponibileRiga, 2)

            totaleImpostaRiga = totaleRiga - totaleImponibileRiga
            totaleNonScontato += totaleRiga
            totaleImponibile += totaleImponibileRiga
            totaleImposta += totaleImpostaRiga

            if percentualeIvaRiga not in castellettoIva.keys():
                castellettoIva[percentualeIvaRiga] = {'imponibile': totaleImponibileRiga, 'imposta': totaleImpostaRiga, 'totale': totaleRiga}
            else:
                castellettoIva[percentualeIvaRiga]['imponibile'] += totaleImponibileRiga
                castellettoIva[percentualeIvaRiga]['imposta'] += totaleImpostaRiga
                castellettoIva[percentualeIvaRiga]['totale'] += totaleRiga

        self.totale_generale_label.set_text(('%14.2f') % float(totaleNonScontato))
        self.totale_generale_riepiloghi_label.set_text(('%14.2f') % float(totaleNonScontato))
        self.totale_imponibile_label.set_text(('%14.2f') % float(totaleImponibile))
        self.totale_imponibile_riepiloghi_label.set_text(('%14.2f') % float(totaleImponibile))
        self.totale_imposta_label.set_text(('%14.2f') % float(totaleImposta))
        self.totale_imposta_riepiloghi_label.set_text(('%14.2f') % float(totaleImposta))

        model = self.riepiloghi_iva_treeview.get_model()
        model.clear()
        for k in castellettoIva.keys():
            model.append(('%5.2f' % float(k),
                         ('%14.2f') % float(castellettoIva[k]['imponibile']),
                         ('%14.2f') % float(castellettoIva[k]['imposta'])))


    # ---


    def showMessage(self, msg):
        dialog = gtk.MessageDialog(self.dialogTopLevel, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg)
        dialog.run()
        dialog.destroy()


    def on_storico_costi_button_clicked(self, toggleButton):
        from StoricoForniture import StoricoForniture
        idArticolo = self._righe[0]["idArticolo"]
        if self._tipoPersonaGiuridica == "fornitore":
            idFornitore = self.id_persona_giuridica_customcombobox.getId()
        else:
            idFornitore = None

        anag = StoricoForniture(idArticolo, idFornitore)
        anagWindow = anag.getTopLevel()
        anagWindow.set_transient_for(self.dialogTopLevel)
        anagWindow.show_all()


    def on_storico_listini_button_clicked(self, toggleButton):
        from StoricoListini import StoricoListini
        idArticolo = self._righe[0]["idArticolo"]

        anag = StoricoListini(idArticolo)

        anagWindow = anag.getTopLevel()
        anagWindow.set_transient_for(self.dialogTopLevel)
        anagWindow.show_all()


    def on_variazione_listini_button_clicked(self, toggleButton):
        if self._righe[0]["idArticolo"] is None:
            self.showMessage('Selezionare un articolo !')
            return

        from VariazioneListini import VariazioneListini
        idArticolo = self._righe[0]["idArticolo"]
        costoNuovo = None
        costoUltimo = None
        if self._tipoPersonaGiuridica == "fornitore":
            costoNuovo = float(self._righe[0]["prezzoNetto"])
            costoUltimo = float(self._righe[0]["prezzoNettoUltimo"])
        anag = VariazioneListini(idArticolo, costoUltimo, costoNuovo)
        anagWindow = anag.getTopLevel()
        anagWindow.set_transient_for(self.dialogTopLevel)
        anagWindow.show_all()


    # ---


    def on_edit_date_and_number_button_clicked(self, toggleButton):
        msg = 'Attenzione! Si sta per variare i riferimenti primari del movimento.\n Continuare ?'
        dialog = gtk.MessageDialog(self.dialogTopLevel, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_YES:
            self.data_movimento_entry.set_sensitive(True)
            self.numero_movimento_entry.set_sensitive(True)
            self.data_movimento_entry.grab_focus()
            self.id_persona_giuridica_customcombobox.set_sensitive(True)


    def showDatiDocumento(self):
        stringLabel = '-'
        if self.dao.id_testata_documento is not None:
            #queryString = ('SELECT data_documento, numero, parte FROM ' +
                           #Environment.connection._schemaAzienda +
                           #'.testata_documento WHERE id = ' + str(self.dao.id_testata_documento))
            #argList = []
            #Environment.connection._cursor.execute(queryString, argList)
            #res = Environment.connection._cursor.fetchall()
            res = TestataDocumento(id = self.dao.id_testata_documento).getRecord()
            if res:
                stringLabel = 'N.' + str(res.numero) + ' del ' + dateToString(res.data_documento)

        self.rif_documento_label.set_text(stringLabel)
