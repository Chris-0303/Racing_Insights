# VDSS: Racing_Insights

Formel1 Projekt, 4. Semester, DS23t  
Dieses Readme dient als Dokumentation für unser Projekt.  
Dieses Repository war ursprünglich auf github.zhaw.ch abelegt, wurde aber zur einfacheren Verknüpfung mit Streamlit verlegt.  

## Inhaltsverzeichnis
1. [App-Link](#app-link)
2. [Contributors](#contributors)   
3. [Dokumentation](#dokumentation)
   1. [Projektplan](#projektplan)
   2. [Limitationen](#limitationen)  
   3. [Verwendete Python-Pakete](#verwendete python-pakete)
4. [Web-App](#web-app)
5. [Dateien](#dateien)  
   1. [Projektkonzept](#Projektkonzept)
   2. [Personas](#Personas)
   3. [Datenbericht](#datenbericht)
   4. [Präsentationsmedien](#präsentationsmedien)
   5. [Skripts](#Skripts)
      1. [Helper-Functions](#Helper-Functions)
      2. [Pages](#Pages)


## App-Link

Die Streamlit-App zum Projekt ist verfügbar unter: https://racing-insights-vdss.streamlit.app/


## Contributors

- Natalie Jakab (jakabnat)  
- Sarruja Sabesan (sabessar)  
- Nelly Mossig (mossinel)  
- Chris Eggenberger (eggench1)  

## Dokumentation

Grundlage unseres Projekts ist das Python-Paket "fastf1", das eine API mit diversen Datenpunkten zu jeder Rennsession der Formel 1 beinhalten und kostenlos zugänglich ist. Die Dokumentation von fastf1 ist verfügbar unter https://docs.fastf1.dev/index.html und wurde von uns während dem Projekt extensiv durchgearbeitet, um die vorhandenen Daten und Möglichkeiten für Insights zu verstehen. 

Das Ziel das Projekt ist es, wie ausführlicher im Konzept beschrieben, grafische Auswertungen der Leistung eines Fahrers oder mehrere Fahrer in einem Rennen zur Verfügung zu stellen und damit anhand von Daten Insights zu einem Rennen zu geben. Die Grafiken sollen in einem Stil existieren, wie sie zum Beispiel auf der Webseite eines Motorsportmagazins zu sehen sein könnten. 
Somit besteht unsere Zielgruppe aus Fans des Sports, die zusätzliche Informationen und Analysen zum Rennen, das sie mit grosser Wahrscheinlichkeit bereits gesehen haben, suchen. Somit müssen die Grafiken nicht die komplette Geschichte eines Rennens erzählen, sondern können sich auf spezifische Fahrer oder thematische Schwerpunkte fokussieren, anhand derer die Nutzer die Story des Rennens noch einmal detaillierter entdecken.
Daraus schliesst sich auch, dass Fachbegriffe wie zum Beispiel das Safety Car, VSC (Virtual Safety Car) oder die Reifentypen in den Grafiken erklärt werden müssen.

Aktualität: Rennen sind im Tool ab einem Tag nach dem Rennen verfügbar, sofern das Paket die Daten liefert, was es laut dessen Dokumentation in diesem zeitlichen Rahmen tun sollte.

Farbschema: Zur einheitlichen Visualisierung wird in allen Anwendungen das im Paket inbegriffene Farbschema "fastf1" verwendet.

### Projektplan

->Brauchen wir noch einen Projektplan oder so? einfach simpel was in welchen Wochen etwa gemacht

### Limitationen

Es wurde erkannt, dass das abrufen der API bei jedem Wechsel des Rennens im Input die Nutzung des Tools ziemlich langsam macht. Die vom Projektteam ermittelte Lösung wäre, Daten in einer eigenen Datenbank zwischenzuspeichern und dann die API einfach in regelmässigen Abständen nach neuen Daten zu überprüfen. Da diese Lösung allerdings nicht im Rahmen dieses Projekts liegt, wurde entschieden, diese Lösung hier nicht zu implementieren. 

### Verwendete Python-Pakete

In der Folge werden die im Projekt verwendeten Python-Pakete aufgelistet und erklärt, zu welchem Zweck sie gebraucht wurden  
- streamlit (Webapp)  
- fastf1 (Datenbeschaffung)  
- warnings (Datenexploration)  
- pandas (Datenbearbeitung)  
- numpy (Datenbearbeitung)  
- re (Datenbearbeitung)  
- datetime (Datenbearbeitung)  
- matplotlib (Datenvisualisierung)  
- seaborn (Datenvisualisierung)  

## Web-App

Die Web-App wird via Streamlit gehostet und zieht sich den auszuführenden Code automatisch vom GitHub-Repository. Dank der Implementierung mit Streamlit ist unser Tool auch auf Mobilgeräten problemlos nutzbar.

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

#### Helper-Functions
Das Skript "helper_functions.py" liegt im Ordner utils (der rein der Strukturierung dient) und dient dazu, einheitliche Funktionen zu schreiben, mit der die API abgerufen und der gesammelte Datensatz bereinigt und prozessiert wird. Es existieren folgende Funktionen:  
- _**load_races:**_ Input: Jahr (User-Input). Ausgabe: Rennkalender dieses Jahres  
- _**load_data:**_ Input: Jahr (User-Input), Rennen (User-Input). Ausgabe: Session des gewünschten Rennens  
- _**data_cleaner:**_ Input: Session. Ausgaben:  
- _**driver_info:**_ Dataframe, mit dem dem User die teilnehmenden Fahrer als Auswahl gegeben werden können. Dies muss auf Rennebebe passieren, da nicht in jedem Rennen alle gleichen Fahrer am Start waren.  
- _**laps:**_ Dataframe mit den Runden des Rennens inklusive benutzerdefinierter Zusatzelemente wie dem Wetter.  

#### Pages 

Weiter gibt es die Pages. Jede Page beheimatet ein Skript für eine Visualisierung. Innerhalb jeder Page wird zuerst helper_functions aufgerufen und danach das abrufen der User-Inputs sowie die Visualisierung programmiert.  
- _**Geschwindigkeit:**_ TEXT
- _**Positionsverlauf:**_ In der Visualisierung Positionsverlauf wird der Verlauf des Rennens anhand der Positionen aller Fahrer nach Runde dargestellt.  
- _**Punkte:**_ In der Visualisierung Punkte wird der Punkteverlauf der Rennen über die gesamte gewählte Season dargestellt.  
- _**Rundenzeiten:**_ In der Visualisierung Rundenzeiten können die Nutzer bis zu vier Fahrer wählen, deren Rennverlauf sie anhand ihrer einzelnen Runden darstellen wollen. Neben der Entwicklung der Rundenzeiten bieten auch Elemente wie die Darstellung von Regen, Safety-Car-Phasen, Boxenstopps sowie genutzten Reifentypen Einblick in die Unterschiede der Rennstrategien verschiedener Fahrer.  
