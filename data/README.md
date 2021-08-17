# Beschreibung Spalten Daten-Export
In diesem Readme werden alle Spalten des Daten-Exports aufgelistet.
- File: export-pt-*.csv enthält Daten-Export als CSV
- File: usage-group-complete-ch.json enthält hierarchische Ordnung der Nutzungen
- File: usages-ch.json enthält Übersetzungen der Nutzungen
- Mit Prefix Ausrufezeichen versehene Spalten sind eher projektrelevant

## Generelle Daten
**!id:** kennwerte interner Identifier\
**!source:** Quelle des Dateninstanz\
**!verification_status:** manuell geprüfter Verifikationsstatus 
- VERIFIED_OK := "Verifiziert und OK",
- VERIFIED_OK_BUT_UNSUITABLE := "Verifiziert aber fehlerhaft",
- PARTIALLY_VERIFIED := "Teilweise verifiziert",
- NOT_VERIFIED := "Nicht verifziert"
    
**!title:** Bezeichnung der Dateninstanz\
**!neubau_umbau:** Typ des Baus (NEUBAU oder UMBAU)\
comment: Kommentar des Datenerfassers resp. Prüfers\
nom_address: Adresse\
nom_zip: PLZ4\
nom_location_name: Ortsname\
nom_country: Land\
nom_economy_region: Grobe Wirtschaftsregion\
nom_competition: Wettbewerbssituation bei Erstellung / Ausschreibung\
nom_contract_assignment: \
index_year: Kostenrelevantes Abrechnungsjahr\
index_month: Kostenrelevanter Abrechnungsmonat\
index_source: Angewandtes Indexierungsverfahren bei Kostenabrechnung\
construction_start: Baujahr\
moving_in: Bezugsjahr\
planzeit: Dauer der Planungsphase in Monaten\
bauzeit: Dauer der Bauzeit in Monaten\
**!nom_usage_main:** Hauptnutzung\
nom_usage_main_readable: Hauptnutzung auf deutsch übersetzt\
**!usages:** Nutzung\
usage_cluster: Grobeinteilung der Nutzung

nom_material: Typ Innere Tragkonstruktion\
**!nom_facade:** Typ Aussenwandkonstruktion und Fassade\
heating_types: Heiztyp\
electrical_types: Elektr. Anlage wie Photovoltaikanlage\
conditioning_types: Klima / Kälte Anlagen\
ventilation_types: Lüftungsanlagen

## Geometrische Daten
area_building: Gebäudegrundfläche GGF\
area_built_up: Bebaute Fläche\
area_surrounded: Umgebungsfläche UF\
area_total: Grundstücksfläche GSF\
area_outer_floor: Aussengeschossfläche AGF\
**!area_total_floor_416:** Geschossfläche GF\
**!area_net_floor_416:** Nettogeschossfläche NGF\
**!area_main_usage:** Hauptnutzfläche HNF\
**!area_usage**: Nutzfläche NF\
**!volume_total_416:** Volumen GV SIA 416\
**!volume_total_116:** Volumen RI SIA 116

ratio_volume_under_terrain: Ratio des Volumens unter Terrain (0 bis 1)\
weak_ratio_volume_under_terrain: Angabe, ob ratio_volume_under_terrain 
- geschätzt ist := 1
- sicher ermittelt ist := 0

ratio_garage: Ratio der Garage gemessen in Geschossfläche GF

roofs: JSON, grobe Angabe, wo sich Dach befindet

compactness_grade: Gebäudehüllzahl A / EBF SIA 380/1\
coverage_divby_area: *veralt* Gebäudehüllzahl\
heating_demand: Heizwärmebedarf QH (spezifisch) kWh/m2 a\
nom_energy: Energie-Zertifizierung

## Lifte
bool_elevators: Angabe, ob Lifte vorhanden\
num_elevators: Anzahl vorhandener Lifte\
bool_elevators_inclined: Angabe, ob Schrägaufzüge vorhanden§\
num_elevators_inclined:  Anzahl vorhandener Schrägaufzüge
..

## Funktionseinheiten
**!num_buildings:** Anzahl Gebäude\
num_appartments: Anzahl Wohnungen\
num_office_spaces: Anzahl Büros\
num_class_rooms: Anzahl Klassenzimmer\
num_parking_spaces_underground: Anzahl unterrirdische Parkplätze

num_floors: Anz. Stockwerke\
**!num_floors_overground:** Anz. oberirdische Stockwerke\
**!num_floors_underground:** Anz. unterirdische Stockwerke

## Kosten
bkp_*: Kosten nach BKP\
**!dyn_expenses_json:** JSON, welches alle Kostenangaben enthält\
**!dyn_cost_ref:** JSON, welches kostenrelevante Bezugsflächen enthält

## Ergänzung
## Diese Features fehlen noch
dyn_floor_list\
area_traffic: Verkehrsfläche VF\
area_functional: Funktionsfläche FF\
area_ancillary: Nebennutzfläche NNF\
area_floor_heated: Geschossfläche beheizt\
area_energy_reference: Energiebezugsfläche AE (EBF)\
heating_demand_MJ: Heizwärmebedarf QH (spezifisch) MJ / m2 a\
heating_demand_effective: Heizwärmebedarf QHeff (effektiv) kWh / m2 a\
heating_demand_effective_MJ: Heizwärmebedarf QHeff (effektiv) MJ / m2 a\
area_thermal_compactness_grade: Therm. Gebäudehülle Ath

