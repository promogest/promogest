# -*- coding: utf-8 -*-

# Promogest
#
# Copyright (C) 2005-2008 by Promotux Informatica - http://www.promotux.it/
import gtk
from math import sqrt
from GladeWidget import GladeWidget
from promogest import Environment
from utils import *
from utilsCombobox import *
from promogest.dao.TestataDocumento import TestataDocumento
from promogest.dao.TestataMovimento import TestataMovimento
from promogest.dao.RigaDocumento import RigaDocumento
from promogest.dao.ScontoRigaDocumento import ScontoRigaDocumento
from promogest.dao.ScontoTestataDocumento import ScontoTestataDocumento
from promogest.dao.ScontoVenditaDettaglio import ScontoVenditaDettaglio
from promogest.dao.ScontoVenditaIngrosso import ScontoVenditaIngrosso
from promogest.dao.CodiceABarreArticolo import CodiceABarreArticolo
from promogest.dao.Articolo import Articolo
from promogest.dao.Magazzino import Magazzino
from promogest.dao.Operazione import Operazione
from promogest.dao.DaoUtils import giacenzaArticolo

if "PromoWear" in Environment.modulesList:
    from promogest.modules.PromoWear.ui import AnagraficaDocumentiEditPromoWearExt
if "SuMisura" in Environment.modulesList:
    from promogest.modules.SuMisura.ui import AnagraficaDocumentiEditSuMisuraExt
if "GestioneNoleggio" in Environment.modulesList:
    from promogest.modules.GestioneNoleggio.ui import AnagraficaDocumentiEditGestioneNoleggioExt
if "Pagamenti" in Environment.modulesList:
    from promogest.modules.Pagamenti.ui import AnagraficadocumentiPagamentExt

def drawPart(anaedit):

    treeview = anaedit.righe_treeview
    rendererSx = gtk.CellRendererText()
    rendererDx = gtk.CellRendererText()
    rendererDx.set_property('xalign', 1)

    column = gtk.TreeViewColumn('N°', rendererSx, text=0)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)

    column = gtk.TreeViewColumn('Magazzino', rendererSx, text=1)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)

    column = gtk.TreeViewColumn('Codice articolo', rendererSx, text=2)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)

    column = gtk.TreeViewColumn('Descrizione', rendererSx, text=3)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(True)
    treeview.append_column(column)

    column = gtk.TreeViewColumn('% IVA', rendererDx, text=4)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)
    #treeview.set_reorderable(True)
    if "SuMisura" in Environment.modulesList:
        AnagraficaDocumentiEditSuMisuraExt.setTreeview(treeview, rendererSx)

    column = gtk.TreeViewColumn('Multiplo', rendererSx, text=8)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)

    column = gtk.TreeViewColumn('Listino', rendererSx, text=9)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)

    column = gtk.TreeViewColumn('U.M.', rendererSx, text=10)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)

    column = gtk.TreeViewColumn('Quantita''', rendererDx, text=11)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)

    column = gtk.TreeViewColumn('Prezzo lordo', rendererDx, text=12)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)

    column = gtk.TreeViewColumn('Sconti', rendererSx, text=13)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)

    column = gtk.TreeViewColumn('Prezzo netto', rendererDx, text=14)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)

    if "GestioneNoleggio" in Environment.modulesList:
        AnagraficaDocumentiEditGestioneNoleggioExt.setTreeview(treeview, rendererSx)

    column = gtk.TreeViewColumn('Totale', rendererDx, text=16)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(False)
    treeview.append_column(column)
    #treeview.set_reorderable(True)
    fillComboboxOperazioni(anaedit.id_operazione_combobox, 'documento')
    fillComboboxMagazzini(anaedit.id_magazzino_combobox)
    fillComboboxPagamenti(anaedit.id_pagamento_customcombobox.combobox)
    fillComboboxBanche(anaedit.id_banca_customcombobox.combobox)
    fillComboboxAliquoteIva(anaedit.id_aliquota_iva_esenzione_customcombobox.combobox)
    fillComboboxCausaliTrasporto(anaedit.causale_trasporto_comboboxentry)
    fillComboboxAspettoEsterioreBeni(anaedit.aspetto_esteriore_beni_comboboxentry)
    anaedit.id_operazione_combobox.set_wrap_width(Environment.conf.combo_columns)
    anaedit.porto_combobox.set_active(-1)
    anaedit.porto_combobox.set_sensitive(False)

    """ modello righe: magazzino, codice articolo,
    descrizione, percentuale iva, unita base, multiplo, listino,
    quantita, prezzo lordo, sconti, prezzo netto, totale, altezza, larghezza,molt_pezzi
    """
    anaedit.modelRiga = gtk.ListStore(int,str, str, str, str, str, str, str,str, str, str, str, str, str,str, str,str)

    anaedit.righe_treeview.set_model(anaedit.modelRiga)

    anaedit.nuovaRiga()
    # preferenza ricerca articolo ?
    if hasattr(Environment.conf,'Documenti'):
        if hasattr(Environment.conf.Documenti,'ricerca_per'):
            if Environment.conf.Documenti.ricerca_per == 'codice':
                anaedit.ricerca_codice_button.set_active(True)
            elif Environment.conf.Documenti.ricerca_per == 'codice_a_barre':
                anaedit.ricerca_codice_a_barre_button.set_active(True)
            elif Environment.conf.Documenti.ricerca_per == 'descrizione':
                anaedit.ricerca_descrizione_button.set_active(True)
            elif Environment.conf.Documenti.ricerca_per == 'codice_articolo_fornitore':
                anaedit.ricerca_codice_articolo_fornitore_button.set_active(True)

    anaedit.id_operazione_combobox.connect('changed',
            anaedit.on_id_operazione_combobox_changed)
    anaedit.id_persona_giuridica_customcombobox.setSingleValue()
    anaedit.id_persona_giuridica_customcombobox.setOnChangedCall(anaedit.persona_giuridica_changed)
    anaedit.id_magazzino_combobox.connect('changed',
            anaedit.on_id_magazzino_combobox_changed)
    anaedit.id_multiplo_customcombobox.connect('clicked',
            anaedit.on_id_multiplo_customcombobox_button_clicked)
    anaedit.id_multiplo_customcombobox.combobox.connect('changed',
            anaedit.on_id_multiplo_customcombobox_changed)
    anaedit.id_listino_customcombobox.connect('clicked',
            anaedit.on_id_listino_customcombobox_button_clicked)
    anaedit.id_listino_customcombobox.combobox.connect('changed',
            anaedit.on_id_listino_customcombobox_changed)
    anaedit.id_listino_customcombobox.button.connect('toggled',
            anaedit.on_id_listino_customcombobox_button_toggled)
    anaedit.sconti_widget.button.connect('toggled',
            anaedit.on_sconti_widget_button_toggled)
    anaedit.id_destinazione_merce_customcombobox.connect('clicked',
            anaedit.on_id_destinazione_merce_customcombobox_button_clicked)
    idHandler = anaedit.id_vettore_customcombobox.connect('changed',
            on_combobox_vettore_search_clicked)
    anaedit.id_vettore_customcombobox.setChangedHandler(idHandler)
    idHandler = anaedit.id_agente_customcombobox.connect('changed',
            on_combobox_agente_search_clicked)
    anaedit.id_agente_customcombobox.setChangedHandler(idHandler)
    anaedit.sconti_testata_widget.button.connect('toggled',
            anaedit.on_sconti_testata_widget_button_toggled)
    anaedit.id_pagamento_customcombobox.connect('clicked',
            on_id_pagamento_customcombobox_clicked)
    anaedit.id_banca_customcombobox.connect('clicked',
            on_id_banca_customcombobox_clicked)
    anaedit.id_aliquota_iva_esenzione_customcombobox.connect('clicked',
            on_id_aliquota_iva_customcombobox_clicked)
    anaedit.ricerca_codice_button.connect('clicked',
            anaedit.on_ricerca_codice_button_clicked)
    anaedit.ricerca_codice_a_barre_button.connect('clicked',
            anaedit.on_ricerca_codice_a_barre_button_clicked)
    anaedit.ricerca_descrizione_button.connect('clicked',
            anaedit.on_ricerca_descrizione_button_clicked)
    anaedit.ricerca_codice_articolo_fornitore_button.connect('clicked',
            anaedit.on_ricerca_codice_articolo_fornitore_button_clicked)
    if "Pagamenti" in Environment.modulesList:
        AnagraficadocumentiPagamentExt.connectEntryPag(anaedit)

    #Castelletto iva
    rendererText = gtk.CellRendererText()

    column = gtk.TreeViewColumn('Aliquota I.V.A.', rendererText, text=0)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(True)
    anaedit.riepiloghi_iva_treeview.append_column(column)

    rendererText = gtk.CellRendererText()
    rendererText.set_property('xalign', 1)

    column = gtk.TreeViewColumn('Imponibile', rendererText, text=1)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(True)
    anaedit.riepiloghi_iva_treeview.append_column(column)

    column = gtk.TreeViewColumn('Imposta', rendererText, text=2)
    column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
    column.set_clickable(False)
    column.set_resizable(True)
    column.set_expand(True)
    anaedit.riepiloghi_iva_treeview.append_column(column)

    model = gtk.ListStore(str, str, str)
    anaedit.riepiloghi_iva_treeview.set_model(model)

def calcolaTotalePart(anaedit, dao=None):
    """ calcola i totali documento """
    # FIXME: duplicated in TestataDocumenti.py
    totaleImponibile = Decimal(0)
    totaleImposta = Decimal(0)
    totaleNonScontato = Decimal(0)
    totaleImpostaScontata = Decimal(0)
    totaleImponibileScontato = Decimal(0)
    totaleScontato = Decimal(0)

    castellettoIva = {}

    for i in range(1, len(anaedit._righe)):
        prezzoNetto = mN(anaedit._righe[i]["prezzoNetto"])
        quantita = Decimal(anaedit._righe[i]["quantita"])
        moltiplicatore = Decimal(str(anaedit._righe[i]["moltiplicatore"]))
        percentualeIva = Decimal(str(anaedit._righe[i]["percentualeIva"]))

        totaleRiga = mN(prezzoNetto * quantita * moltiplicatore)
        if "GestioneNoleggio" in Environment.modulesList and anaedit.noleggio and str(anaedit._righe[i]["arco_temporale"]) != "NO" :
            arco_temporale = Decimal(anaedit.giorni_label.get_text())
            if str(anaedit._righe[i]["divisore_noleggio"]) == "1":
                totaleRiga = mN(totaleRiga *Decimal(anaedit._righe[i]["arco_temporale"]))
            else:
                totaleRiga= mN(totaleRiga *Decimal(str(sqrt(int(anaedit._righe[i]["arco_temporale"])))))

        percentualeIvaRiga = percentualeIva

        if (anaedit._fonteValore == "vendita_iva" or anaedit._fonteValore == "acquisto_iva"):
            totaleImponibileRiga = mN(calcolaPrezzoIva(totaleRiga, -1 * percentualeIvaRiga)) or 0
        else:
            totaleImponibileRiga = totaleRiga
            totaleRiga = mN(calcolaPrezzoIva(totaleRiga, percentualeIvaRiga))

        totaleImpostaRiga = totaleRiga - mN(totaleImponibileRiga)
        totaleNonScontato += totaleRiga
        totaleImponibile += totaleImponibileRiga
        totaleImposta += totaleImpostaRiga

        if percentualeIvaRiga not in castellettoIva.keys():
            castellettoIva[percentualeIvaRiga] = {'imponibile': totaleImponibileRiga, 'imposta': totaleImpostaRiga, 'totale': totaleRiga}
        else:
            castellettoIva[percentualeIvaRiga]['imponibile'] += totaleImponibileRiga
            castellettoIva[percentualeIvaRiga]['imposta'] += totaleImpostaRiga
            castellettoIva[percentualeIvaRiga]['totale'] += mN(totaleRiga,2)

    totaleNonScontato = mN(totaleNonScontato,2)
    totaleImponibile = mN(totaleImponibile)
    totaleImposta = totaleNonScontato - totaleImponibile
    for percentualeIva in castellettoIva:
        castellettoIva[percentualeIva]['imponibile'] = mN(castellettoIva[percentualeIva]['imponibile'])
        castellettoIva[percentualeIva]['imposta'] = mN(castellettoIva[percentualeIva]['imposta'])
        castellettoIva[percentualeIva]['totale'] = mN(castellettoIva[percentualeIva]['totale'],2)

    totaleImponibileScontato = totaleImponibile
    totaleImpostaScontata = totaleImposta
    totaleScontato = totaleNonScontato
    scontiSuTotale = anaedit.sconti_testata_widget.getSconti()
    applicazioneSconti = anaedit.sconti_testata_widget.getApplicazione()
    if len(scontiSuTotale) > 0:
        for s in scontiSuTotale:
            if s["tipo"] == 'percentuale':
                if applicazioneSconti == 'scalare':
                    totaleScontato = mN(totaleScontato) * (1 - mN(s["valore"]) / 100)
                elif applicazioneSconti == 'non scalare':
                    totaleScontato = mN(totaleScontato) - mN(totaleNonScontato) * mN(s["valore"]) / 100
                else:
                    raise Exception, ('BUG! Tipo di applicazione sconto '
                                        'sconosciuto: %s' % s['tipo'])
            elif s["tipo"] == 'valore':
                totaleScontato = mN(totaleScontato) - mN(s["valore"])

        # riporta l'insieme di sconti ad una percentuale globale
        percentualeScontoGlobale = (1 - totaleScontato / totaleNonScontato) * 100
        totaleImpostaScontata = 0
        totaleImponibileScontato = 0
        totaleScontato = 0
        # riproporzione del totale, dell'imponibile e dell'imposta
        for k in castellettoIva.keys():
            castellettoIva[k]['totale'] = mN(castellettoIva[k]['totale']) * (1 - mN(percentualeScontoGlobale) / 100)
            castellettoIva[k]['imponibile'] = mN(castellettoIva[k]['imponibile']) * (1 - mN(percentualeScontoGlobale) / 100)
            castellettoIva[k]['imposta'] = castellettoIva[k]['totale'] - castellettoIva[k]['imponibile']

            totaleImponibileScontato += mN(castellettoIva[k]['imponibile'])
            totaleImpostaScontata += mN(castellettoIva[k]['imposta'])

        totaleScontato = mN(mN(totaleImponibileScontato) + mN(totaleImpostaScontata),2)

    anaedit.totale_generale_label.set_text(str(totaleNonScontato))
    anaedit.totale_generale_riepiloghi_label.set_text(str(totaleNonScontato))
    anaedit.totale_imponibile_label.set_text(str(totaleImponibile))
    anaedit.totale_imponibile_riepiloghi_label.set_text(str(totaleImponibile))
    anaedit.totale_imposta_label.set_text(str(totaleImposta))
    anaedit.totale_imposta_riepiloghi_label.set_text(str(totaleImposta))
    anaedit.totale_imponibile_scontato_riepiloghi_label.set_text(str(totaleImponibileScontato))
    anaedit.totale_imposta_scontata_riepiloghi_label.set_text(str(totaleImpostaScontata))
    anaedit.totale_scontato_riepiloghi_label.set_text(str(totaleScontato))

    model = anaedit.riepiloghi_iva_treeview.get_model()
    model.clear()
    for k in castellettoIva.keys():
        model.append((mN(k),
                        (mN(castellettoIva[k]['imponibile'])),
                        (mN(castellettoIva[k]['imposta'])),))

def mostraArticoloPart(anaedit, id, art=None):
    """questa funzione viene chiamata da ricerca articolo e si occupa di
        riempire la riga[0] con i dati corretti
    """
    anaedit.articolo_entry.set_text('')
    anaedit.descrizione_entry.set_text('')
    anaedit.codice_articolo_fornitore_entry.set_text('')
    anaedit.percentuale_iva_entry.set_text('0')
    anaedit.id_multiplo_customcombobox.combobox.clear()
    anaedit.id_listino_customcombobox.combobox.clear()
    anaedit.prezzo_lordo_entry.set_text('0')
    anaedit.quantita_entry.set_text('0')
    anaedit.prezzo_netto_label.set_text('0')
    anaedit.sconti_widget.clearValues()
    anaedit.totale_riga_label.set_text('0')

    anaedit._righe[0]["idArticolo"] = None
    anaedit._righe[0]["codiceArticolo"] = ''
    anaedit._righe[0]["descrizione"] = ''
    anaedit._righe[0]["codiceArticoloFornitore"] = ''
    anaedit._righe[0]["percentualeIva"] = 0
    anaedit._righe[0]["idUnitaBase"] = None
    anaedit._righe[0]["idMultiplo"] = None
    anaedit._righe[0]["moltiplicatore"] = 1
    anaedit._righe[0]["idListino"] = None
    anaedit._righe[0]["prezzoLordo"] = 0
    anaedit._righe[0]["quantita"] = 0
    anaedit._righe[0]["prezzoNetto"] = 0
    anaedit._righe[0]["divisore_noleggio"] = 0
    anaedit._righe[0]["sconti"] = []
    anaedit._righe[0]["applicazioneSconti"] = 'scalare'
    anaedit._righe[0]["totale"] = 0
    data = stringToDate(anaedit.data_documento_entry.get_text())

    fillComboboxMultipli(anaedit.id_multiplo_customcombobox.combobox, id, True)

    # articolo c'è 
    if id is not None:
        articolo = leggiArticolo(id)
        if "PromoWear" in Environment.modulesList:
            AnagraficaDocumentiEditPromoWearExt.fillLabelInfo(anaedit, articolo)
        artic = Articolo().getRecord(id=id)
        if articleType(artic) =="father" :
            anaedit.ArticoloPadre = artic
            anaedit.promowear_manager_taglia_colore_togglebutton.set_property("visible", True)
            anaedit.promowear_manager_taglia_colore_togglebutton.set_sensitive(True)
            anaedit.NoRowUsableArticle = True
        if art:
            # articolo proveninente da finestra taglia e colore ...
            anaedit.NoRowUsableArticle = False
            articolo = art
            anaedit._righe[0]["idArticolo"] = id
            anaedit._righe[0]["codiceArticolo"] = articolo["codice"]
            anaedit.articolo_entry.set_text(anaedit._righe[0]["codiceArticolo"])
            anaedit._righe[0]["descrizione"] = articolo["denominazione"]
            anaedit.descrizione_entry.set_text(anaedit._righe[0]["descrizione"])
            anaedit._righe[0]["percentualeIva"] = articolo["percentualeAliquotaIva"]
            anaedit.percentuale_iva_entry.set_text('%-5.2f' % anaedit._righe[0]["percentualeIva"])
            anaedit._righe[0]["idUnitaBase"] = articolo["idUnitaBase"]
            anaedit._righe[0]["unitaBase"] = articolo["unitaBase"]
            anaedit.unitaBaseLabel.set_text(anaedit._righe[0]["unitaBase"])
            if ((anaedit._fonteValore == "acquisto_iva") or  (anaedit._fonteValore == "acquisto_senza_iva")):
                costoLordo = str(articolo['valori']["prezzoLordo"])
                if costoLordo:costoLordo = costoLordo.replace(',','.')
                costoNetto = str(articolo['valori']["prezzoNetto"])
                if costoNetto:costoNetto = costoNetto.replace(',','.')
                if anaedit._fonteValore == "acquisto_iva":
                    costoLordo = calcolaPrezzoIva(costoLordo, anaedit._righe[0]["percentualeIva"])
                    costoNetto = calcolaPrezzoIva(costoNetto, anaedit._righe[0]["percentualeIva"])
                anaedit._righe[0]["prezzoLordo"] = mN(costoLordo)
                anaedit.prezzo_lordo_entry.set_text(str(anaedit._righe[0]["prezzoLordo"]))
                anaedit._righe[0]["prezzoNetto"] = mN(costoNetto)
                anaedit.prezzo_netto_label.set_text(str(anaedit._righe[0]["prezzoNetto"]))
                anaedit._righe[0]["prezzoNettoUltimo"] = float(costoNetto)
                anaedit._righe[0]["sconti"] = articolo['valori']["sconti"]
                anaedit._righe[0]["applicazioneSconti"] = articolo['valori']["applicazioneSconti"]
                anaedit.sconti_widget.setValues(anaedit._righe[0]["sconti"], anaedit._righe[0]["applicazioneSconti"], False)
                anaedit._righe[0]["codiceArticoloFornitore"] = articolo['valori']["codiceArticoloFornitore"]
                anaedit.codice_articolo_fornitore_entry.set_text(anaedit._righe[0]["codiceArticoloFornitore"])
                quantita =articolo["quantita"]
                quantita = quantita.replace(',','.')
                anaedit._righe[0]["quantita"] = quantita
                anaedit.quantita_entry.set_text(anaedit._righe[0]["quantita"])
                if anaedit._righe[0]["quantita"]:
                    anaedit.calcolaTotaleRiga()
            elif ((anaedit._fonteValore == "vendita_iva") or (anaedit._fonteValore == "vendita_senza_iva")):

                costoLordo = str(articolo['valori']["prezzoDettaglio"])
                if costoLordo:
                    costoLordo = costoLordo.replace(',','.')
                anaedit._righe[0]["prezzoLordo"] = mN(costoLordo)
                anaedit.prezzo_lordo_entry.set_text(str(anaedit._righe[0]["prezzoLordo"]))
                anaedit._righe[0]["sconti"] = articolo['valori']["scontiDettaglio"]
                anaedit._righe[0]["applicazioneSconti"] = articolo['valori']["applicazioneScontiDettaglio"]
                anaedit.sconti_widget.setValues(anaedit._righe[0]["sconti"], anaedit._righe[0]["applicazioneSconti"], False)
                quantita =articolo["quantita"]
                quantita = quantita.replace(',','.')
                anaedit._righe[0]["quantita"] = quantita
                anaedit.quantita_entry.set_text(anaedit._righe[0]["quantita"])
                if anaedit._righe[0]["quantita"]:
                    anaedit.calcolaTotaleRiga()
                anaedit.on_show_totali_riga()
                #anaedit.refresh_combobox_listini()
            anaedit.on_confirm_row_button_clicked(anaedit.dialogTopLevel)
            return
        #Eccoci all'articolo normale
        anaedit._righe[0]["idArticolo"] = id
        anaedit._righe[0]["codiceArticolo"] = articolo["codice"]
        anaedit.articolo_entry.set_text(anaedit._righe[0]["codiceArticolo"])
        anaedit._righe[0]["descrizione"] = articolo["denominazione"]
        anaedit.descrizione_entry.set_text(anaedit._righe[0]["descrizione"])
        anaedit._righe[0]["percentualeIva"] = articolo["percentualeAliquotaIva"]
        anaedit.percentuale_iva_entry.set_text('%-5.2f' % anaedit._righe[0]["percentualeIva"])
        anaedit._righe[0]["idUnitaBase"] = articolo["idUnitaBase"]
        anaedit._righe[0]["unitaBase"] = articolo["unitaBase"]
        anaedit.unitaBaseLabel.set_text(anaedit._righe[0]["unitaBase"])
        anaedit._righe[0]["idMultiplo"] = None
        anaedit._righe[0]["moltiplicatore"] = 1

        if "GestioneNoleggio" in Environment.modulesList and anaedit.noleggio:
            anaedit._righe[0]["divisore_noleggio"] = artic.divisore_noleggio
            anaedit.coeficente_noleggio_entry.set_text(str(anaedit._righe[0]["divisore_noleggio"]))
            anaedit.getPrezzoAcquisto()

        anaedit._righe[0]["prezzoLordo"] = 0
        anaedit._righe[0]["prezzoNetto"] = 0
        anaedit._righe[0]["sconti"] = []
        anaedit._righe[0]["applicazioneSconti"] = 'scalare'
        anaedit._righe[0]["codiceArticoloFornitore"] = ''
        #inserisco dei dati nel frame delle informazioni 
        anaedit.giacenza_label.set_text(str(giacenzaArticolo(year=Environment.workingYear,
                                            idMagazzino=findIdFromCombobox(anaedit.id_magazzino_combobox),
                                            idArticolo=anaedit._righe[0]["idArticolo"])))

        anaedit.quantitaMinima_label.set_text(str(artic.quantita_minima))
        # Acquisto 
        if ((anaedit._fonteValore == "acquisto_iva") or  (anaedit._fonteValore == "acquisto_senza_iva")):
            fornitura = leggiFornitura(id, anaedit.id_persona_giuridica_customcombobox.getId(), data)
            costoLordo = fornitura["prezzoLordo"]
            costoNetto = fornitura["prezzoNetto"]
            if anaedit._fonteValore == "acquisto_iva":
                    costoLordo = calcolaPrezzoIva(costoLordo, anaedit._righe[0]["percentualeIva"])
                    costoNetto = calcolaPrezzoIva(costoNetto, anaedit._righe[0]["percentualeIva"])
            anaedit._righe[0]["prezzoLordo"] = mN(costoLordo)
            anaedit.prezzo_lordo_entry.set_text(str(anaedit._righe[0]["prezzoLordo"]))
            anaedit._righe[0]["prezzoNetto"] = mN(costoNetto)
            anaedit.prezzo_netto_label.set_text(str(anaedit._righe[0]["prezzoNetto"]))
            anaedit._righe[0]["prezzoNettoUltimo"] = mN(costoNetto)
            anaedit._righe[0]["sconti"] = fornitura["sconti"]
            anaedit._righe[0]["applicazioneSconti"] = fornitura["applicazioneSconti"]
            anaedit.sconti_widget.setValues(anaedit._righe[0]["sconti"], anaedit._righe[0]["applicazioneSconti"], False)
            anaedit._righe[0]["codiceArticoloFornitore"] = fornitura["codiceArticoloFornitore"]
            anaedit.codice_articolo_fornitore_entry.set_text(anaedit._righe[0]["codiceArticoloFornitore"])
        #vendita
        elif ((anaedit._fonteValore == "vendita_iva") or (anaedit._fonteValore == "vendita_senza_iva")):
            anaedit.refresh_combobox_listini()

    if anaedit._tipoPersonaGiuridica == "cliente":
        anaedit.id_listino_customcombobox.combobox.grab_focus()
    elif anaedit._tipoPersonaGiuridica == "fornitore":
        anaedit.codice_articolo_fornitore_entry.grab_focus()
    else:
        anaedit.descrizione_entry.grab_focus()


def on_multi_line_button_clickedPart(anaedit, widget):
    """ widget per l'inserimento di righe "multiriga" """
    mleditor = GladeWidget('multi_linea_editor', callbacks_proxy=anaedit)
    mleditor.multi_linea_editor.set_modal(modal=True)#
    #mleditor.multi_linea_editor.set_transient_for(self)
    #self.placeWindow(mleditor.multi_linea_editor)
    desc = anaedit.descrizione_entry.get_text()
    textBuffer = mleditor.multi_line_editor_textview.get_buffer()
    textBuffer.set_text(desc)
    mleditor.multi_line_editor_textview.set_buffer(textBuffer)
    mleditor.multi_linea_editor.show_all()
    anaedit.a = 0
    anaedit.b = 0
    def test(widget, event):
        char_count = textBuffer.get_char_count()
        line_count = textBuffer.get_line_count()
        if char_count >= 500:
            on_ok_button_clicked(button)
        if anaedit.b != line_count:
            anaedit.b = line_count
            anaedit.a = -1
        anaedit.a += 1
        colonne = Environment.multilinelimit
        if anaedit.a <= (Environment.multilinelimit-1):
            pass
        else:
            textBuffer.insert_at_cursor("\n")
            anaedit.a = -1
        modified = textBuffer.get_modified()
        textStatusBar = "Tot. Caratteri = %s , Righe = %s, Limite= %s, Colonna=%s" %(char_count,line_count, colonne, anaedit.a)
        context_id =  mleditor.multi_line_editor_statusbar.get_context_id("Multi Editor")
        mleditor.multi_line_editor_statusbar.push(context_id,textStatusBar)

    def on_ok_button_clicked(button):
        text = textBuffer.get_text(textBuffer.get_start_iter(),
                                    textBuffer.get_end_iter())

        anaedit.descrizione_entry.set_text(text)
        vediamo = anaedit.descrizione_entry.get_text()
        mleditor.multi_linea_editor.hide()
    button = mleditor.ok_button
    button.connect("clicked", on_ok_button_clicked)
    mleditor.multi_line_editor_textview.connect("key-press-event", test)

def on_quantita_entry_focus_out_eventPart(anaedit, entry, event):
    """ Funzione di controllo della quantità minima con dialog """
    id = anaedit._righe[0]["idArticolo"]
    if id is not None:
        articolo = Articolo().getRecord(id=id)
    else:
        return
    quantita = float(anaedit.quantita_entry.get_text())
    if articolo:
        try:
            quantita_minima = float(articolo.quantita_minima)
        except:
            quantita_minima = None
    if quantita_minima and quantita < quantita_minima :
        msg = """Attenzione!
La quantità inserita:  %s è inferiore
a %s definita come minima di default.
Inserire comunque?""" % (str(quantita), str(quantita_minima))

        dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                gtk.MESSAGE_INFO, gtk.BUTTONS_OK_CANCEL, msg)
        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_NONE or response == gtk.RESPONSE_CANCEL:
            anaedit.quantita_entry.set_text(str(quantita_minima))
                        #return
        elif response == gtk.RESPONSE_OK:
            anaedit.quantita_entry.set_text(str(quantita))

def hidePromoWear(ui):
    """ Hide and destroy labels and button if promowear is not present """
    ui.promowear_manager_taglia_colore_togglebutton.destroy()
    ui.promowear_manager_taglia_colore_image.hide()
    ui.anno_label.destroy()
    ui.label_anno.destroy()
    ui.stagione_label.destroy()
    ui.label15.destroy()
    ui.colore_label.destroy()
    ui.label14.destroy()
    ui.taglia_label.destroy()
    ui.label_taglia.destroy()
    ui.gruppo_taglia_label.destroy()
    ui.label_gruppo_taglia.destroy()
    ui.tipo_label.destroy()
    ui.label_tipo.destroy()

def hideSuMisura(ui):
    """
    funzione per SuMisura .....rimuove dalla vista quando modulo è disattivato
    """
    ui.sumisura_frame.destroy()
    ui.moltiplicatore_entry.destroy()
    ui.label_moltiplicatore.hide()