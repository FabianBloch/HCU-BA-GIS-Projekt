-- Straßenbaumkataster
SELECT * FROM grp1.strassenbaumkataster_original LIMIT 100;

-- Löschen der Tabelle
DROP TABLE IF EXISTS grp1.strassenbaumkataster;

-- Einfügen der Daten in neue Tabelle
SELECT
baumid,
baumnummer,
sorte_latein,
pflanzjahr,
kronendurchmesser,
stammumfang,
strasse,
hausnummer,
ortsteil_nr,
geom
INTO grp1.strassenbaumkataster
FROM grp1.strassenbaumkataster_original;

-- 'baumid' wird zum PK
ALTER TABLE grp1.strassenbaumkataster
ADD CONSTRAINT baumpk PRIMARY KEY (baumid);

SELECT * FROM grp1.strassenbaumkataster LIMIT 100;

-- Wie viele und welche Datensätze würde eine neue Tabelle beinhalten?
SELECT DISTINCT sorte_latein, sorte_deutsch,
				art_latein, art_deutsch,
				gattung_latein, gattung_deutsch
FROM grp1.strassenbaumkataster_original;

DROP TABLE IF EXISTS grp1.sorte;

-- Tabelle 'sorte' erzeugen
CREATE TABLE grp1.sorte (
			id SERIAL PRIMARY KEY,
			sorte_latein VARCHAR,
			sorte_deutsch VARCHAR,
			art_latein VARCHAR,
			art_deutsch VARCHAR,
			gattung_latein VARCHAR,
			gattung_deutsch VARCHAR
);

-- Tabelle 'sorte' mit einer Unterabfrage befüllen.
INSERT INTO grp1.sorte (sorte_latein, sorte_deutsch,
						art_latein, art_deutsch,
						gattung_latein, gattung_deutsch)
							
SELECT DISTINCT sorte_latein, sorte_deutsch,
				art_latein, art_deutsch,
				gattung_latein, gattung_deutsch
				
FROM grp1.strassenbaumkataster_original
WHERE sorte_latein IS NOT null;

SELECT * FROM grp1.sorte;

-- In 'strassenbaumkataster' wird 'sorte_latein' mit der
-- 'id' (PK) aus 'sorte' ersetzt.
WITH subquery AS (
	SELECT id, sorte_latein FROM grp1.sorte
)
UPDATE grp1.strassenbaumkataster
SET sorte_latein = subquery.id::text
FROM subquery
WHERE grp1.strassenbaumkataster.sorte_latein = subquery.sorte_latein;

-- Die Spalte 'sorte_latein' wird in 'sorte_nr' geändert.
ALTER TABLE grp1.strassenbaumkataster
RENAME COLUMN sorte_latein TO sorte_nr;

-- Der Datentyp von 'sorte_nr' wird in INTEGER geändert.
ALTER TABLE grp1.strassenbaumkataster
ALTER COLUMN sorte_nr TYPE INTEGER USING sorte_nr::integer;

