# Solución en Azure Cloud con Delta Lake

* **Ingesta de Datos IoT:**
    * Azure IoT Hub: Ingesta de datos MQTT desde sensores.
    * Azure Event Hubs: Almacenamiento temporal de datos en tiempo real (buffering).
* **Procesamiento de Datos y Orquestación:**
    * Azure Databricks:
        * Structured Streaming para transformaciones de datos en tiempo real y controles de calidad, escribiendo en tablas delta.
        * Workflows para orquestar pipelines de datos.
    * Los jobs de Databricks leerán desde Event Hubs, procesarán los datos y escribirán tablas delta almacenadas en storage account.
* **Almacenamiento de Datos:**
    * Azure Data Lake Storage Gen2 (ADLS Gen2): Almacenamiento en blobs.
* **Catálogo:**
    * Unity Catalog:
        * Gestión centralizada de metadatos.
        * Seguimiento del linaje de datos.
* **Consulta de Datos:**
    * Azure Synapse Analytics Serverless SQL Pools: Consulta de tablas Delta Lake con SQL.
* **Monitorización:**
    * Azure Monitor: Monitorización de pipelines y calidad de datos.
    * Herramientas de monitorización de Databricks.
* **Despliegue:**
    * Plantillas de Azure Resource Manager (ARM): Infraestructura como Código (IaC). O algo como Terraform.
    * Azure DevOps para pipelines de CI/CD.
* **Reporting:**
    * Power BI o alguna otra herramienta. Dashboards y notebooks de datbricks para análisis adhoc. 

## Flujo de Trabajo

1.  IoT Hub ingesta datos de sensores.
2.  Event Hubs almacena temporalmente los datos (buffering).
3.  Procesos spark streaming (para los datos de sensores) o batch (para otros datos complementarios) en databricks.
4.  Unity Catalog para metadatos de tablas delta y fácil gestión centralizada con usuarios.
5.  Azure Monitor o recursos de monitorización de databricks.
6.  Logs ALA y quizás dashboards de status de procesos en Grafana.

## Calidad de Datos

* Controles de calidad de datos en Databricks dentro de los pipelines.
* Seguimiento del linaje de datos en Unity Catalog.

## Usuarios

* Unity Catalog para compartir tablas Delta Lake de forma segura.
* Synapse SQL para consultas fáciles.
