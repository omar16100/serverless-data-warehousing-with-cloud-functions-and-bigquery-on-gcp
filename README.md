# Serverless Data Warehousing Solution With Cloud Functions And Bigquery On GCP

## 

Create a VM instance

Install Python

Install pip

Install Airflow

```Shell
sudo pip3 install apache-airflow
```

```Shell
airflow initdb
```

```Shell
airflow webserver -p 8080
```

```Shell

```


## 

It is recommended that virtualenv be used to keep everything tidy. The [requirements.txt](requirements.txt) describes the dependencies needed for the code used in this repo.

The following high-level steps describe the setup needed to run this example:

1. Create a Cloud Storage (GCS) bucket for receiving input files (*input-gcs-bucket*).

2. Create a GCS bucket for storing processed files (*output-gcs-bucket*).

3. Create a Cloud Composer environment from your terminal or Cloud Shell

```Shell
gcloud composer environments create example-environment --location=asia-south1
```

It takes some time to create.

4. Create a Cloud BigQuery table for the processed output. The following schema is used for this example:

|Column Name|Column Type|
|:-|:-|
|state|STRING|
|gender|STRING|
|year|STRING|
|name|STRING|
|number|STRING|
|created_date|STRING|
|filename|STRING|
|load_dt|DATE|

5. Set the following [Airflow variables](https://airflow.apache.org/docs/stable/concepts.html#variables) needed for this example:

| Key                   | Value                                           |Example                                   |
| :--------------------- |:---------------------------------------------- |:---------------------------              |
| gcp_project           | *your-gcp-project-id*                           |cloud-comp-df-demo                        |
| gcp_temp_location     | *gcs-bucket-for-dataflow-temp-files*            |gs://my-comp-df-demo-temp/tmp             |
| gcs_completion_bucket | *output-gcs-bucket*                             |my-comp-df-demp-output                    |
| input_field_names     | *comma-separated-field-names-for-delimited-file*|state,gender,year,name,number,created_date|
| bq_output_table       | *bigquery-output-table*                         |my_dataset.usa_names                      |
| email                 | *some-email@mycompany.com*                      |some-email@mycompany.com                  |

 The variables can be set as follows:

 `gcloud composer environments run` **_cloud-composer-env-name_** `variables -- --set` **_key val_**

6. Browse to the Cloud Composer widget in Cloud Console and click on the DAG folder icon as shown below:
![Alt text](../img/dag-folder-example.png "Workflow Overview")

7. The DAG folder is essentially a Cloud Storage bucket. Upload the [simple_load_dag.py](simple_load_dag.py) file into the folder:
![Alt text](../img/bucket-example.png "DAG Bucket")
8. Upload the Python Dataflow code [process_delimited.py](dataflow/process_delimited.py) into a *dataflow* folder created in the base DAG folder.
9. Finally follow [these](https://cloud.google.com/composer/docs/how-to/using/triggering-with-gcf) instructions to create a Cloud Function.
    - Ensure that the **DAG_NAME** property is set to _**GcsToBigQueryTriggered**_ i.e. The DAG name defined in [simple_load_dag.py](simple_load_dag.py).

***

## Triggering the workflow

The workflow is automatically triggered by Cloud Function that gets invoked when a new file is uploaded into the *input-gcs-bucket*
For this example workflow, the [usa_names.csv](resources/usa_names.csv) file can be uploaded into the  *input-gcs-bucket*

`gsutil cp resources/usa_names.csv gs://` **_input-gcs-bucket_**

***

## References

* [Cloud Composer Example](https://github.com/GoogleCloudPlatform/professional-services/tree/master/examples/cloud-composer-examples)
* [GCS Bucket To Bigquery Cloud Function](https://github.com/omar16100/gcs-to-bigquery-function)
* [Google Sheets To Bigquery Cloud Function](https://github.com/omar16100/sheets-to-bigquery-cloud-function)
