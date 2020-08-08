# Serverless Data Warehousing Solution With Cloud Functions And Bigquery On GCP

`Work In Progress`

## Introduction 

Traditionally data warehousing systems were built to save compute power and cost. Starting from the source to the sink, data would be aggregated and will become multiple times smaller. This is due to the limitation of compute power as well.

As with time, with **big data processing** becoming more common practive among all sizes of businesses and increase in compute power, the traditional way of doing things have changed.

We will be working with Bigquery which is built upon the open source project Apache Drill. Originally Apache Drill is based on the Google Dremel.

**Apache Dremel** is schema-free SQL query engine for Hadoop, NoSQL and cloud storage systems.

Meanswhile **BigQuery** is a fully-managed, serverless data warehouse that enables scalable analysis over petabytes of data. It is a serverless Software as a Service that supports querying using ANSI SQL. It also has built-in machine learning capabilities. [1](#references)

So, unlike before Petabytes of data can be calculated or processed within seconds allowing all kinds operations from aggregation to other scenerios.

But, we have to get the data to Bigquery first to take advantage of the capabilitites.

Here comes Apache Airflow, which is th regular choice for running Extract Tranform Load (ETL) steps.

**Apache Airflow** is platform created by the community to programmatically author, schedule and monitor workflows.

Apache Airflow is an open-source workflow management platform. It started at Airbnb in October 2014 as a solution to manage the company's increasingly complex workflows. Creating Airflow allowed Airbnb to programmatically author and schedule their workflows and monitor them via the built-in Airflow user interface.[2](#references)

It requires virtual machine instances and database to operate.

Google Cloud Platform has a managed service which makes it much simpler to use which is Cloud Composer.

**Cloud Composer** is a fully managed workflow orchestration service built on Apache Airflow.

But there simpler ways to achieve the **ETL** steps.

Introducing **Cloud Functions**. It is scalable pay as you go Functions-as-a-Service (FaaS) to run your code with zero server management.

- No servers to provision, manage, or upgrade

- Automatically scale based on the load

- Integrated monitoring, logging, and debugging capability

- Built-in security at role and per function level based on the principle of least privilege

- Key networking capabilities for hybrid and multi-cloud scenarios

It is much better use functions instead of Apache Airflow for certain ETL use cases and this article will show how.

### Comparison Table

|Apache Airflow|Cloud Function|
|:-|:-|
|More Expensive|Cheaper |
|Requires Servers|Pay To The Upper 100ms Executed|
|High Learning Curve|Easy Of Use|
|Requires More Administration|Requires Less Administration |

## With Cloud Composer (Managed Apache Airflow)

We will be using Cloud Composer for the ETL steps here.

And the next steps will show how to achieve such.

It is recommended that virtualenv be used to keep everything tidy in the local environmeny. The [requirements.txt](requirements.txt) describes the dependencies needed for the code used in this repo.

The following high-level steps describe the setup needed to run this example:

1. Create a Cloud Storage (GCS) bucket for receiving input files (*input-gcs-bucket*), for storing processed files (*output-gcs-bucket*) and storing temporary files (*temp-gcs-bucket*).

2. Create a Cloud Composer environment from your terminal or Cloud Shell

```Shell
gcloud composer environments create example-environment --location=asia-south1
```

It takes some time to create. Make sure you have the right quota limit of CPUs.

4. Create a Cloud BigQuery table from the console for the processed output. The following schema is used for this example:

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

 The variables can be set from the terminal as follows as follows:

 `gcloud composer environments run` **_cloud-composer-env-name_** `variables -- --set` **_key val_**

 Example :

 ```Shell
gcloud composer environments run project-name --location asia-northeast1 variables -- --set email johndoe@example.com
 ```

From the Airflow GUI, you can create them in Admin -> Variables

6. Browse to the Cloud Composer widget in Cloud Console and click on the DAG folder icon as shown below:
![Alt text](/img/dag-folder-example.png "Workflow Overview")

7. The DAG folder is essentially a Cloud Storage bucket. Upload the [simple_load_dag.py](simple_load_dag.py) file into the folder:
![Alt text](img/bucket-example.png "DAG Bucket")

8. Upload the Python Dataflow code [process_delimited.py](dataflow/process_delimited.py) into a *dataflow* folder created in the base DAG folder.

9. Finally follow these instructions to create a Cloud Function :

- To authenticate to IAP, grant the Appspot Service Account (used by Cloud Functions) the Service Account Token Creator role on itself

```Shell
gcloud iam service-accounts add-iam-policy-binding \
your-project-id@appspot.gserviceaccount.com \
--member=serviceAccount:your-project-id@appspot.gserviceaccount.com \
--role=roles/iam.serviceAccountTokenCreator
```

- Get the client ID by running the `get_client_id.py` which can be found [here](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/composer/rest/get_client_id.py)

```Shell
python3 get_client_id.py <your-project-id> <your-composer-location> <your-composer-environment>
```

- Ensure that the **DAG_NAME** property is set to _**GcsToBigQueryTriggered**_ i.e. The DAG name defined in [simple_load_dag.py](simple_load_dag.py)

***

### Triggering The Workflow

The workflow is automatically triggered by Cloud Function that gets invoked when a new file is uploaded into the *input-gcs-bucket*
For this example workflow, the [usa_names.csv](resources/usa_names.csv) file can be uploaded into the  *input-gcs-bucket*

```Shell
gsutil cp resources/usa_names.csv gs:// _input-gcs-bucket_
```

***

## With Cloud Functions

Here, we will do the ETL steps with Cloud Functions.

Function :

```Shell
import google.cloud
from google.cloud import bigquery
import pandas as pd
#import datetime
#import time

def gcs_to_bq():

    # Construct a BigQuery client object.
    
    client = bigquery.Client()

    # TODO(developer): Set table_id to the ID of the table to create.
    
    table_id = "bda-kict-2020.dataset_asia_south1.demo"
    
    uri = "gs://bda-input-bucket-asia-south/usa_names.csv"
    
    data = pd.read_csv(uri, header=None)
    
    # Preprocessing steps

    # Add columns 
    
    #data[['day', 'month', 'year']] = data[5].str.split('/', expand=True)
    #data[['day', 'month', 'year']].astype('int')
    
    #data['filename']=uri
    
    job_config = bigquery.LoadJobConfig(schema=[
        bigquery.SchemaField("state", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("gender", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("year", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("name", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("number", bigquery.enums.SqlTypeNames.STRING),
        bigquery.SchemaField("created_date", bigquery.enums.SqlTypeNames.STRING),
        #bigquery.SchemaField("filename", bigquery.enums.SqlTypeNames.STRING)
        #bigquery.SchemaField("load_dt", bigquery.enums.SqlTypeNames.DATETIME),
    ],write_disposition="WRITE_TRUNCATE")

    # Make an API request.

    load_job = client.load_table_from_uri(
        uri, table_id, job_config = job_config)
    
    # Wait for the job to complete.
    
    load_job.result()

    table = client.get_table(table_id)
    print("Loaded {} rows to table {}".format(table.num_rows, table_id))
```

Deploy the function :

```Shell
gcloud functions deploy gcs-to-bq --region=asia-south1 --entry-point=gcs_to_bq --runtime=python37 --trigger-bucket=input-bucket --source=functions/gcs-to-bq/
```

This function will get the `usa_names.csv` and send them to Bigquery. That's it.

In the terminal above, you can see `--trigger-bucket` parameter. This tells the function to be triggered when new files are added, in this case `usa_names.csv`

## Caveats

- Cloud Functions can only be triggered by Cloud Storage buckets in the same Google Cloud Platform project. Same for Bigquery table.

## Debugging Notes

- Make sure you are in the right location supported by Cloud Composer
- The number of CPU quota should be satisfied

## References

- [Bigquery](https://en.wikipedia.org/wiki/BigQuery)
- [Apache Airflow](https://en.wikipedia.org/wiki/Apache_Airflow)
- [Cloud Composer Example](https://github.com/GoogleCloudPlatform/professional-services/tree/master/examples/cloud-composer-examples)
- [GCS Bucket To Bigquery Cloud Function](https://github.com/omar16100/gcs-to-bigquery-function)
- [Google Sheets To Bigquery Cloud Function](https://github.com/omar16100/sheets-to-bigquery-cloud-function)
- [GCS Triggered Cloud Functions](https://zaxrosenberg.com/gcs-triggered-google-cloud-functions/)
