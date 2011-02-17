# -*- coding: utf-8 -*-

#    Copyright (C) 2005, 2006, 2007 2008, 2009, 2010 by Promotux
#                        di Francesco Meloni snc - http://www.promotux.it/

#    Author: Francesco Meloni  <francesco@promotux.it>
#    Author: Andrea Argiolas <andrea@promotux.it>
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

import gtk
from sqlalchemy.orm import join
from sqlalchemy import or_
from AnagraficaComplessa import Anagrafica, AnagraficaFilter, \
                        AnagraficaHtml, AnagraficaReport, AnagraficaEdit
import promogest.dao.Cliente
from promogest import Environment
from promogest.dao.Cliente import Cliente
from promogest.dao.PersonaGiuridica import PersonaGiuridica_
from promogest.dao.ClienteCategoriaCliente import ClienteCategoriaCliente
from promogest.modules.Contatti.dao.ContattoCliente import ContattoCliente
from promogest.dao.RecapitoContatto import RecapitoContatto
from promogest.dao.Contatto import Contatto
from promogest.dao.DaoUtils import *
from utils import *
from utilsCombobox import *
if posso("IP"):
    from promogest.modules.InfoPeso.ui.InfoPesoNotebookPage import InfoPesoNotebookPage
    from promogest.modules.InfoPeso.dao.TestataInfoPeso import TestataInfoPeso

class AnagraficaClientiEdit(AnagraficaEdit):
    """ Modifica un record dell'anagrafica dei clienti """

    def __init__(self, anagrafica):
        AnagraficaEdit.__init__(self,
                                anagrafica,
                                'anagrafica_clienti_detail_notebook',
                                'Dati cliente',
                                gladeFile='_anagrafica_clienti_elements.glade')
        self._widgetFirstFocus = self.codice_entry

    def draw(self,cplx=False):
        #Popola combobox categorie clienti
        fillComboboxCategorieClienti(self.id_categoria_cliente_customcombobox.combobox)
        self.id_categoria_cliente_customcombobox.connect('clicked',
                                                         on_id_categoria_cliente_customcombobox_clicked)
        #Elenco categorie
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn('Categoria', rendererText, text=1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(True)
        column.set_expand(True)
        self.categorie_treeview.append_column(column)

        rendererPixbuf = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn('', rendererPixbuf, pixbuf=2)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
        column.set_clickable(False)
        column.set_resizable(False)
        column.set_expand(False)
        column.set_min_width(20)
        self.categorie_treeview.append_column(column)

        model = gtk.ListStore(int, str, gtk.gdk.Pixbuf, str)
        self.categorie_treeview.set_model(model)

        fillComboBoxNazione(self.nazione_combobox, default="Italia")

        fillComboboxPagamenti(self.id_pagamento_customcombobox.combobox)
        self.id_pagamento_customcombobox.connect('clicked',
                                 on_id_pagamento_customcombobox_clicked)
        fillComboboxMagazzini(self.id_magazzino_customcombobox.combobox)
        self.id_magazzino_customcombobox.connect('clicked',
                                 on_id_magazzino_customcombobox_clicked)
        fillComboboxListini(self.id_listino_customcombobox.combobox)
        self.id_listino_customcombobox.connect('clicked',
                               on_id_listino_customcombobox_clicked)
        fillComboboxBanche(self.id_banca_customcombobox.combobox)
        self.id_banca_customcombobox.connect('clicked',
                                 on_id_banca_customcombobox_clicked)
        fillComboboxAliquoteIva(self.id_aliquota_iva_customcombobox.combobox)
        self.id_aliquota_iva_customcombobox.connect('clicked',
                                on_id_aliquota_iva_customcombobox_clicked)

#        if not setconf(key="INFOPESO", section="General"):
        if posso("IP"):
            self.infopeso_page = InfoPesoNotebookPage(self, "")
            self.infopeso_page_label = gtk.Label()
            self.infopeso_page_label.set_markup("<b>INFO PESO</b>")
            self.anagrafica_clienti_detail_notebook.append_page(self.infopeso_page.infopeso_frame, self.infopeso_page_label)



    def on_categorie_clienti_add_row_button_clicked(self, widget):
        """
        Aggiunge una categoria cliente al dao selezionato
        """
        id = findIdFromCombobox(self.id_categoria_cliente_customcombobox.combobox)
        if id is not None:
            categoria = findStrFromCombobox(self.id_categoria_cliente_customcombobox.combobox, 2)
            model = self.categorie_treeview.get_model()
            for c in model:
                if c[0] == id:
                    return
            image = gtk.Image()
            anagPixbuf = image.render_icon(gtk.STOCK_ADD,
                                               gtk.ICON_SIZE_BUTTON)
            model.append((id, categoria, anagPixbuf, 'added'))
        self.categorie_treeview.get_selection().unselect_all()

    def on_categorie_clienti_delete_row_button_clicked(self, widget):
        """
        Rimuove una categoria al dao selezionato
        """
        id = findIdFromCombobox(self.id_categoria_cliente_customcombobox.combobox)
        if id is not None:
            image = gtk.Image()
            anagPixbuf = image.render_icon(gtk.STOCK_REMOVE,
                                           gtk.ICON_SIZE_BUTTON)
            model = self.categorie_treeview.get_model()
            for c in model:
                if c[0] == id:
                    if c[2] is None:
                        c[2] = anagPixbuf
                        c[3] = 'deleted'
                    else:
                        model.remove(c.iter)
        self.categorie_treeview.get_selection().unselect_all()

    def on_categorie_clienti_undelete_row_button_clicked(self, widget):
        id = findIdFromCombobox(self.id_categoria_cliente_customcombobox.combobox)
        if id is not None:
            model = self.categorie_treeview.get_model()
            for c in model:
                if c[0] == id:
                    if c[3] == 'deleted':
                        c[2] = None
                        c[3] = None
        self.categorie_treeview.get_selection().unselect_all()

    def on_categorie_treeview_cursor_changed(self, treeview = None):
        """ quando si clicca su una riga della treeview """
        sel = treeview.get_selection()
        (model, iterator) = sel.get_selected()
        if iterator is not None:
            idCategoriaCliente = model.get_value(iterator, 0)
            findComboboxRowFromId(self.id_categoria_cliente_customcombobox.combobox, idCategoriaCliente)
            status = model.get_value(iterator, 3)
            self.categorie_clienti_delete_row_button.set_sensitive(status != 'deleted')
            self.categorie_clienti_undelete_row_button.set_sensitive(status == 'deleted')

    def setDao(self, dao):
        if dao is None:
            # Crea un nuovo Dao vuoto
            self.dao = Cliente()
            self.dao.codice = promogest.dao.Cliente.getNuovoCodiceCliente()
            self._oldDaoRicreato = False
        else:
            # Ricrea il Dao con una connessione al DBMS SQL
            self.dao = Cliente().getRecord(id=dao.id)
            self._oldDaoRicreato = True

        if posso("IP"):
            self.infopeso_page.infoPesoSetDao(self.dao)
            self.infopeso_page.nome_cognome_label.set_text(str(self.dao.ragione_sociale) or ""+"\n"+str(self.dao.cognome) or ""+" "+str(self.dao.nome) or "")

        if not self.dao.id:
            self.dao_contatto = ContattoCliente()
        else:
            self.dao_contatto = ContattoCliente().select(idCliente=self.dao.id)
            if self.dao_contatto:
                self.dao_contatto = self.dao_contatto[0]
            else:
                self.dao_contatto = ContattoCliente()
        self._refresh()
        return self.dao

    def _refresh(self):
        self.codice_entry.set_text(self.dao.codice or '')
        self.ragione_sociale_entry.set_text(self.dao.ragione_sociale or '')
        self.insegna_entry.set_text(self.dao.insegna or '')
        self.cognome_entry.set_text(self.dao.cognome or '')
        self.nome_entry.set_text(self.dao.nome or '')
        self.indirizzo_sede_operativa_entry.set_text(self.dao.sede_operativa_indirizzo or '')
        self.cap_sede_operativa_entry.set_text(self.dao.sede_operativa_cap or '')
        self.localita_sede_operativa_entry.set_text(self.dao.sede_operativa_localita or '')
        self.provincia_sede_operativa_entry.set_text(self.dao.sede_operativa_provincia or '')
        self.indirizzo_sede_legale_entry.set_text(self.dao.sede_legale_indirizzo or '')
        self.cap_sede_legale_entry.set_text(self.dao.sede_legale_cap or '')
        self.localita_sede_legale_entry.set_text(self.dao.sede_legale_localita or '')
        self.provincia_sede_legale_entry.set_text(self.dao.sede_legale_provincia or '')
        self.codice_fiscale_entry.set_text(self.dao.codice_fiscale or '')
        self.partita_iva_entry.set_text(self.dao.partita_iva or '')

        self.id_categoria_cliente_customcombobox.combobox.set_active(-1)
        self._refreshCategorie()

        findComboboxRowFromId(self.id_pagamento_customcombobox.combobox,
                              self.dao.id_pagamento)
        findComboboxRowFromId(self.id_magazzino_customcombobox.combobox,
                              self.dao.id_magazzino)
        findComboboxRowFromId(self.id_listino_customcombobox.combobox,
                              self.dao.id_listino)
        findComboboxRowFromId(self.id_banca_customcombobox.combobox,
                              self.dao.id_banca)
        findComboboxRowFromStr(self.nazione_combobox,self.dao.nazione, 0)
        #finComboBoxNazione(self.nazione_combobox, default="Italia")
        #if Environment.conf.hasPagamenti == True:
        if posso("IP"):
            self.infopeso_page.infoPeso_refresh()
        self.showTotaliDareAvere()
        self.cellulare_principale_entry.set_text("")
        self.telefono_principale_entry.set_text("")
        self.email_principale_entry.set_text("")
        self.fax_principale_entry.set_text("")
        self.sito_web_principale_entry.set_text("")
        for reca in getRecapitiContatto(self.dao_contatto.id):
            if reca.tipo_recapito =="Cellulare":
                self.cellulare_principale_entry.set_text(reca.recapito)
            elif reca.tipo_recapito=="Telefono":
                self.telefono_principale_entry.set_text(reca.recapito)
            elif reca.tipo_recapito =="Email":
                self.email_principale_entry.set_text(reca.recapito)
            elif reca.tipo_recapito =="Fax":
                self.fax_principale_entry.set_text(reca.recapito)
            elif reca.tipo_recapito =="Sito":
                self.sito_web_principale_entry.set_text(reca.recapito)

    def showTotaliDareAvere(self):

        if self.dao.id:
            totaleDareAnnuale = TotaleAnnualeCliente(id_cliente=self.dao.id)
            self.totale_annuale_dare_entry.set_text(str(mN(totaleDareAnnuale,2)))
            # Calcoliamo il totale sospeso:
            totaleDareAperto = TotaleClienteAperto(id_cliente=self.dao.id)
            self.totale_dare_entry.set_text(str(mN(totaleDareAperto,2)))

        self.anagrafica_clienti_detail_notebook.set_current_page(0)

    def _refreshCategorie(self, widget=None, orderBy=None):

        model = self.categorie_treeview.get_model()
        model.clear()
        if not self.dao.id:
            return
        categorie = self.dao.categorieCliente
        for c in categorie:
            model.append([c.id_categoria_cliente, c.categoria_cliente.denominazione, None, None])

    def saveDao(self):
        self.verificaListino()
        self.dao.codice = self.codice_entry.get_text()
        self.dao.codice = omogeneousCode(section="Clienti", string=self.dao.codice )
        self.dao.ragione_sociale = self.ragione_sociale_entry.get_text()
        self.dao.insegna = self.insegna_entry.get_text()
        self.dao.cognome= self.cognome_entry.get_text()
        self.dao.nome= self.nome_entry.get_text()
        if (self.dao.codice and (self.dao.ragione_sociale or self.dao.insegna or self.dao.cognome or self.dao.nome)) =='':
            msg="""Il codice è obbligatorio.
    Inserire almeno un campo a scelta tra:
    ragione sociale, insegna, cognome o nome """
            dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg)
            dialog.run()
            dialog.destroy()
            raise Exception, 'Operation aborted Campo minimo cliente non inserito'
        self.dao.sede_operativa_indirizzo = self.indirizzo_sede_operativa_entry.get_text()
        self.dao.sede_operativa_cap = self.cap_sede_operativa_entry.get_text()
        self.dao.sede_operativa_localita = self.localita_sede_operativa_entry.get_text()
        self.dao.sede_operativa_provincia = self.provincia_sede_operativa_entry.get_text()
        self.dao.sede_legale_indirizzo = self.indirizzo_sede_legale_entry.get_text()
        self.dao.sede_legale_cap = self.cap_sede_legale_entry.get_text()
        self.dao.sede_legale_localita = self.localita_sede_legale_entry.get_text()
        self.dao.sede_legale_provincia = self.provincia_sede_legale_entry.get_text()
        self.dao.codice_fiscale = self.codice_fiscale_entry.get_text()
        self.dao.partita_iva = self.partita_iva_entry.get_text()
        if self.dao.partita_iva != '':
            partiva = checkPartIva(self.dao.partita_iva)
            if not partiva:
                raise Exception, 'Operation aborted: Partita iva non corretta'
        self.dao.id_pagamento = findIdFromCombobox(self.id_pagamento_customcombobox.combobox)
        self.dao.id_magazzino = findIdFromCombobox(self.id_magazzino_customcombobox.combobox)
        self.dao.id_listino = findIdFromCombobox(self.id_listino_customcombobox.combobox)
        self.dao.id_banca = findIdFromCombobox(self.id_banca_customcombobox.combobox)
        self.dao.nazione = findStrFromCombobox(self.nazione_combobox,0)
        if self.dao.codice_fiscale != '':
            codfis = checkCodFisc(self.dao.codice_fiscale)
            if not codfis:
                raise Exception, 'Operation aborted: Codice Fiscale non corretto'
        self.dao.persist()
        if posso("IP"):
            (dao_testata_infopeso, dao_generalita_infopeso) = self.infopeso_page.infoPesoSaveDao()
            dao_testata_infopeso.id_cliente = self.dao.id
            dao_testata_infopeso.persist()
            dao_generalita_infopeso.id_cliente = self.dao.id
            dao_generalita_infopeso.persist()

        model = self.categorie_treeview.get_model()
        cleanClienteCategoriaCliente = ClienteCategoriaCliente()\
                                                    .select(idCliente=self.dao.id,
                                                    batchSize=None)
        for cli in cleanClienteCategoriaCliente:
            cli.delete()
        for c in model:
            if c[3] == 'deleted':
                pass
            else:
                daoClienteCategoriaCliente = ClienteCategoriaCliente()
                daoClienteCategoriaCliente.id_cliente = self.dao.id
                daoClienteCategoriaCliente.id_categoria_cliente = c[0]
                daoClienteCategoriaCliente.persist()
        #self.dao.categorieCliente = categorie
        self._refreshCategorie()
        #SEzione dedicata ai contatti/recapiti principali
        if Environment.tipo_eng =="sqlite" and not self.dao.id:
            forMaxId = Contatto().select(batchSize=None)
            if not forMaxId:
                self.dao_contatto.id = 1
            else:
                idss = []
                for l in forMaxId:
                    idss.append(l.id)
                self.dao_contatto.id = (max(idss)) +1
        self.dao_contatto.tipo_contatto ="cliente"
        self.dao_contatto.id_cliente =self.dao.id
        self.dao_contatto.persist()

        recont = RecapitoContatto().select(idContatto=self.dao_contatto.id,tipoRecapito="Cellulare")
        if recont:
            reco = recont[0]
            if self.cellulare_principale_entry.get_text() =="" or reco.recapito=="":
                reco.delete()
            else:
                reco.id_contatto = self.dao_contatto.id
                reco.tipo_recapito = "Cellulare"
                reco.recapito = self.cellulare_principale_entry.get_text()
                reco.persist()

        else:
            reco = RecapitoContatto()
            reco.id_contatto = self.dao_contatto.id
            reco.tipo_recapito = "Cellulare"
            reco.recapito = self.cellulare_principale_entry.get_text()
            reco.persist()

        recont = RecapitoContatto().select(idContatto=self.dao_contatto.id,tipoRecapito="Telefono")
        if recont:
            reco = recont[0]
            if self.telefono_principale_entry.get_text() =="" or reco.recapito=="":
                reco.delete()
            else:
                reco.id_contatto = self.dao_contatto.id
                reco.tipo_recapito = "Telefono"
                reco.recapito = self.telefono_principale_entry.get_text()
                reco.persist()
        else:
            reco = RecapitoContatto()
            reco.id_contatto = self.dao_contatto.id
            reco.tipo_recapito = "Telefono"
            reco.recapito = self.telefono_principale_entry.get_text()
            reco.persist()


        recont = RecapitoContatto().select(idContatto=self.dao_contatto.id,tipoRecapito="Email")
        if recont:
            reco = recont[0]
            if self.email_principale_entry.get_text() =="" or reco.recapito=="":
                reco.delete()
            else:
                reco.id_contatto = self.dao_contatto.id
                reco.tipo_recapito = "Email"
                reco.recapito = self.email_principale_entry.get_text()
                reco.persist()
        else:
            reco = RecapitoContatto()
            reco.id_contatto = self.dao_contatto.id
            reco.tipo_recapito = "Email"
            reco.recapito = self.email_principale_entry.get_text()
            reco.persist()

        recontw = RecapitoContatto().select(idContatto=self.dao_contatto.id,tipoRecapito="Sito")
        if recontw:
            recow = recontw[0]
            if self.sito_web_principale_entry.get_text() =="" or recow.recapito=="":
                recow.delete()
            else:
                recow.id_contatto = self.dao_contatto.id
                recow.tipo_recapito = "Sito"
                recow.recapito = self.sito_web_principale_entry.get_text()
                recow.persist()
        else:
            recow = RecapitoContatto()
            recow.id_contatto = self.dao_contatto.id
            recow.tipo_recapito = "Sito"
            recow.recapito = self.sito_web_principale_entry.get_text()
            recow.persist()

        recont = RecapitoContatto().select(idContatto=self.dao_contatto.id,tipoRecapito="Fax")
        if recont:
            reco = recont[0]
            if self.fax_principale_entry.get_text() =="" or reco.recapito=="":
                reco.delete()
            else:
                reco.id_contatto = self.dao_contatto.id
                reco.tipo_recapito = "Fax"
                reco.recapito = self.fax_principale_entry.get_text()
                reco.persist()
        else:
            reco = RecapitoContatto()
            reco.id_contatto = self.dao_contatto.id
            reco.tipo_recapito = "Fax"
            reco.recapito = self.fax_principale_entry.get_text()
            reco.persist()

    def on_scheda_contabile_togglebutton_clicked(self, toggleButton):
        """
        Apre la finestra di registrazione documenti, ricercando solo
        i documenti del cliente
        """

        if not(toggleButton.get_active()):
            toggleButton.set_active(False)
            return

        if self.dao.id is None:
            msg = 'Prima di poter visualizzare la registrazione documenti occorre salvare il cliente.\n Salvare? '
            dialog = gtk.MessageDialog(self.dialogTopLevel,
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_QUESTION,
                    gtk.BUTTONS_YES_NO,
                    msg)
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                self.on_anagrafica_complessa_detail_dialog_response(
                        self.dialogTopLevel, gtk.RESPONSE_APPLY)
            else:
                toggleButton.set_active(False)
                return

        from AnagraficaDocumenti import AnagraficaDocumenti
        anag = AnagraficaDocumenti()
        anagWindow = anag.getTopLevel()
        showAnagraficaRichiamata(self.dialogTopLevel, anagWindow,
                toggleButton)
        anag.filter.id_cliente_filter_customcombobox.setId(self.dao.id)
        anag.filter.refresh()

    def on_contatti_togglebutton_clicked(self, toggleButton):
        if not(toggleButton.get_active()):
            toggleButton.set_active(False)
            return
        if posso("CN"):
            if self.dao.id is None:
                msg = 'Prima di poter inserire i contatti occorre salvare il cliente.\n Salvare ?'
                dialog = gtk.MessageDialog(self.dialogTopLevel,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
                        msg)
                response = dialog.run()
                dialog.destroy()
                if response == gtk.RESPONSE_YES:
                    self.on_anagrafica_complessa_detail_dialog_response(self.dialogTopLevel, gtk.RESPONSE_APPLY)
                else:
                    toggleButton.set_active(False)
                    return

            from promogest.modules.Contatti.ui.AnagraficaContatti import AnagraficaContatti
            anag = AnagraficaContatti(self.dao.id, 'cliente')
            anagWindow = anag.getTopLevel()

            showAnagraficaRichiamata(self.dialogTopLevel, anagWindow, toggleButton)
        else:
            fenceDialog()
            toggleButton.set_active(False)

    def on_destinazioni_merce_togglebutton_clicked(self, toggleButton):
        if not(toggleButton.get_active()):
            toggleButton.set_active(False)
            return

        if self.dao.id is None:
            msg = 'Prima di poter inserire le destinazioni merce occorre salvare il cliente.\n Salvare ?'
            dialog = gtk.MessageDialog(self.dialogTopLevel, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                       gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, msg)
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                self.on_anagrafica_complessa_detail_dialog_response(self.dialogTopLevel, gtk.RESPONSE_APPLY)
            else:
                toggleButton.set_active(False)
                return

        from AnagraficaDestinazioniMerce import AnagraficaDestinazioniMerce
        anag = AnagraficaDestinazioniMerce(self.dao.id)
        anagWindow = anag.getTopLevel()

        showAnagraficaRichiamata(self.dialogTopLevel, anagWindow, toggleButton)

    def verificaListino(self):
        """ Verifica se il listino inserito e' compatibile con le categorie e il magazzino associati al cliente """
        from promogest.dao.ListinoCategoriaCliente import ListinoCategoriaCliente
        from promogest.dao.ListinoMagazzino import ListinoMagazzino
        listino = findIdFromCombobox(self.id_listino_customcombobox.combobox)
        #FIXME : ricontrollare
        #if listino is not None:
            #categoriaOk = True
            #magazzinoOk = True
            #model = self.categorie_treeview.get_model()
            #categorie = set(c[0] for c in model if c[3] != 'deleted')
            #categorieListino = set(c.id_categoria_cliente for c in ListinoCategoriaCliente()\
                                        #.select(idListino=listino,batchSize=None, orderBy="id_listino"))
            #categoriaOk = len(categorieListino.intersection(categorie)) > 0
            #magazzino = findIdFromCombobox(self.id_magazzino_customcombobox.combobox)
            #if magazzino is not None:
                #magazziniListino = set(m.id_magazzino for m in ListinoMagazzino()\
                                        #.select(idListino=listino,batchSize=None, orderBy="id_listino"))
                #magazzinoOk = (magazzino in magazziniListino)
            #if not(categoriaOk and magazzinoOk):
                #msg = 'Il listino inserito non sembra compatibile con il magazzino e le categorie indicate.\nContinuare ?'
                #dialog = gtk.MessageDialog(self.dialogTopLevel, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                           #gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO, msg)
                #response = dialog.run()
                #dialog.destroy()
                #if response != gtk.RESPONSE_YES:
                    #raise Exception, 'Operation aborted'
