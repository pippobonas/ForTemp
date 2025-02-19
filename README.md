# ForTemp 🌍🔥

## Indice 📌
1. [Descrizione](#1-descrizione-)
2. [Tecnologie Utilizzate](#2-tecnologie-utilizzate-)
3. [Architettura del Progetto](#3-architettura-del-progetto-)
4. [Installazione](#4-installazione-)
5. [Utilizzo](#5-utilizzo-)
6. [Licenza](#6-licenza-)
7. [To do](#7-to-do)
8. [Credits](#8-credits)
9. [Docs](#9-docs)

## 1. Descrizione 📝

ForTemp è un progetto che sfrutta tecnologie distribuite per il monitoraggio dei dati meteorologici e per la previsione a breve termine (1h) della temperatura a bassa quota (2m).  
I dati provengono da dataset eterogenei che forniscono metriche diverse:  
- Da ERA5 Single Level si ottengono, ad esempio, medie satellitari su una griglia con risoluzione di circa 32 km.  
- Tramite l'API Current Weather di OpenWeather è possibile accedere a dati puntuali provenienti da varie stazioni.
L'interpolazione dei dati permette di creare un modello che, nella modalità batch, sfrutta i dati storici di ERA5 Single Level, mentre per l'analisi in tempo reale impiega i valori offerti da OpenWeather per prevedere la temperatura a bassa quota.  
Il modello, pur essendo stato addestrato su dati medi storici e testato con misurazioni in tempo reale, riesce a generare previsioni puntuali. Tuttavia, per ottimizzarne le stime e verificarne l'efficacia nell'approccio ibrido, sono necessarie ulteriori analisi e sperimentazioni.
ForTemp offre due modalità d'uso:  
1. Utilizzo immediato tramite un modello preaddestrato basato sui dati storici di ERA5 Single Level.  
2. Modalità (beta) per addestrare un modello personalizzato in base al proprio bound di coordinate, utilizzando sempre i dati di ERA5 Single Level.  

Indipendentemente dalla modalità scelta, il modello richiede una fase di warm-up (circa 4 ore) prima di iniziare a generare previsioni in tempo reale.

## 2. Tecnologie Utilizzate 🚀

- **OpenWeather API** - Per ottenere dati meteo in tempo reale. ☁️
- **ECMWF CDS API** - Per recuperare dati meteorologici storici e di previsione. 🌦️
- **ecCodes** - Libreria per la gestione dei dati in formato GRIB e BUFR. 📜
- **Pandas** - Per la manipolazione e l'analisi dei dati. 🐼
- **Docker & Docker Compose** - Per la containerizzazione e gestione dei servizi. 🐳
- **Kafka & Kafka Streams** - Per lo streaming e l'elaborazione in tempo reale. 📡
- **Logstash, Kibana & Elasticsearch** - Per l'aggregazione, il monitoraggio e la visualizzazione dei dati. 📊🔍
- **Spark & Spark Structured Streaming** - Per l'elaborazione scalabile dei dati in tempo reale. ⚡🔥
- **Crond** - Per la pianificazione delle attività ricorrenti. ⏲️

## 3. Architettura del Progetto 🏗️

0. **(Opzionale) Training del modello**:
    - Raccolta dati da CDS API 🌦️
    - Esecuzione Script di conversione da grib a csv 📜
    - Training del modello di machine learning in regressione lineare 🤖

1. **Raccolta Dati & Ingestion**:
    - OpenWeather API 🌎
    - Script python per l'acquisizione dei dati 🐍
    - Ricezione dati ad Logstash 📥

2. **Streaming & Micro-batch**:
   - Logstash invia dati a Kafka 📡
   - Kafka Streams aggrega i dati e li trasforma in un formato strutturato tramite un worm up sui dati 🔄
   - Spark Structured Streaming esegue analisi sul modello pre-addestrato in tempo reale ⚡

3. **Storage & Visualizzazione**:
   - Logstash processa i dati da Kafka e li invia a Elasticsearch 📦
   - Kibana permette la visualizzazione e il monitoraggio interattivo dei dati 📊

## 4. Installazione ⚙️

### 4.1 Prerequisiti 🛠️

- Docker e Docker Compose installati 🐳
- API Key per OpenWeather e (opzionale) ECMWF CDS API 🔑
- Python 

### 4.2 Setup con modello pre addestrato🏗️
La guida è prettamente per gli utenti Linux e macOS. Per Windows, cercare guide online. 🖥️

1. Clonare il repository: 🖥️

2. Modificare il file "acquisition.env" come da template per ottenere i dati da OpenWeather: 🔒

3. Aggiungere al sistema le città da monitorare: 🌍
   - Spostarsi nella cartella del progetto: `/data_acquisition/data_acquisition_stream`
   - (Opzionale ma consigliato) creare un ambiente virtuale Python 🐍
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   - Installare nel proprio ambiente i requirements 📦
   ```bash
   pip install -r requirements.txt 
   ```
   - Seguire le istruzioni nel terminale 🖥️

4. Build delle immagini 🛠️
   ```bash
   docker-compose build
   ```

5. Primo avvio per mappare gli indici su Elasticsearch: 🚀
   ```bash
   docker-compose --profile setup up -d
   ```

6. Avvio Docker 🐳
   ```bash
   docker-compose up -d
   ```

### 4.3(Opzionale) Training del modello |beta|
Se si desidera un modello elaborato da elementi più pertinenti al proprio bound di città monitorate è possibile:
0. Registrarsi su ECMWF CDS: [https://cds.climate.copernicus.eu/how-to-api](https://cds.climate.copernicus.eu/how-to-api) 🌐

1. Download grib dataset da ERA5 single level e pressure level:
   - Scrivendosi i JSON delle richieste ed in seguito utilizzando script Python per il download del dataset da ECMWF CDS:
      - Spostarsi nella cartella `/data_acquisition/data_acquisition_batch` 📂
      - Modificare il file `.cdsapirc` e copiarlo nella propria home 🏠
      - (Opzionale ma consigliato) creare un ambiente virtuale Python 🐍
         ```bash
         python3 -m venv venv
         source venv/bin/activate
         ```
      - Installare nel proprio ambiente i requirements 📦
         ```bash
         pip install -r requirements.txt 
         ```
      - Eseguire per scaricare i dati:
         ```bash
         python main.py download data/grib data/request
         ```
   - Oppure tramite web interface all'indirizzo: [https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download) 🌐
      - Selezionare le seguenti variabili meteorologiche:
         - `"10m_u_component_of_wind", "10m_v_component_of_wind", "2m_temperature", "mean_sea_level_pressure", "surface_pressure", "surface_solar_radiation_downwards", "total_cloud_cover"`
         - `!!WARN!!` Selezionare tutte le ore e mesi contigui altrimenti la finestrazione sarà logicamente inconsistente ⚠️
         - Selezionare il bound di coordinate desiderato 🌍
      - Copiare/spostare i dati .grib all'interno della directory `/data_acquisition/data_acquisition_batch/data` 📂

2. Convertire i dati da grib in csv:
   - Spostarsi nella cartella `/data_acquisition/data_acquisition_batch` 📂
   - (Se non lo si è fatto in precedenza)
      - (Opzionale ma consigliato) creare un ambiente virtuale Python 🐍
         ```bash
         python3 -m venv venv
         source venv/bin/activate
         ```
      - Installare nel proprio ambiente i requirements 📦
         ```bash
          pip install -r requirements.txt 
          ```
         - Eseguire per convertire i dati: 🔄
            ```bash
            python main.py output.csv . data/grib
            ```
         - Eseguire compose per elaborare il modello: 🐳
            ```bash
            docker-compose up trainer
            ```

## 5. Utilizzo 🎯
- **AVVIO**: 
   ```bash
      docker-compose up trainer
   ```
- **Monitorare l'elaborazione**: Accedere a spark su `http://localhost:4040`
- **Monitorare i dati**: Accedere a Kibana su `http://localhost:5601`. 📊
- **Visualizzare i dati in Elasticsearch**: 🔎
  ```bash
  curl -X GET "localhost:9200/_search?pretty"
  ```

## 6. Licenza 📜

Distribuito sotto la licenza MIT. Vedi `LICENSE` per i dettagli. 🏛️


## 7. To do 📝
- Automatizzare un processo di download da ECMWF e training per ottenere sempre un modello che utilizza dati storici più recenti ⏳
- Utilizzare un modello più performante 🚀
- Aggiungere al monitoraggio variabili come: "total precipitation" da ERA5 single level, "relative pressure" da ERA5 pressure level. Quest'ultima in base alla pressione hPa derivante anche dall'altitudine 🌧️📈
- Migliorare l'orchestrazione dei container tramite k8s

## 8. Credits 🙏

The model of linear regression is generated using Copernicus Climate Change Service information 2020-2024 . Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains.

Citing the data:

Hersbach, H., Bell, B., Berrisford, P., Biavati, G., Horányi, A., Muñoz Sabater, J., Nicolas, J., Peubey, C., Radu, R., Rozum, I., Schepers, D., Simmons, A., Soci, C., Dee, D., Thépaut, J-N. (2023): ERA5 hourly data on single levels from 1940 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS), DOI: 10.24381/cds.adbb2d47 (Accessed on 17-2-2025)

Citing the web catalogue entry:

Copernicus Climate Change Service, Climate Data Store, (2023): ERA5 hourly data on single levels from 1940 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS), DOI: 10.24381/cds.adbb2d47 (Accessed on 17-2-2025)

## 9. Docs 📚

- OpenWeather API Current Weather https://openweathermap.org/current
- Openweather API GeoCoding https://openweathermap.org/current#geocoding
- OpenElevation API Docs https://open-elevation.com/
- CDS API https://cds.climate.copernicus.eu/how-to-api
- EcCodes https://confluence.ecmwf.int/display/ECC/documentation
- Pandas :https://pandas.pydata.org/docs/
- Docker https://docs.docker.com/
- Docker compose https://docs.docker.com/compose/
- Kafka https://kafka.apache.org/documentation/
- Kafka Stream https://kafka.apache.org/documentation/streams/
- Spark https://archive.apache.org/dist/spark/docs/3.4.4/
- Spark sstructured streaming https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
- PySpark https://spark.apache.org/docs/latest/api/python/index.html
- Crond https://www.linux.org/docs/man8/cron.html
- Logstash https://www.elastic.co/guide/en/logstash/current/index.html
- Elasticksearch https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- Kibana https://www.elastic.co/guide/en/kibana/current/index.html









