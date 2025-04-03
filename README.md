
A Batch data pipeline for extracting, processing, and analyzing job market data from JoinRise API and enabling on the fly analysis without querying the data for non-technical and business users.

**WORKFLOW**
<img width="1508" alt="Screenshot 2025-04-03 at 2 12 35 AM" src="https://github.com/user-attachments/assets/eeab5d59-7dcf-41e3-94b4-605da3a9806e" />


💻 Tech Stack
<div align="center">
  <table>
    <tr>
      <th>Component</th>
      <th>Technology</th>
      <th>Purpose</th>
    </tr>
    <tr>
      <td><b>Orchestration</b></td>
      <td>Apache Airflow (GCP Composer)</td>
      <td>Workflow management and scheduling</td>
    </tr>
    <tr>
      <td><b>Storage</b></td>
      <td>Google Cloud Storage (GCS)</td>
      <td>Raw data and Parquet file storage</td>
    </tr>
    <tr>
      <td><b>Processing</b></td>
      <td>Apache Spark (PySpark)</td>
      <td>Large-scale data processing</td>
    </tr>
    <tr>
      <td><b>Transformation</b></td>
      <td>dbt (data build tool)</td>
      <td>SQL transformations and testing</td>
    </tr>
    <tr>
      <td><b>Data Warehouse</b></td>
      <td>Google BigQuery</td>
      <td>Analytics and data serving</td>
    </tr>
    <tr>
      <td><b>Visualization</b></td>
      <td>ThoughtSpot</td>
      <td>Dashboards and reporting</td>
    </tr>
    <tr>
      <td><b>Infrastructure</b></td>
      <td>Google Cloud Platform (GCP)</td>
      <td>Cloud infrastructure</td>
    </tr>
  </table>
</div>


🔍 Overview
This project implements an end-to-end data pipeline that extracts job postings from the JoinRise API, processes and transforms the data using modern data engineering tools, and loads it into BigQuery for analysis and visualization.
The pipeline enables data-driven insights into job market trends, geographic demand, and salary distributions through automated daily updates.
🏗️ Architecture

1️⃣ Data Ingestion (Airflow DAG)
 - Extract job postings daily from the `JoinRise API`
 - Load raw data into `GCS`

2️⃣ Data Processing using `Python`

- apply some transformation dynamically while loading into `BigQuery`
Load raw data from 
Clean, normalize, and preprocess job details
Convert data into Parquet format for efficient querying

3️⃣ Data Transformation `(dbt + BigQuery)`
 - Create Data Models for Business usecases using `DBT`
 - Create Daily snap shots, views, data quality checks and tests using `DBR`
 - 
<img width="1081" alt="Screenshot 2025-04-03 at 2 16 10 AM" src="https://github.com/user-attachments/assets/3f6622fe-2bfd-4473-8bde-12a23f36a611" />


   
Define data models (Staging, Intermediate, Fact & Dimension tables)
Implement testing (dbt tests) and documentation
Optimize queries using partitioning & clustering in BigQuery

4️⃣ Orchestration & Scheduling `(Apache Airflow)`
 - Automate daily job execution
 - Implement DAG dependencies for ingestion, transformation, and reporting
 - Send failure alerts & logging
   
<img width="1685" alt="Screenshot 2025-03-18 at 12 23 15 AM" src="https://github.com/user-attachments/assets/4afb4e85-628b-4a57-969e-27ea6b86c807" />

   

5️⃣ Analytics & Visualization
 - generate reports, serach based analysis and charts using ThoughtSpot
Track job trends, demand by location, and salary distribution just by typing keywords.

<img width="1655" alt="Screenshot 2025-04-03 at 1 45 06 AM" src="https://github.com/user-attachments/assets/70268973-ec49-406b-864c-4bf33011dda0" />



