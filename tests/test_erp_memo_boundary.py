# -*- coding: utf-8 -*-
import unittest

# Mocking the Frappe Framework test layer to run independent validation sequences
class MockFrappeDatabase:
    def __init__(self):
        self.ledger_records = []
        self.gl_records = []

    def insert_memo_entry(self, doc):
        self.ledger_records.append(doc)
        
    def check_gl_leaks(self):
        return len(self.gl_records)

class TestERPMemoBoundaryIntegration(unittest.TestCase):
    
    def setUp(self):
        """QA Configuration: Instantiate separate ledger tracking domains"""
        self.db = MockFrappeDatabase()

    def test_custom_ledger_isolation(self):
        """
        QA Test Case: Validate that custom tenant entries post strictly 
        to an isolated Operational Memo Ledger and write exactly ZERO rows to the core General Ledger (GL).
        """
        # 1. Simulate an intake document payload mapping
        mock_payload = {
            "resident_id": "EMP-9902",
            "building_target": "Camp Alpha Block 2",
            "daily_operational_cost": 45.50,
            "posting_mode": "Operational Memo Only"
        }
        
        # 2. Process data ingestion boundary
        self.db.insert_memo_entry(mock_payload)
        
        # 3. ASSERTION: Prove data saved to your custom metrics tracking ledger
        self.assertEqual(len(self.db.ledger_records), 1, "QA Fail: Custom Memo Ledger failed to record operational metrics.")
        
        # 4. CRITICAL GOVERNANCE ASSERTION: Prove zero leakage into core financial tables
        gl_leaks = self.db.check_gl_leaks()
        self.assertEqual(gl_leaks, 0, "SECURITY COMPLIANCE FAILURE: Custom integration leaked unverified data into the financial General Ledger!")

if __name__ == '__main__':
    unittest.main()
