--
-- Copyright (C) 2005 by Promotux Informatica - http://www.promotux.it/
-- Author: Andrea Argiolas <andrea@promotux.it>
--
-- This program is free software; you can redistribute it and/or
-- modify it under the terms of the GNU General Public License
-- as published by the Free Software Foundation; either version 2
-- of the License, or (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program; if not, write to the Free Software
-- Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

/*

genere_abbigliamento - Tabella generi abbigliamento

*/


DROP TABLE promogest.genere_abbigliamento;

DROP SEQUENCE promogest.genere_abbigliamento_id_seq;
CREATE SEQUENCE promogest.genere_abbigliamento_id_seq;

CREATE TABLE promogest.genere_abbigliamento (
     id                 bigint          DEFAULT NEXTVAL('promogest.genere_abbigliamento_id_seq') PRIMARY KEY NOT NULL
    ,denominazione      varchar(50)     NOT NULL       
    
    ,UNIQUE ( denominazione )
);

INSERT INTO promogest.genere_abbigliamento ( denominazione ) VALUES ('Unisex');
INSERT INTO promogest.genere_abbigliamento ( denominazione ) VALUES ('Uomo');
INSERT INTO promogest.genere_abbigliamento ( denominazione ) VALUES ('Donna');
