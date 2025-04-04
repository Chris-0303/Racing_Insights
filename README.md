# VDSS: Racing_Insights

Formel1 Projekt, 4. Semester, DS23t
Dieses Readme dient als Dokumentation für unser Projekt.
Dieses Repository war ursprünglich auf github.zhaw.ch abelegt, wurde aber zur einfacheren Verknüpfung mit Streamlit verlegt.

## Inhaltsverzeichnis
1. [App-Link](#app-link)
2. [Contributors](#contributors)   
3. [Dokumentation](#dokumentation)  
4. [Web-App](#web-app)
5. [Dateien](#dateien)  
   1. [Projektkonzept](#Projektkonzept)
   2. [Personas](#Personas)
   3. [Datenbericht](#datenbericht)
   4. [Präsentationsmedien](#präsentationsmedien)
   5. [Skripts](#Skripts)


## App-Link

Die Streamlit-App zum Projekt ist verfügbar unter: https://racing-insights-vdss.streamlit.app/


## Contributors

- Natalie Jakab (jakabnat)  
- Sarruja Sabesan (sabessar)  
- Nelly Mossig (mossinel)  
- Chris Eggenberger (eggench1)  

## Dokumentation

Grundlage unseres Projekts ist das Python-Paket "fastf1", das eine API mit diversen Datenpunkten zu jeder Rennsession der Formel 1 beinhalten und kostenlos zugänglich ist. Die Dokumentation von fastf1 ist verfügbar unter https://docs.fastf1.dev/index.html und wurde von uns während dem Projekt extensiv durchgearbeitet, um die vorhandenen Daten und Möglichkeiten für Insights zu verstehen. 

Aktualität: Rennen sind im Tool ab einem Tag nach dem Rennen verfügbar, sofern das Paket die Daten liefert, was es laut dessen Dokumentation in diesem zeitlichen Rahmen tun sollte.

Farbschema: Zur einheitlichen Visualisierung wird in allen Anwendungen das im Paket inbegriffene Farbschema "fastf1" verwendet.

### Projektplan

->Brauchen wir noch einen Projektplan oder so? einfach simpel was in welchen Wochen etwa gemacht

### Verwendete Python-Pakete

In der Folge werden die im Projekt verwendeten Python-Pakete aufgelistet und erklärt, zu welchem Zweck sie gebraucht wurden
-streamlit (Webapp)
-fastf1 (Datenbeschaffung)
-warnings (Datenexploration)
-pandas (Datenbearbeitung)
-numpy (Datenbearbeitung)
-re (Datenbearbeitung)
-datetime (Datenbearbeitung)
-matplotlib (Datenvisualisierung)
-seaborn (Datenvisualisierung)

## Web-App

Hier erklären wir, wie unsere Web-App funktioniert und was die verschiedenen Anwendungen sind ...

## Dateien

In der Folge werden die zugehörigen Dateien und Skripts zum Projekt aufgeführt. Die alleinstehende Datei requirements.txt gehört zum Streamlit-Ökosystem und dient zur Angabe der benötigten Python-Pakete.

Die Datenerkundung wurde gezielt als Jupyter Notebook (.ipynb) geschrieben, um einzelne Erkundungsschritte aus rückwirkend möglichst einfach einsehen zu können. Die Datenerkundung wurde in der Umgebung DataSpell von JetBrains ausgeführt, das eine tolle Funktionalität bieten, unter anderem mit interaktiven Outputs in der Erkundung.

Die für das Streamlit-Programm verwendeten Skripts mussten dann als .py-Skripts geschrieben werden, damit sie mit der Web-App kompatibel sind.

### Projektkonzept

Das Projektkonzept wurde zu Beginn des Projekts erstellt und liegt ab in GitHub unter /Konzept_DataViz/Konzept_DataViz_Projekt_MossigJakabSabesanEggenberger.pdf

### Personas


### Datenbericht

Template Datenbericht liegt im Moodle

### Präsentationsmedien


### Skripts

Das Skript "helper_functions.py" liegt im Ordner utils (der rein der Strukturierung dient) und dient dazu, einheitliche Funktionen zu schreiben, mit der die API abgerufen und der gesammelte Datensatz bereinigt und prozessiert wird. Es existieren folgende Funktionen:
-load_races: Input: Jahr (User-Input). Ausgabe: Rennkalender dieses Jahres
-load_data: Input: Jahr (User-Input), Rennen (User-Input). Ausgabe: Session des gewünschten Rennens
-data_cleaner: Input: Session. Ausgaben: 
-- driver_info: Dataframe, mit dem dem User die teilnehmenden Fahrer als Auswahl gegeben werden können. Dies muss auf Rennebebe passieren, da nicht in jedem Rennen alle gleichen Fahrer am Start waren.
-- laps: Dataframe mit den Runden des Rennens inklusive benutzerdefinierter Zusatzelemente wie dem Wetter.

Weiter gibt es die Pages. Jede Page beheimatet ein Skript für eine Visualisierung. Innerhalb jeder Page wird zuerst helper_functions aufgerufen und danach das abrufen der User-Inputs sowie die Visualisierung programmiert.
-Positionsverlauf: In der Visualisierung Positionsverlauf wird …
-Rundenzeiten: In der Visualisierung Rundenzeiten wird … 