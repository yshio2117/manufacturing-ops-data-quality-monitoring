import pytest
import os
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from src.manufacturing_ops.ingestion.record_loader import read_records_csv_with_metadata, raw_records_to_bq


def test_read_csv_success(tmp_path):
    """Test reading a valid CSV file successfully and verifying metadata insertion."""

    csv_file = tmp_path / "sample.csv"

    csv_file.write_text(
        (
            "date,shift,line,planned_output,actual_output,"
            "defect_qty,downtime_min,downtime_reason,operator,source_system\n"
            "2025-01-01,A,Line1,100,95,2,10,Cleaning,John,Google Form\n"
        ),
        encoding="utf-8",
    )

    args = SimpleNamespace(
        input_file=str(csv_file),
        run_id="test_run",
    )

    rows = read_records_csv_with_metadata(args)

    assert len(rows) == 1

    row = rows[0]

    assert row["date"] == "2025-01-01"
    assert row["shift"] == "A"
    assert row["run_id"] == "test_run"

    assert "row_id" in row
    assert "ingested_at" in row
    assert "source_file" in row


def test_missing_required_column_raises_error(tmp_path):
    """Test that a ValueError is raised when required columns are missing from the CSV."""

    csv_file = tmp_path / "sample.csv"

    csv_file.write_text(
        (
            "date,shift,line,planned_output,actual_output,defect_qty\n"
            "2025-01-01,A,Line1,100,95,2\n"
        ),
        encoding="utf-8",
    )

    args = SimpleNamespace(
        input_file=str(csv_file),
        run_id="test_run",
    )

    with pytest.raises(ValueError, match="missing required columns"):
        read_records_csv_with_metadata(args)


def test_missing_optional_columns_are_filled_with_none(tmp_path):
    """Test that missing optional columns are automatically filled with None."""
    
    csv_file = tmp_path / "sample.csv"

    csv_file.write_text(
        (
            "date,shift,line,planned_output,actual_output,"
            "defect_qty,downtime_min\n"
            "2025-01-01,A,Line1,100,95,2,10\n"
        ),
        encoding="utf-8",
    )

    args = SimpleNamespace(
        input_file=str(csv_file),
        run_id="test_run",
    )

    rows = read_records_csv_with_metadata(args)

    row = rows[0]

    assert row["downtime_reason"] is None
    assert row["operator"] is None
    assert row["source_system"] is None


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