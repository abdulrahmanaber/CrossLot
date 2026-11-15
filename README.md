\# CrossLot

\### Cross-Source Vehicle Price Resolution Pipeline



CrossLot is a Data Engineering project that processes used vehicle listings, enriches vehicle information using VIN decoding and fuzzy matching, and loads the results into a SQL Server Data Warehouse for analytics.



\## Project Overview



The project aims to improve the quality and consistency of vehicle listing data by combining data cleaning, standardization, vehicle identification, and data warehouse development.



\## Technologies Used



\- \*\*Python\*\* – Data processing and pipeline development

\- \*\*Pandas\*\* – Data cleaning and transformation

\- \*\*RapidFuzz\*\* – Fuzzy matching

\- \*\*NHTSA API\*\* – VIN decoding and vehicle information enrichment

\- \*\*SQL Server\*\* – Data warehouse storage

\- \*\*Apache Airflow\*\* – Pipeline orchestration

\- \*\*SQL\*\* – Data modeling and analytical queries



\## Data Pipeline



1\. \*\*Data Extraction:\*\* Load the source vehicle listings dataset.

2\. \*\*Data Cleaning:\*\* Handle missing values, duplicates, and inconsistent formats.

3\. \*\*Data Standardization:\*\* Normalize vehicle information.

4\. \*\*VIN Decoding:\*\* Enrich vehicle attributes using the NHTSA API.

5\. \*\*Fuzzy Matching:\*\* Resolve additional vehicle information using similarity matching.

6\. \*\*Data Warehouse Loading:\*\* Load data into SQL Server using a Star Schema.

7\. \*\*Data Validation:\*\* Check data quality and warehouse readiness.

8\. \*\*Orchestration:\*\* Manage pipeline tasks using Apache Airflow.



\## Data Warehouse Design



The project uses a Star Schema with the following tables:



\### Fact Table

\- `FactVehicleListings`



\### Dimension Tables

\- `DimVehicle`

\- `DimLocation`

\- `DimDate`

\- `DimCondition`

\- `DimSeller`



\## Data Quality Results



The processed dataset contains 10,000 vehicle listings.



\- Duplicate listing IDs: 0

\- Missing required values: 0

\- Vehicle information enriched through VIN decoding and fuzzy matching.

\- Unresolved and uncertain matches are retained for review rather than treated as confirmed matches.



\## Analytical Views



The warehouse includes SQL views for:



\- Average vehicle price

\- Average price by state

\- Monthly vehicle price trends

\- Average price by vehicle condition



\## Airflow Orchestration



The Airflow DAG `crosslot\_pipeline` includes the following tasks:



\- `check\_project\_files`

\- `validate\_dataset`

\- `check\_warehouse`

\- `pipeline\_ready`



\## Project Structure



```text

CrossLot/

│

├── dags/

│   └── crosslot\_pipeline.py

│

├── src/

│   ├── extract\_data.py

│   ├── clean\_data.py

│   ├── standardize\_data.py

│   ├── fuzzy\_matching.py

│   ├── load\_dim\_vehicle.py

│   └── load\_fact\_vehicle\_listings.py

│

├── data/

│   ├── raw/

│   └── processed/

│

├── .gitignore

└── README.md

```



\## Future Improvements



\- Add automated monitoring and failure notifications.

\- Improve fuzzy matching review workflows.

\- Expand analytical dashboards.

\- Add incremental warehouse loading.



