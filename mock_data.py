"""Mock data for testing."""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models import AppointmentData, InsuranceData, ReportData


class MockDataGenerator:
    """Mock data generator."""
    
    # Mock appointment data
    APPOINTMENTS = [
        {
            "appointment_id": "APT-001",
            "patient_name": "John Doe",
            "appointment_date": "2024-01-15",
            "appointment_time": "10:00 AM",
            "status": "confirmed",
            "provider": "Dr. Smith",
            "location": "Main Clinic"
        },
        {
            "appointment_id": "APT-002",
            "patient_name": "Jane Smith",
            "appointment_date": "2024-01-16",
            "appointment_time": "2:30 PM",
            "status": "pending",
            "provider": "Dr. Johnson",
            "location": "Downtown Branch"
        },
        {
            "appointment_id": "APT-003",
            "patient_name": "Bob Williams",
            "appointment_date": "2024-01-14",
            "appointment_time": "9:00 AM",
            "status": "completed",
            "provider": "Dr. Brown",
            "location": "Main Clinic"
        },
        {
            "appointment_id": "APT-004",
            "patient_name": "Alice Johnson",
            "appointment_date": "2024-01-17",
            "appointment_time": "11:00 AM",
            "status": "cancelled",
            "provider": "Dr. Davis",
            "location": "Main Clinic"
        },
        {
            "appointment_id": "APT-005",
            "patient_name": "Charlie Brown",
            "appointment_date": "2024-01-18",
            "appointment_time": "3:00 PM",
            "status": "rescheduled",
            "provider": "Dr. Wilson",
            "location": "Downtown Branch"
        }
    ]
    
    # Mock insurance data
    INSURANCE_RECORDS = [
        {
            "member_id": "INS-12345",
            "insurance_provider": "BlueCross BlueShield",
            "policy_number": "BC-987654",
            "coverage_status": "active",
            "effective_date": "2023-01-01",
            "expiry_date": "2024-12-31",
            "is_valid": True
        },
        {
            "member_id": "INS-67890",
            "insurance_provider": "Aetna",
            "policy_number": "AE-456789",
            "coverage_status": "active",
            "effective_date": "2023-06-01",
            "expiry_date": "2024-05-31",
            "is_valid": True
        },
        {
            "member_id": "INS-11111",
            "insurance_provider": "UnitedHealthcare",
            "policy_number": "UH-222333",
            "coverage_status": "expired",
            "effective_date": "2022-01-01",
            "expiry_date": "2023-12-31",
            "is_valid": False
        },
        {
            "member_id": "INS-44444",
            "insurance_provider": "Cigna",
            "policy_number": "CI-555666",
            "coverage_status": "active",
            "effective_date": "2023-03-15",
            "expiry_date": "2024-03-14",
            "is_valid": True
        },
        {
            "member_id": "INS-77777",
            "insurance_provider": "Medicare",
            "policy_number": "MC-888999",
            "coverage_status": "active",
            "effective_date": "2023-01-01",
            "expiry_date": "2024-12-31",
            "is_valid": True
        }
    ]
    
    # Mock report data
    REPORT_TYPES = [
        "lab_results",
        "imaging_results",
        "billing_statement",
        "medical_history",
        "prescription_history",
        "visit_summary"
    ]
    
    # Customer to appointment mapping
    CUSTOMER_APPOINTMENTS = {
        "CUST-001": ["APT-001"],
        "CUST-002": ["APT-002"],
        "CUST-003": ["APT-003"],
        "CUST-004": ["APT-004"],
        "CUST-005": ["APT-005"]
    }
    
    # Customer to insurance mapping
    CUSTOMER_INSURANCE = {
        "CUST-001": "INS-12345",
        "CUST-002": "INS-67890",
        "CUST-003": "INS-11111",
        "CUST-004": "INS-44444",
        "CUST-005": "INS-77777"
    }
    
    @staticmethod
    def get_appointment_by_id(appointment_id: str) -> Dict[str, Any]:
        """Retrieve appointment by ID."""
        for apt in MockDataGenerator.APPOINTMENTS:
            if apt["appointment_id"] == appointment_id:
                return apt.copy()
        return None
    
    @staticmethod
    def get_appointment_by_customer(customer_id: str) -> List[Dict[str, Any]]:
        """Retrieve appointments for a customer."""
        appointment_ids = MockDataGenerator.CUSTOMER_APPOINTMENTS.get(customer_id, [])
        appointments = []
        for apt_id in appointment_ids:
            apt = MockDataGenerator.get_appointment_by_id(apt_id)
            if apt:
                appointments.append(apt)
        return appointments
    
    @staticmethod
    def get_insurance_by_member_id(member_id: str) -> Dict[str, Any]:
        """Retrieve insurance by member ID."""
        for ins in MockDataGenerator.INSURANCE_RECORDS:
            if ins["member_id"] == member_id:
                return ins.copy()
        return None
    
    @staticmethod
    def get_insurance_by_customer(customer_id: str) -> Dict[str, Any]:
        """Retrieve insurance for a customer."""
        member_id = MockDataGenerator.CUSTOMER_INSURANCE.get(customer_id)
        if member_id:
            return MockDataGenerator.get_insurance_by_member_id(member_id)
        return None
    
    @staticmethod
    def validate_insurance(customer_id: str, member_id: str = None) -> Dict[str, Any]:
        """Validate insurance information."""
        insurance_data = MockDataGenerator.get_insurance_by_customer(customer_id)
        if not insurance_data and member_id:
            insurance_data = MockDataGenerator.get_insurance_by_member_id(member_id)
        
        if insurance_data:
            return {
                "valid": insurance_data["is_valid"],
                "provider": insurance_data["insurance_provider"],
                "member_id": insurance_data["member_id"],
                "status": insurance_data["coverage_status"],
                "expiry_date": insurance_data["expiry_date"]
            }
        return {"valid": False, "reason": "Insurance not found"}
    
    @staticmethod
    def request_report(customer_id: str, report_type: str) -> Dict[str, Any]:
        """Generate a mock report request."""
        report_id = f"RPT-{random.randint(1000, 9999)}"
        return {
            "report_id": report_id,
            "customer_id": customer_id,
            "report_type": report_type,
            "status": "processing",
            "requested_date": datetime.now().isoformat(),
            "estimated_completion": (datetime.now() + timedelta(days=2)).isoformat()
        }
    
    @staticmethod
    def get_customer_info(customer_id: str) -> Dict[str, Any]:
        """Get comprehensive customer information."""
        return {
            "customer_id": customer_id,
            "appointments": MockDataGenerator.get_appointment_by_customer(customer_id),
            "insurance": MockDataGenerator.get_insurance_by_customer(customer_id)
        }

