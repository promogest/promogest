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

from promogest.ui.utils import *
from promogest.dao.Setconf import SetConf
from promogest import Environment
from GladeWidget import GladeWidget


class AnagraficaDocumentiSetup(GladeWidget):
    """ Widget di configurazione del codice installazione e dei parametri
    di configurazione

    [Documenti]
    cliente_predefinito =  # FATTO
    tipo_documento_predefinito = # FATTO
    color_base = #F9FBA7
    ricerca_per = descrizione  #FATTO
    tipo_movimento_predefinito =  #FATTO
    cartella_predefinita = /home/vete/promogest2/AziendaPromo/documenti/  # FATTO
    fornitore_predefinito =  #FATTO
    color_text = black
    """
    def __init__(self, maino):
        GladeWidget.__init__(self, '_anagrafica_documenti_setup_frame',
                                    '_anagrafica_documenti_setup.glade')
#        self.placeWindow(self.getTopLevel())
        self.maino = maino
        self._draw()

    def _draw(self):
        """ Riempiamo le combo """
        fillComboboxOperazioni(self.tipo_documento_predefinito_combo,'documento')
        fillComboboxOperazioni(self.tipo_movimento_predefinito_combo)

    def _refresh(self):
        """
        Carichiamo i dati in interfaccia
        """
        self.multilinea_entry.set_text(str(setconf("Multilinea", "multilinealimite")))
        a = setconf("Documenti", "tipo_documento_predefinito")
        if a and a != "None":
            findComboboxRowFromId(self.tipo_documento_predefinito_combo,a)
        a = setconf("Documenti", "tipo_movimento_predefinito")
        if a and a != "None":
            findComboboxRowFromId(self.tipo_movimento_predefinito_combo,a)
        a = setconf("Documenti", "cliente_predefinito")
        if a and a != "None":
            self.cliente_predefinito_combo.setId(a)
        a = setconf("Documenti", "fornitore_predefinito")
        if a and a != "None":
            self.fornitore_predefinito_combo.setId(a)
        a = setconf("Documenti","ricerca_per")
        if a =="codice":
            self.codice_radio.set_active(True)
        elif a == "codice_a_barre":
            self.codice_a_barre_radio.set_active(True)
        elif a == "descrizione":
            self.descrizione_radio.set_active(True)
        elif a== "codice_articolo_fornitore":
            self.codice_articolo_fornitore_radio.set_active(True)


    def _saveSetup(self):
        """ Salviamo i dati modificati in interfaccia """
        d = SetConf().select(key="multilinealimite", section="Multilinea")
        d[0].value = str(self.multilinea_entry.get_text())
        d[0].tipo = "int"
        Environment.session.add(d[0])

        d = SetConf().select(key="tipo_documento_predefinito", section="Documenti")
        if d:
            d = d[0]
        else:
            d = SetConf()
        d.key = "tipo_documento_predefinito"
        d.section = "Documenti"
        d.tipo = "str"
        d.value = findIdFromCombobox(self.tipo_documento_predefinito_combo)
        d.description = "eventuale tipo documento preferenziale da preimpostare"
        d.tipo_section = "Generico"
        d.active = True
        d.visible = True
        d.date = datetime.datetime.now()
        Environment.session.add(d)

        d = SetConf().select(key="tipo_movimento_predefinito", section="Documenti")
        if d:
            d = d[0]
        else:
            d = SetConf()
        d.key = "tipo_movimento_predefinito"
        d.section = "Documenti"
        d.tipo = "str"
        d.value = findIdFromCombobox(self.tipo_movimento_predefinito_combo)
        d.description = "eventuale tipo movimento preferenziale da preimpostare"
        d.tipo_section = "Generico"
        d.active = True
        d.visible = True
        d.date = datetime.datetime.now()
        Environment.session.add(d)

        d = SetConf().select(key="cliente_predefinito", section="Documenti")
        if d:
            d = d[0]
        else:
            d = SetConf()
        d.key = "cliente_predefinito"
        d.section = "Documenti"
        d.tipo = "int"
        d.value = findIdFromCombobox(self.cliente_predefinito_combo)
        d.description = "eventuale cliente preferenziale da preimpostare"
        d.tipo_section = "Generico"
        d.active = True
        d.visible = True
        d.date = datetime.datetime.now()
        Environment.session.add(d)

        d = SetConf().select(key="fornitore_predefinito", section="Documenti")
        if d:
            d = d[0]
        else:
            d = SetConf()
        d.key = "fornitore_predefinito"
        d.section = "Documenti"
        d.tipo = "int"
        d.value = findIdFromCombobox(self.fornitore_predefinito_combo)
        d.description = "eventuale fornitore preferenziale da preimpostare"
        d.tipo_section = "Generico"
        d.active = True
        d.visible = True
        d.date = datetime.datetime.now()
        Environment.session.add(d)

        d = SetConf().select(key="ricerca_per", section="Documenti")
        if self.codice_radio.get_active():
            d[0].value = "codice"
        elif self.codice_a_barre_radio.get_active():
            d[0].value = "codice_a_barre"
        elif self.descrizione_radio.get_active():
            d[0].value = "descrizione"
        elif self.codice_articolo_fornitore_radio.get_active():
            d[0].value = "codice_articolo_fornitore"
        d[0].tipo = "str"
        Environment.session.add(d[0])
        return
