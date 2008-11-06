# -*- coding: iso-8859-15 -*-

"""
 Promogest
 Copyright (C) 2005-2008 by Promotux Informatica - http://www.promotux.it/
 Author: Andrea Argiolas <andrea@promotux.it>
 Author: Francesco Meloni <francesco@promotux.it>
 License: GNU GPLv2
 """

import gtk
from GladeWidget import GladeWidget

from promogest import Environment
from promogest.dao.Dao import Dao
import promogest.dao.Articolo
from promogest.dao.Articolo import Articolo
import promogest.dao.CodiceABarreArticolo
from promogest.dao.CodiceABarreArticolo import CodiceABarreArticolo
import promogest.dao.ListinoArticolo
from promogest.dao.ListinoArticolo import ListinoArticolo

from utils import *
from utilsCombobox import *
import datetime


class AnagraficaArticoliSemplice(GladeWidget):

    def __init__(self):
        GladeWidget.__init__(self, 'anagrafica_articoli_semplice_dialog', fileName='anagrafica_articoli_semplice_dialog.glade')

        self.placeWindow(self.getTopLevel())
        self._loading = False
        self._codiceByFamiglia = promogest.dao.Articolo.isNuovoCodiceByFamiglia()

        # Crea un nuovo Dao vuoto
        self.daoArticolo = Articolo().getRecord()
        self.daoCodiceABarreArticolo = None
        self.daoListinoArticolo = None

        # Assegna il codice se ne e' prevista la crazione automatica, ma non per famiglia
        if not self._codiceByFamiglia:
            self.daoArticolo.codice = promogest.dao.Articolo.getNuovoCodiceArticolo()

        self.draw()


    def draw(self):
        #Popola combobox aliquote iva
        fillComboboxAliquoteIva(self.id_aliquota_iva_customcombobox.combobox)
        self.id_aliquota_iva_customcombobox.connect('clicked',
                                                    on_id_aliquota_iva_customcombobox_clicked)
        #Popola combobox categorie articolo
        fillComboboxCategorieArticoli(self.id_categoria_articolo_customcombobox.combobox)
        self.id_categoria_articolo_customcombobox.connect('clicked',
                                                          on_id_categoria_articolo_customcombobox_clicked)
        #Popola combobox famiglie articolo
        fillComboboxFamiglieArticoli(self.id_famiglia_articolo_customcombobox.combobox)
        self.id_famiglia_articolo_customcombobox.connect('clicked',
                                                         on_id_famiglia_articolo_customcombobox_clicked)
        if self._codiceByFamiglia:
            #Collega la creazione di un nuovo codice articolo al cambiamento della famiglia
            self.id_famiglia_articolo_customcombobox.combobox.connect('changed',
                                                                      self.on_id_famiglia_articolo_customcombobox_changed)
        #Popola combobox listini
        fillComboboxListini(self.id_listino_customcombobox.combobox)
        self.id_listino_customcombobox.connect('clicked',
                                               on_id_listino_customcombobox_clicked)
        self.id_listino_customcombobox.combobox.connect('changed',
                                                        self.on_id_listino_customcombobox_changed)

        #Popola combobox unita base
        fillComboboxUnitaBase(self.id_unita_base_combobox)

        # Seleziona Pezzi come unita' di default
        findComboboxRowFromId(self.id_unita_base_combobox, 1)

        # Seleziona il listino di default
        try:
            findComboboxRowFromStr(self.id_listino_customcombobox.combobox, Environment.conf.Dettaglio.listino, 2)
        except:
            pass

        if self._codiceByFamiglia:
            self.codice_a_barre_entry.grab_focus()
        else:
            self.codice_entry.set_text(self.daoArticolo.codice or '')
            if emptyStringToNone(self.daoArticolo.codice) is None:
                self.codice_entry.grab_focus()
            else:
                self.codice_a_barre_entry.grab_focus()

        self.getTopLevel().show_all()


    def on_confirm_button_clicked(self, button=None):
        if (self.codice_entry.get_text() == ''):
            obligatoryField(self.getTopLevel(), self.codice_entry)

        if (self.denominazione_entry.get_text() == ''):
            obligatoryField(self.getTopLevel(), self.denominazione_entry)

        if (self.produttore_entry.get_text() == ''):
            obligatoryField(self.getTopLevel(), self.produttore_entry)

        if findIdFromCombobox(self.id_famiglia_articolo_customcombobox.combobox) is None:
            obligatoryField(self.getTopLevel(), self.id_famiglia_articolo_customcombobox.combobox)

        if findIdFromCombobox(self.id_categoria_articolo_customcombobox.combobox) is None:
            obligatoryField(self.getTopLevel(), self.id_categoria_articolo_customcombobox.combobox)

        if findIdFromCombobox(self.id_aliquota_iva_customcombobox.combobox) is None:
            obligatoryField(self.getTopLevel(), self.id_aliquota_iva_customcombobox.combobox)

        if findIdFromCombobox(self.id_unita_base_combobox) is None:
            obligatoryField(self.getTopLevel(), self.id_unita_base_combobox)

        # controllo esistenza codice articolo
        arts = Articolo(isList=True).select(codice = self.codice_entry.get_text(),
                                                        offset = None,
                                                        batchSize = None)

        if len(arts) > 0:
            msg = "Codice articolo gia' assegnato: !"
            dialog = gtk.MessageDialog(self.getTopLevel(),
                                       gtk.DIALOG_MODAL
                                       | gtk.DIALOG_DESTROY_WITH_PARENT,
                                       gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                       msg)
            dialog.run()
            dialog.destroy()

            self.codice_entry.grab_focus()
            raise Exception, 'Operation aborted'

        # controllo esistenza codice a barre su altro articolo
        bars = CodiceABarreArticolo(isList=True).select(idArticolo=None,
                                    codice=self.codice_a_barre_entry.get_text(),
                                    offset=None,
                                    batchSize=None)
        if len(bars) > 0:
            articolo = leggiArticolo(bars[0].id_articolo)
            msg = "Codice a barre gia' assegnato all'articolo: \n\nCod. " + articolo["codice"] + " (" + articolo["denominazione"] + ")"
            dialog = gtk.MessageDialog(self.getTopLevel(),
                                       gtk.DIALOG_MODAL
                                       | gtk.DIALOG_DESTROY_WITH_PARENT,
                                       gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                       msg)
            dialog.run()
            dialog.destroy()

            self.codice_a_barre_entry.grab_focus()
            raise Exception, 'Operation aborted'

        self.save()
        self.quit()


    def save(self):
        """ Salvataggio nuovo articolo """
        try:
            self.daoArticolo.codice = self.codice_entry.get_text()
            self.daoArticolo.denominazione = self.denominazione_entry.get_text()
            self.daoArticolo.id_aliquota_iva = findIdFromCombobox(self.id_aliquota_iva_customcombobox.combobox)
            self.daoArticolo.id_famiglia_articolo = findIdFromCombobox(self.id_famiglia_articolo_customcombobox.combobox)
            self.daoArticolo.id_categoria_articolo = findIdFromCombobox(self.id_categoria_articolo_customcombobox.combobox)
            self.daoArticolo.id_unita_base = findIdFromCombobox(self.id_unita_base_combobox)
            self.daoArticolo.produttore = self.produttore_entry.get_text()
            self.daoArticolo.cancellato = False
            self.daoArticolo.sospeso = False
            self.daoArticolo.url_immagine=None
            self.daoArticolo.id_immagine=None
            self.daoArticolo.persist()

            if self.codice_a_barre_entry.get_text() != '':
                self.daoCodiceABarreArticolo = CodiceABarreArticolo().getRecord()
                self.daoCodiceABarreArticolo.codice = self.codice_a_barre_entry.get_text()
                self.daoCodiceABarreArticolo.id_articolo = self.daoArticolo.id
                self.daoCodiceABarreArticolo.primario = True
                self.daoCodiceABarreArticolo.persist()

            if findIdFromCombobox(self.id_listino_customcombobox.combobox) is not None:
                try:
                    prezzoDettaglio = float(self.prezzo_dettaglio_entry.get_text())
                except:
                    self.prezzo_dettaglio_entry.set_text('')
                    prezzoDettaglio = float(0)
                try:
                    prezzoIngrosso = float(self.prezzo_ingrosso_entry.get_text())
                except:
                    self.prezzo_ingrosso_entry.set_text('')
                    prezzoIngrosso = float(0)

                if prezzoDettaglio > 0 or prezzoIngrosso > 0:
                    self.daoListinoArticolo = ListinoArticolo().getRecord()
                    self.daoListinoArticolo.id_listino = findIdFromCombobox(self.id_listino_customcombobox.combobox)
                    self.daoListinoArticolo.id_articolo = self.daoArticolo.id
                    self.daoListinoArticolo.prezzo_dettaglio = prezzoDettaglio
                    self.daoListinoArticolo.prezzo_ingrosso = prezzoIngrosso
                    self.daoListinoArticolo.ultimo_costo = float(0)
                    self.daoListinoArticolo.data_listino_articolo = datetime.datetime.today()
                    self.daoListinoArticolo.listino_attuale = True
                    self.daoListinoArticolo.persist()
        except:
            raise


    def on_id_famiglia_articolo_customcombobox_changed(self, combobox):
        """ Restituisce un nuovo codice articolo al cambiamento della famiglia """

        if self._loading:
            return

        if not self._codiceByFamiglia:
            return

        idFamiglia = findIdFromCombobox(self.id_famiglia_articolo_customcombobox.combobox)
        if idFamiglia is not None:
            self.daoArticolo.codice = promogest.dao.Articolo.getNuovoCodiceArticolo(idFamiglia)
            self.codice_entry.set_text(self.daoArticolo.codice)


    def on_id_listino_customcombobox_changed(self, combobox):
        """ Abilita/disabilita i campi prezzo """

        idListino = findIdFromCombobox(self.id_listino_customcombobox.combobox)
        self.prezzo_dettaglio_entry.set_sensitive(idListino is not None)
        self.prezzo_ingrosso_entry.set_sensitive(idListino is not None)


    def on_anagrafica_articoli_semplice_dialog_close(self, widget, event=None):
        self.quit()


    def quit(self):
        self.destroy()
        return None
