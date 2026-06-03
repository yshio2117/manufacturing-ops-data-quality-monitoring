import pytest
import os
from unittest.mock import patch, MagicMock
from src.manufacturing_ops.ingestion.record_loader import raw_records_to_bq


def test_raw_records_to_bq():
    """
    Test cases verified by this function:
    - The BigQuery Client is instantiated properly.
    - load_table_from_json() is called exactly once.
    - The correct raw data (dummy_records) is passed as the first argument.
    - The correct destination table ID is passed as the second argument.
    - 'job_config' is passed as a keyword argument.
    - result() is called on the returned load job to wait for completion.
    """
   

    dummy_records = [
        {
            "date": "2026-06-04",
            "shift": "A",
            "line": "Line1",
            "planned_output": 1234,
            "actual_output": 1233,
            "defect_qty": 123,
            "downtime_min": 0,
            "downtime_reason": "No Downtime",
            "operator": "A",
            "source_system": "Legacy Excel log"
        }
    ]

    # set BigQuery Mock and patch environment variables
    with patch("src.manufacturing_ops.ingestion.record_loader.SHIFT_LOG_RAW_TABLE_ID", "test_project.test_dataset.test_table_name"), \
         patch("src.manufacturing_ops.ingestion.record_loader.bigquery.Client") as MockClient, \
         patch("src.manufacturing_ops.ingestion.record_loader.bigquery.LoadJobConfig"):
        
        # mock Client and LoadJobConfig to prevent actual BigQuery calls during the test
        mock_client_instance = MockClient.return_value
        mock_load_job = MagicMock()
        mock_client_instance.load_table_from_json.return_value = mock_load_job
        
        
        raw_records_to_bq(dummy_records)

        
        # check if the client was called once
        MockClient.assert_called_once()
        
        expected_table = "test_project.test_dataset.test_table_name"
        
        # check if load_table_from_json was called with the correct arguments
        mock_client_instance.load_table_from_json.assert_called_once()
        args, kwargs = mock_client_instance.load_table_from_json.call_args
        
        assert args[0] == dummy_records
        assert args[1] == expected_table
        assert "job_config" in kwargs    # check if job_config is passed as a keyword argument
        
        # check if result() was called to wait for the job completion
        mock_load_job.result.assert_called_once()