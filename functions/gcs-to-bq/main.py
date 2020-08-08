import google.cloud
from google.cloud import bigquery
import pandas as pd
import datetime
import time

def gcs_to_bq():

    # Construct a BigQuery client object.
    
    client = bigquery.Client()

    # TODO(developer): Set table_id to the ID of the table to create.
    
    table_id = "bda-kict-2020.dataset_asia_south1.demo"
    
    uri = "gs://bda-input-bucket-asia-south/usa_names.csv"
    
    data = pd.read_csv(uri, header=None)
    
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

