import unittest
from unittest.mock import Mock, patch
import os
from src.GSheetWriteRead import GSheetWrite
from src.assets import update_cols

class TestGSheetWrite(unittest.TestCase):
    def setUp(self):
        self.spreadsheet_id = "test_spreadsheet_id"
        self.sheet_name = "test_sheet"
        self.test_data = {
            "name": "test_product",
            "tags": "test_tag",
            "img_url": "http://example.com/image.jpg",
            "product_url": "http://example.com/product"
        }
        
        # Mock the Google Sheets API
        self.mock_credentials = Mock()
        self.mock_service = Mock()
        self.mock_sheet = Mock()
        
        # Set up the mock chain
        self.mock_sheet.values().get().execute.return_value = {"values": []}
        self.mock_service.spreadsheets.return_value = self.mock_sheet
        self.mock_build = Mock(return_value=self.mock_service)
        
        # Patch the necessary dependencies
        self.credentials_patcher = patch('src.utils.gg_utils.check_credentials', return_value=self.mock_credentials)
        self.build_patcher = patch('googleapiclient.discovery.build', self.mock_build)
        
        self.credentials_patcher.start()
        self.build_patcher.start()
        
        # Initialize GSheetWrite with test values
        self.gsheet_writer = GSheetWrite(
            update_cols=update_cols,
            spreadsheetId=self.spreadsheet_id,
            sheet_name=self.sheet_name,
            queue_number=2,
            start_column="A"
        )

    def tearDown(self):
        self.credentials_patcher.stop()
        self.build_patcher.stop()

    def test_init(self):
        """Test initialization of GSheetWrite"""
        self.assertEqual(self.gsheet_writer.spreadsheetId, self.spreadsheet_id)
        self.assertEqual(self.gsheet_writer.sheet_name, self.sheet_name)
        self.assertEqual(self.gsheet_writer.queue_number, 2)
        self.assertEqual(self.gsheet_writer.start_column, "A")
        self.assertEqual(self.gsheet_writer.update_cols, update_cols)
        self.assertEqual(self.gsheet_writer.queue, [])

    def test_add_to_queue(self):
        """Test adding data to queue"""
        self.gsheet_writer.add_to_queue(self.test_data)
        self.assertEqual(len(self.gsheet_writer.queue), 1)
        
        # Test adding data with missing required columns
        with self.assertRaises(KeyError):
            self.gsheet_writer.add_to_queue({"invalid": "data"})

    def test_change_data_to_list(self):
        """Test converting dictionary data to list format"""
        result = self.gsheet_writer.change_data_to_list(self.test_data)
        expected = ["test_product", "test_tag", "http://example.com/image.jpg", "http://example.com/product"]
        self.assertEqual(result, expected)

    def test_queue_flush(self):
        """Test that queue is flushed when it reaches queue_number"""
        # Add data to reach queue_number
        self.gsheet_writer.add_to_queue(self.test_data)
        self.gsheet_writer.add_to_queue(self.test_data)
        
        # Queue should be empty after flush
        self.assertEqual(len(self.gsheet_writer.queue), 0)

    def test_close_queue(self):
        """Test closing queue with remaining data"""
        self.gsheet_writer.add_to_queue(self.test_data)
        self.gsheet_writer.close_queue()
        self.assertEqual(len(self.gsheet_writer.queue), 0)

    def test_write_to_gsheet_invalid_start_column(self):
        """Test write_to_gsheet with invalid start column"""
        # Create a writer with an invalid start column
        invalid_writer = GSheetWrite(
            update_cols=update_cols,
            spreadsheetId=self.spreadsheet_id,
            sheet_name=self.sheet_name,
            queue_number=2,
            start_column="Z"  # Z is not in update_cols
        )
        
        # Add some data to the queue
        invalid_writer.add_to_queue(self.test_data)
        
        # Writing should raise ValueError
        with self.assertRaises(ValueError):
            invalid_writer.write_to_gsheet()

if __name__ == '__main__':
    unittest.main() 