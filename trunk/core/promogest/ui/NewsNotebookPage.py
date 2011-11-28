# -*- coding: utf-8 -*-

# Promogest
#
# Copyright (C) 2005-2009 by Promotux Informatica - http://www.promotux.it/
# Author: Francesco Meloni <francesco@promotux.it>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import webbrowser
from promogest.ui.utils import *
from promogest.dao.Setconf import SetConf
from promogest import Environment
from GladeWidget import GladeWidget
from promogest.lib.HtmlHandler import createHtmlObj, renderTemplate, renderHTML
from promogest.lib import feedparser
from promogest.ui.SendEmail import SendEmail

try:
    if Environment.pg3:
        from gi.repository.WebKit import WebView
    else:
        from webkit import WebView
    WEBKIT = True
except:
    import gtkhtml2
    WEBKIT = False

class NewsNotebookPage(GladeWidget):
    """ Widget di configurazione del codice installazione e dei parametri
    di configurazione """
    def __init__(self, main, azienda):
        GladeWidget.__init__(self, 'notizie_frame',
                                    'news_notebook.glade')
#        self.placeWindow(self.getTopLevel())
        self.rowBackGround = None
        self.main = main
        self.main_wind = main
        self.aziendaStr = azienda or ""
        gobject.idle_add(self.create_news_frame)

    def draw(self):
        return self

    def create_news_frame(self):
        """ CREIAMO IL TAB DELLE NEWS"""
        Environment.htmlwidget = createHtmlObj(self)
        self.feed_scrolled.add(Environment.htmlwidget)
        html = """<html><body>
<a style="text-color:black;" href="program:/recuperafeed">
<div style="text-align: center;">
    <img style="width: 530px; height: 110px;" alt="PROMOGEST" src="http://www.promotux.it/templates/promoGest/img/testata_promogest2.png"><br>
</div>
<div style="text-align:center;color:black;"><br />
    <h3 style="color:black;">HAI LETTO LE NOVITA' SUL TUO SOFTWARE GESTIONALE PREFERITO?</a></h3></div></body></html>"""
        renderHTML(Environment.htmlwidget,html)



        #if setconf("Feed", "feed"):
            #feedAll = Environment.feedAll
            #feedToHtml = Environment.feedCache
            #if feedAll != "" and feedAll and feedToHtml:
                #self.renderPage(feedToHtml)
            #else:
                #try:
                    #gobject.idle_add(self.getfeedFromSite)
                #except:
                    #Environment.pg2log.info("LEGGERO RITARDO NEL RECUPERO DEI FEED")

    def on_nuovo_articolo_button_clicked(self, widget):
        if not hasAction(actionID=8):return
        from AnagraficaArticoli import AnagraficaArticoli
        anag = AnagraficaArticoli(self.aziendaStr)
        showAnagrafica(self.getTopLevel(), anag)
        anag.on_record_new_activate()

    def on_nuovo_cliente_button_clicked(self, widget):
        if not hasAction(actionID=11):return
        from AnagraficaClienti import AnagraficaClienti
        anag = AnagraficaClienti(self.main_wind.aziendaStr)
        showAnagrafica(self.main_wind.getTopLevel(), anag)
        anag.on_record_new_activate()

    def on_nuovo_fornitore_button_clicked(self, widget):
        if not hasAction(actionID=11):return
        from AnagraficaFornitori import AnagraficaFornitori
        anag = AnagraficaFornitori(self.aziendaStr)
        showAnagrafica(self.getTopLevel(), anag)
        anag.on_record_new_activate()

    def on_nuovo_promemoria_button_clicked(self, widget):
        if not hasAction(actionID=11):return
        from AnagraficaPromemoria import AnagraficaPromemoria
        anag = AnagraficaPromemoria(self.aziendaStr)
        showAnagrafica(self.getTopLevel(), anag)
        anag.on_record_new_activate()

    def on_nuovo_contatto_button_clicked(self, widget):
        if not hasAction(actionID=11):return
        from promogest.modules.Contatti.ui.AnagraficaContatti import AnagraficaContatti
        anag = AnagraficaContatti(self.aziendaStr)
        showAnagrafica(self.getTopLevel(), anag)
        anag.on_record_new_activate()

    def on_nuovo_fattura_vendita_button_clicked(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("Fattura vendita")

    def on_nuovo_fattura_acquisto_button_clicked(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("Fattura acquisto")

    def on_nuovo_ddt_vendita_button_clicked(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("DDT vendita")

    def on_nuovo_ddt_acquisto_button_clicked(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("DDT acquisto")

    def on_nuovo_ddt_reso_da_cliente_button_clicked(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("DDT reso da cliente")

    def on_nuovo_ddt_reso_a_fornitore_button_clicked(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("DDT reso a fornitore")

    def on_nota_di_credito_a_cliente_button_clicked(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("Nota di credito a cliente")

    def on_nota_di_credito_a_fornitore_button_clicked(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("Nota di credito da fornitore")

    def on_fattura_accompagnatoria_menu_activate(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("Fattura accompagnatoria")

    def on_nuovo_preventivo_button_clicked(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("Preventivo")

    def on_nuovo_ordine_da_cliente_button_clicked(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("Ordine da cliente")

    def on_nuovo_vendita_al_dettaglio_button_clicked(self, widget):
        if not hasAction(actionID=2):return
        self.nuovoDocumento("Vendita dettaglio")

    def nuovoDocumento(self, kind):
        if not hasAction(actionID=2):return
        from promogest.ui.anagDocumenti.AnagraficaDocumenti import AnagraficaDocumenti
        #from utils import findComboboxRowFromStr
#        self.aziendaStr = Environment.azienda
        anag = AnagraficaDocumenti()
        showAnagrafica(self.main_wind.getTopLevel(), anag)
        anag.on_record_new_activate()
        findComboboxRowFromStr(anag.editElement.id_operazione_combobox, kind, 1)
        anag.editElement.id_persona_giuridica_customcombobox.grab_focus()
        findComboboxRowFromStr(anag.editElement.id_persona_giuridica_customcombobox, "Altro", 1)

    def on_promotux_button_clicked(self, button):
        url ="http://www.promotux.it"
        webbrowser.open_new_tab(url)

    def on_promogest_button_clicked(self, button):
        url ="http://www.promogest.me"
        webbrowser.open_new_tab(url)

    def on_email_button_clicked(self, button):
        sendemail = SendEmail()

def showAnagrafica(window, anag, button=None, mainClass=None):
    anagWindow = anag.getTopLevel()
#    anagWindow.connect("destroy", on_anagrafica_destroyed, [window, button,mainClass])
    #anagWindow.connect("hide", on_anagrafica_destroyed, [window, button,mainClass])
#    anagWindow.set_transient_for(window)
#    setattr(anagWindow, "mainClass",mainClass)
    anagWindow.show_all()
