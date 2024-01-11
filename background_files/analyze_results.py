import parameters
from google.cloud import storage
from google.cloud import aiplatform
from pandas import DataFrame as df



def make_batch(filename):
    # make the batch
    aiplatform.init(location=parameters.location)
    model = aiplatform.Model(parameters.model_id)
    print(model.supported_input_storage_formats)
    job_display_name = 'john lemon'
    gcs_source = 'gs://' + parameters.batch_bucket + '/' + filename
    gcs_destination_prefix = 'gs://' + parameters.batch_bucket + '/result'

    batch_prediction_job = model.batch_predict(
        job_display_name=job_display_name,
        gcs_source=gcs_source,
        gcs_destination_prefix=gcs_destination_prefix,
    )
    return batch_prediction_job
