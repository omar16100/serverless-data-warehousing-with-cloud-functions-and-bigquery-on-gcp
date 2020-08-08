import google.cloud
from google.cloud import bigquery

def gcs_to_bq():

    # Construct a BigQuery client object.
    
    client = bigquery.Client()

    # TODO(developer): Set table_id to the ID of the table to create.
    
    table_id = "bda-kict-2020.bda-kict-2020.your_table_name.bda_project_table_function"

    uri = "gs://bda-input-bucket-asia-south/usa_names.csv"

    # Make an API request.

    load_job = client.load_table_from_uri(
        uri, table_id) 

    load_job.result()  # Wait for the job to complete.

    table = client.get_table(table_id)
    print("Loaded {} rows to table {}".format(table.num_rows, table_id))

