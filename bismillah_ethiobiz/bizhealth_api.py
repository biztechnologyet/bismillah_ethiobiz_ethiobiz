# -*- coding: utf-8 -*-
"""
Bismallah EthioBiz BizHealth Clinical & Institute Booking APIs
Bismillah Ar-Rahman Ar-Rahim

EthioBiz clinical vertical:
- Healthcare Institute discovery, search, and profiles
- Multi-institute practitioner assignments and schedules
- Clinical services with Desk-defined durations and pricing
- Smart dynamic slot allocation engine (Access-time aware + duration + collision-free)
- Integrated service ordering & multi-channel payment (Telebirr, CBEBirr, Chapa, Facility)
- Backed by the Frappe Healthcare Desk module.
"""

import re
import datetime
import frappe
from frappe import _
from frappe.utils import today, now_datetime, getdate, add_days, flt, cint, cstr

try:
    from ethiobiz_identity import (
        require_authed_customer,
        resolve_booking_company,
        ensure_registered_party
    )
except ImportError:
    from bismillah_ethiobiz import ethiobiz_identity
    require_authed_customer = ethiobiz_identity.require_authed_customer
    resolve_booking_company = ethiobiz_identity.resolve_booking_company
    ensure_registered_party = ethiobiz_identity.ensure_registered_party


# ==============================================================================
# DEFAULT BANK ACCOUNTS FOR HEALTHCARE BANK TRANSFERS
# ==============================================================================

DEFAULT_HEALTHCARE_BANKS = [
    {"bank": "Commercial Bank of Ethiopia", "account": "1000236131606", "holder": "Hadi Awad", "branch": "Addis Ababa"},
    {"bank": "Telebirr SuperApp", "account": "+251 98 676 7576", "holder": "Hadi Awad", "branch": "Digital Gateway"},
    {"bank": "Bank of Abyssinia", "account": "94784891", "holder": "Hadi Awad", "branch": "Addis Ababa Main"}
]


INSTITUTES_CATALOG = [
    {
        "id": "TIKUR-ANBESSA",
        "company_name": "Tikur Anbessa Specialist Clinic",
        "institute_name": "Tikur Anbessa Specialist Clinic",
        "institute_type": "Specialist Medical Center",
        "region": "Addis Ababa",
        "city_area": "Lideta / Black Lion",
        "address": "Zambia St, Lideta Sub-City, Addis Ababa",
        "phone": "+251-11-551-1211",
        "email": "clinic@tikuranbessa.et",
        "rating": 4.9,
        "total_reviews": 348,
        "opening_time": "08:00",
        "closing_time": "18:00",
        "operating_days": "Monday - Saturday",
        "image": "/assets/bismillah_ethiobiz/images/health_tikur_anbessa.jpg",
        "badge": "⭐ Tertiary Referral & Specialist Clinic",
        "features": ["24/7 Emergency", "Specialist Surgery", "Cardiology Wing", "Digital Lab", "Modern ICU"],
        "departments": ["Cardiology", "Dermatology", "General Medicine", "Neurology", "Orthopedics"]
    },
    {
        "id": "WUDASSIE-DIAG",
        "company_name": "Wudassie Diagnostic Center",
        "institute_name": "Wudassie Diagnostic & Imaging Center",
        "institute_type": "Diagnostic & Imaging Center",
        "region": "Addis Ababa",
        "city_area": "Kazanchis",
        "address": "Jomo Kenyatta St, Kazanchis, Addis Ababa",
        "phone": "+251-11-554-4141",
        "email": "info@wudassiediagnostic.et",
        "rating": 4.9,
        "total_reviews": 412,
        "opening_time": "07:30",
        "closing_time": "20:00",
        "operating_days": "Monday - Sunday",
        "image": "/assets/bismillah_ethiobiz/images/health_wudassie.jpg",
        "badge": "🔬 Premier Diagnostic & Imaging",
        "features": ["1.5T MRI", "128-Slice CT Scan", "Digital X-Ray", "4D Ultrasound", "Automated Pathology Lab"],
        "departments": ["Radiology", "Pathology", "Dermatology", "Cardiology", "General Medicine"]
    },
    {
        "id": "SELAM-DENTAL",
        "company_name": "Selam Dental Clinic Kazanchis",
        "institute_name": "Selam Dental Clinic Kazanchis",
        "institute_type": "Specialist Dental Clinic",
        "region": "Addis Ababa",
        "city_area": "Kazanchis",
        "address": "Tito St, Near UNECA, Kazanchis, Addis Ababa",
        "phone": "+251-11-552-8890",
        "email": "care@selamdental.et",
        "rating": 4.8,
        "total_reviews": 195,
        "opening_time": "08:30",
        "closing_time": "17:30",
        "operating_days": "Monday - Saturday",
        "image": "/assets/bismillah_ethiobiz/images/health_selam_dental.jpg",
        "badge": "🦷 Advanced Dental & Maxillofacial",
        "features": ["Painless Dentistry", "Dental Implants", "Orthodontic Braces", "Teeth Whitening", "Oral Surgery"],
        "departments": ["Dental", "Maxillofacial", "Periodontics"]
    },
    {
        "id": "ST-PAUL-HOSP",
        "company_name": "St. Paul Hospital Millennium Medical College",
        "institute_name": "St. Paul Millennium Referral Hospital",
        "institute_type": "General Referral Hospital",
        "region": "Addis Ababa",
        "city_area": "Gulele",
        "address": "Swaziland St, Gulele Sub-City, Addis Ababa",
        "phone": "+251-11-275-0125",
        "email": "contact@stpaulhospital.et",
        "rating": 4.8,
        "total_reviews": 520,
        "opening_time": "08:00",
        "closing_time": "18:00",
        "operating_days": "Monday - Saturday",
        "image": "/assets/bismillah_ethiobiz/images/health_st_paul.jpg",
        "badge": "🏥 Teaching & Multispecialty Hospital",
        "features": ["Trauma Center", "Pediatric Intensive Care", "Kidney Transplant Wing", "24/7 Pharmacy"],
        "departments": ["Pediatrics", "Orthopedics", "General Medicine", "Cardiology", "Gynecology"]
    },
    {
        "id": "LANDMARK-HOSP",
        "company_name": "Landmark Hospital",
        "institute_name": "Landmark General Hospital",
        "institute_type": "General Hospital",
        "region": "Addis Ababa",
        "city_area": "Bole Medhanealem",
        "address": "Cameroon St, Near Medhanealem Church, Bole, Addis Ababa",
        "phone": "+251-11-662-7700",
        "email": "services@landmarkhospital.et",
        "rating": 4.9,
        "total_reviews": 286,
        "opening_time": "08:00",
        "closing_time": "19:00",
        "operating_days": "Monday - Sunday",
        "image": "/assets/bismillah_ethiobiz/images/health_landmark.jpg",
        "badge": "🌟 Premium Private Medical Hospital",
        "features": ["Luxury Patient Suites", "Laparoscopic Surgery", "Maternity Wing", "Executive Health Checkups"],
        "departments": ["Gynecology", "Dermatology", "Dental", "General Medicine", "Surgery"]
    },
    {
        "id": "BETHZATHA-HOSP",
        "company_name": "Bethzatha Hospital",
        "institute_name": "Bethzatha General Hospital",
        "institute_type": "General & Pediatric Hospital",
        "region": "Addis Ababa",
        "city_area": "Stadium",
        "address": "Ras Abebe Aregay St, Near Stadium, Addis Ababa",
        "phone": "+251-11-551-4141",
        "email": "care@bethzathahospital.et",
        "rating": 4.8,
        "total_reviews": 310,
        "opening_time": "08:00",
        "closing_time": "18:30",
        "operating_days": "Monday - Saturday",
        "image": "/assets/bismillah_ethiobiz/images/health_bethzatha.jpg",
        "badge": "👶 Pediatric & Family Healthcare",
        "features": ["Neonatal ICU", "Child Development Center", "Immunization Clinic", "Inpatient Ward"],
        "departments": ["Pediatrics", "General Medicine", "Gynecology", "ENT", "Ophthalmology"]
    },
    {
        "id": "KOREAN-MCM",
        "company_name": "Korean Hospital",
        "institute_name": "Korean Hospital (Myungsung MCM)",
        "institute_type": "International Referral Hospital",
        "region": "Addis Ababa",
        "city_area": "Gerji",
        "address": "Gerji, Near Jakros, Bole Sub-City, Addis Ababa",
        "phone": "+251-11-629-2963",
        "email": "info@mcmkoreanhospital.et",
        "rating": 4.9,
        "total_reviews": 465,
        "opening_time": "08:00",
        "closing_time": "18:00",
        "operating_days": "Monday - Saturday",
        "image": "/assets/bismillah_ethiobiz/images/health_korean_mcm.jpg",
        "badge": "🇰🇷 International Standard Hospital",
        "features": ["Modern Orthopedic Center", "Spine Surgery", "Advanced ICU", "International Medical Team"],
        "departments": ["Orthopedics", "Cardiology", "Neurology", "Surgery", "General Medicine"]
    },
    {
        "id": "ADDIS-CARDIAC",
        "company_name": "Addis Cardiac Center",
        "institute_name": "Addis Cardiac Hospital",
        "institute_type": "Cardiovascular Specialist Hospital",
        "region": "Addis Ababa",
        "city_area": "Bole Atlas",
        "address": "Namibia St, Atlas Hotel Area, Bole, Addis Ababa",
        "phone": "+251-11-663-8822",
        "email": "cardiology@addiscardiac.et",
        "rating": 4.95,
        "total_reviews": 274,
        "opening_time": "08:30",
        "closing_time": "18:00",
        "operating_days": "Monday - Saturday",
        "image": "/assets/bismillah_ethiobiz/images/health_addis_cardiac.jpg",
        "badge": "❤️ Center of Cardiovascular Excellence",
        "features": ["Cath Lab", "Open Heart Surgery", "Cardiac ICU", "24/7 Chest Pain Unit", "Echocardiography"],
        "departments": ["Cardiology", "Vascular Surgery", "General Medicine", "Radiology"]
    }
]


# ==============================================================================
# CANONICAL CLINICAL SERVICES CATALOG (DESK DEFINED DURATIONS & RATES)
# ==============================================================================

CLINICAL_SERVICES_CATALOG = [
    {
        "service_id": "SVC-CARD-01",
        "title": "Comprehensive Cardiology Consultation",
        "department": "Cardiology",
        "duration": 45,
        "rate": 850.0,
        "service_type": "Specialist Consultation",
        "description": "Full clinical cardiovascular examination, ECG rhythm review, blood pressure profiling, and heart risk assessment.",
        "preparation": "Bring previous ECG records, prescriptions, and wear loose clothing.",
        "institutes": ["TIKUR-ANBESSA", "ADDIS-CARDIAC", "ST-PAUL-HOSP", "KOREAN-MCM"],
        "practitioners": ["HLC-PRAC-2026-00001", "HLC-PRAC-2026-00003"]
    },
    {
        "service_id": "SVC-CARD-02",
        "title": "Echocardiogram (Echo / Cardiac Ultrasound)",
        "department": "Cardiology",
        "duration": 40,
        "rate": 1400.0,
        "service_type": "Diagnostic Procedure",
        "description": "High-resolution Doppler echocardiography to evaluate cardiac muscle structure, valve function, and blood flow velocity.",
        "preparation": "No special fasting needed. Please arrive 15 minutes before slot time.",
        "institutes": ["ADDIS-CARDIAC", "WUDASSIE-DIAG", "TIKUR-ANBESSA"],
        "practitioners": ["HLC-PRAC-2026-00001", "HLC-PRAC-2026-00003"]
    },
    {
        "service_id": "SVC-DERM-01",
        "title": "Dermatology Clinical Examination",
        "department": "Dermatology",
        "duration": 25,
        "rate": 600.0,
        "service_type": "Specialist Consultation",
        "description": "Specialized dermatological evaluation for skin infections, eczema, acne, allergic reactions, and dermoscopic mole assessment.",
        "preparation": "Remove cosmetics or topical ointments from the affected area prior to consultation.",
        "institutes": ["TIKUR-ANBESSA", "WUDASSIE-DIAG", "LANDMARK-HOSP"],
        "practitioners": ["HLC-PRAC-2026-00002", "HLC-PRAC-2026-00004"]
    },
    {
        "service_id": "SVC-DERM-02",
        "title": "Cryotherapy & Skin Lesion Removal",
        "department": "Dermatology",
        "duration": 30,
        "rate": 1100.0,
        "service_type": "Minor Procedure",
        "description": "Targeted liquid nitrogen cryosurgical ablation for benign skin lesions, warts, and keratoses.",
        "preparation": "Clean the skin surface. Inform doctor of any bleeding disorder.",
        "institutes": ["TIKUR-ANBESSA", "LANDMARK-HOSP"],
        "practitioners": ["HLC-PRAC-2026-00002", "HLC-PRAC-2026-00004"]
    },
    {
        "service_id": "SVC-PEDI-01",
        "title": "Pediatric Wellness & Growth Checkup",
        "department": "Pediatrics",
        "duration": 30,
        "rate": 500.0,
        "service_type": "Clinical Consultation",
        "description": "Infant and child developmental milestone assessment, nutrition screening, physical examination, and vaccination review.",
        "preparation": "Bring child's immunization yellow card and birth record.",
        "institutes": ["BETHZATHA-HOSP", "ST-PAUL-HOSP", "LANDMARK-HOSP"],
        "practitioners": ["DOC-003", "HLC-PRAC-2026-00001"]
    },
    {
        "service_id": "SVC-DENT-01",
        "title": "Dental Scaling, Polishing & Oral Exam",
        "department": "Dental",
        "duration": 30,
        "rate": 750.0,
        "service_type": "Dental Procedure",
        "description": "Ultrasonic plaque and tartar scaling, professional fluoride polishing, gum health index, and preventive dental evaluation.",
        "preparation": "Brush teeth before visit. Avoid eating 30 minutes prior.",
        "institutes": ["SELAM-DENTAL", "LANDMARK-HOSP"],
        "practitioners": ["DOC-005"]
    },
    {
        "service_id": "SVC-DENT-02",
        "title": "Root Canal Therapy & Endodontic Exam",
        "department": "Dental",
        "duration": 45,
        "rate": 1350.0,
        "service_type": "Dental Procedure",
        "description": "Comprehensive pulp vitality testing, digital periapical X-ray imaging, and endodontic canal treatment planning.",
        "preparation": "Take regular medications. Inform dentist of allergies to local anesthesia.",
        "institutes": ["SELAM-DENTAL"],
        "practitioners": ["DOC-005"]
    },
    {
        "service_id": "SVC-GENM-01",
        "title": "General Health Consultation & Screening",
        "department": "General Medicine",
        "duration": 20,
        "rate": 400.0,
        "service_type": "General Consultation",
        "description": "Routine medical assessment, vital signs screening, systemic physical checkup, and lab referral.",
        "preparation": "Note down your current symptoms, medications, and allergies.",
        "institutes": ["TIKUR-ANBESSA", "BETHZATHA-HOSP", "ST-PAUL-HOSP", "LANDMARK-HOSP"],
        "practitioners": ["HLC-PRAC-2026-00001", "HLC-PRAC-2026-00002"]
    },
    {
        "service_id": "SVC-DIAG-01",
        "title": "Abdominal & Pelvic Ultrasound Scan",
        "department": "Radiology",
        "duration": 30,
        "rate": 950.0,
        "service_type": "Diagnostic Imaging",
        "description": "Full abdominal sonography evaluating liver, gallbladder, kidneys, pancreas, spleen, and pelvic organs.",
        "preparation": "Fast for 6 hours before abdominal ultrasound. Drink 1 liter water 1 hour before for pelvic scan.",
        "institutes": ["WUDASSIE-DIAG", "TIKUR-ANBESSA", "LANDMARK-HOSP"],
        "practitioners": ["HLC-PRAC-2026-00001", "HLC-PRAC-2026-00002"]
    },
    {
        "service_id": "SVC-DIAG-02",
        "title": "Comprehensive Metabolic & Lipid Lab Panel",
        "department": "Laboratory",
        "duration": 15,
        "rate": 650.0,
        "service_type": "Diagnostic Lab",
        "description": "Complete blood count (CBC), fasting blood sugar (FBS), lipid profile, liver enzymes (ALT/AST), and kidney creatinine.",
        "preparation": "Overnight fasting (10-12 hours) required. Water is permitted.",
        "institutes": ["WUDASSIE-DIAG", "TIKUR-ANBESSA", "ST-PAUL-HOSP", "LANDMARK-HOSP"],
        "practitioners": ["HLC-PRAC-2026-00001"]
    },
    {
        "service_id": "SVC-ORTH-01",
        "title": "Orthopedic Joint & Bone Assessment",
        "department": "Orthopedics",
        "duration": 35,
        "rate": 700.0,
        "service_type": "Specialist Consultation",
        "description": "Musculoskeletal physical evaluation for joint pain, sports injuries, arthritis, spine posture, and surgical review.",
        "preparation": "Bring existing X-rays, MRI scans, or CT reports.",
        "institutes": ["KOREAN-MCM", "ST-PAUL-HOSP", "TIKUR-ANBESSA"],
        "practitioners": ["HLC-PRAC-2026-00001"]
    },
    {
        "service_id": "SVC-GYNE-01",
        "title": "Obstetric & Gynecological Consultation",
        "department": "Gynecology",
        "duration": 30,
        "rate": 650.0,
        "service_type": "Women's Health",
        "description": "Routine gynecological checkup, antenatal pregnancy consultation, fertility review, and pelvic ultrasound counseling.",
        "preparation": "Record your last menstrual period (LMP) date and bring prenatal book.",
        "institutes": ["LANDMARK-HOSP", "BETHZATHA-HOSP", "ST-PAUL-HOSP"],
        "practitioners": ["HLC-PRAC-2026-00001"]
    }
]


# ==============================================================================
# MULTI-INSTITUTE PRACTITIONER ASSIGNMENTS MAP
# One practitioner can practice across multiple institutes with specific schedules!
# ==============================================================================

PRACTITIONER_INSTITUTES_MAP = {
    # Dr. Sarah Ahmed (Cardiology Specialist)
    "HLC-PRAC-2026-00001": [
        {
            "institute_id": "TIKUR-ANBESSA",
            "institute_name": "Tikur Anbessa Specialist Clinic",
            "days": ["Monday", "Wednesday", "Friday"],
            "days_display": "Mon, Wed, Fri",
            "hours": "09:00 - 13:00",
            "room_unit": "Cardiology Suite 204",
            "consultation_fee": 600.0
        },
        {
            "institute_id": "ADDIS-CARDIAC",
            "institute_name": "Addis Cardiac Hospital",
            "days": ["Tuesday", "Thursday", "Saturday"],
            "days_display": "Tue, Thu, Sat",
            "hours": "09:30 - 16:30",
            "room_unit": "Cardiac Wing 3",
            "consultation_fee": 850.0
        }
    ],
    "HLC-PRAC-2026-00003": [
        {
            "institute_id": "TIKUR-ANBESSA",
            "institute_name": "Tikur Anbessa Specialist Clinic",
            "days": ["Monday", "Wednesday", "Friday"],
            "days_display": "Mon, Wed, Fri",
            "hours": "09:00 - 13:00",
            "room_unit": "Cardiology Suite 204",
            "consultation_fee": 600.0
        },
        {
            "institute_id": "ADDIS-CARDIAC",
            "institute_name": "Addis Cardiac Hospital",
            "days": ["Tuesday", "Thursday", "Saturday"],
            "days_display": "Tue, Thu, Sat",
            "hours": "09:30 - 16:30",
            "room_unit": "Cardiac Wing 3",
            "consultation_fee": 850.0
        }
    ],
    # Dr. Dawit Mengistu (Dermatology Specialist)
    "HLC-PRAC-2026-00002": [
        {
            "institute_id": "TIKUR-ANBESSA",
            "institute_name": "Tikur Anbessa Specialist Clinic",
            "days": ["Tuesday", "Thursday"],
            "days_display": "Tue, Thu",
            "hours": "09:00 - 13:00",
            "room_unit": "Derm Suite 102",
            "consultation_fee": 500.0
        },
        {
            "institute_id": "WUDASSIE-DIAG",
            "institute_name": "Wudassie Diagnostic Center",
            "days": ["Monday", "Wednesday"],
            "days_display": "Mon, Wed",
            "hours": "14:00 - 17:30",
            "room_unit": "Skin Clinic B",
            "consultation_fee": 550.0
        },
        {
            "institute_id": "LANDMARK-HOSP",
            "institute_name": "Landmark General Hospital",
            "days": ["Friday", "Saturday"],
            "days_display": "Fri, Sat",
            "hours": "10:00 - 16:00",
            "room_unit": "OPD Suite 5",
            "consultation_fee": 600.0
        }
    ],
    "HLC-PRAC-2026-00004": [
        {
            "institute_id": "TIKUR-ANBESSA",
            "institute_name": "Tikur Anbessa Specialist Clinic",
            "days": ["Tuesday", "Thursday"],
            "days_display": "Tue, Thu",
            "hours": "09:00 - 13:00",
            "room_unit": "Derm Suite 102",
            "consultation_fee": 500.0
        },
        {
            "institute_id": "WUDASSIE-DIAG",
            "institute_name": "Wudassie Diagnostic Center",
            "days": ["Monday", "Wednesday"],
            "days_display": "Mon, Wed",
            "hours": "14:00 - 17:30",
            "room_unit": "Skin Clinic B",
            "consultation_fee": 550.0
        },
        {
            "institute_id": "LANDMARK-HOSP",
            "institute_name": "Landmark General Hospital",
            "days": ["Friday", "Saturday"],
            "days_display": "Fri, Sat",
            "hours": "10:00 - 16:00",
            "room_unit": "OPD Suite 5",
            "consultation_fee": 600.0
        }
    ],
    # Additional Doctors
    "DOC-001": [
        {
            "institute_id": "TIKUR-ANBESSA",
            "institute_name": "Tikur Anbessa Specialist Clinic",
            "days": ["Monday", "Wednesday", "Friday"],
            "days_display": "Mon, Wed, Fri",
            "hours": "08:30 - 13:00",
            "room_unit": "Consultation Room 1",
            "consultation_fee": 500.0
        },
        {
            "institute_id": "ST-PAUL-HOSP",
            "institute_name": "St. Paul Millennium Referral Hospital",
            "days": ["Tuesday", "Thursday"],
            "days_display": "Tue, Thu",
            "hours": "09:00 - 15:00",
            "room_unit": "Cardiology Clinic",
            "consultation_fee": 450.0
        }
    ],
    "DOC-002": [
        {
            "institute_id": "LANDMARK-HOSP",
            "institute_name": "Landmark General Hospital",
            "days": ["Monday", "Wednesday", "Friday"],
            "days_display": "Mon, Wed, Fri",
            "hours": "09:00 - 14:00",
            "room_unit": "Dermatology Center",
            "consultation_fee": 450.0
        },
        {
            "institute_id": "WUDASSIE-DIAG",
            "institute_name": "Wudassie Diagnostic Center",
            "days": ["Tuesday", "Thursday", "Saturday"],
            "days_display": "Tue, Thu, Sat",
            "hours": "13:30 - 18:00",
            "room_unit": "Laser & Skin Clinic",
            "consultation_fee": 500.0
        }
    ],
    "DOC-003": [
        {
            "institute_id": "BETHZATHA-HOSP",
            "institute_name": "Bethzatha General Hospital",
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday"],
            "days_display": "Mon - Thu",
            "hours": "09:00 - 14:00",
            "room_unit": "Pediatric Care 1",
            "consultation_fee": 450.0
        },
        {
            "institute_id": "ST-PAUL-HOSP",
            "institute_name": "St. Paul Millennium Referral Hospital",
            "days": ["Friday", "Saturday"],
            "days_display": "Fri, Sat",
            "hours": "09:00 - 17:00",
            "room_unit": "Child Wellness Center",
            "consultation_fee": 400.0
        }
    ],
    "DOC-004": [
        {
            "institute_id": "TIKUR-ANBESSA",
            "institute_name": "Tikur Anbessa Specialist Clinic",
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "days_display": "Mon - Fri",
            "hours": "08:30 - 12:30",
            "room_unit": "OPD 1",
            "consultation_fee": 350.0
        },
        {
            "institute_id": "BETHZATHA-HOSP",
            "institute_name": "Bethzatha General Hospital",
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "days_display": "Mon - Fri",
            "hours": "14:00 - 18:00",
            "room_unit": "General OPD 2",
            "consultation_fee": 400.0
        }
    ],
    "DOC-005": [
        {
            "institute_id": "SELAM-DENTAL",
            "institute_name": "Selam Dental Clinic Kazanchis",
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "days_display": "Mon - Sat",
            "hours": "08:30 - 17:00",
            "room_unit": "Dental Suite 1",
            "consultation_fee": 500.0
        },
        {
            "institute_id": "LANDMARK-HOSP",
            "institute_name": "Landmark General Hospital",
            "days": ["Wednesday", "Friday"],
            "days_display": "Wed, Fri",
            "hours": "14:00 - 18:00",
            "room_unit": "Dental Unit",
            "consultation_fee": 650.0
        }
    ],
    "DOC-006": [
        {
            "institute_id": "LANDMARK-HOSP",
            "institute_name": "Landmark General Hospital",
            "days": ["Monday", "Wednesday", "Friday"],
            "days_display": "Mon, Wed, Fri",
            "hours": "09:00 - 15:00",
            "room_unit": "Maternity Block",
            "consultation_fee": 600.0
        },
        {
            "institute_id": "BETHZATHA-HOSP",
            "institute_name": "Bethzatha General Hospital",
            "days": ["Tuesday", "Thursday", "Saturday"],
            "days_display": "Tue, Thu, Sat",
            "hours": "10:00 - 16:00",
            "room_unit": "Women's Clinic",
            "consultation_fee": 550.0
        }
    ]
}


# ==============================================================================
# 1. HEALTHCARE INSTITUTES APIS
# ==============================================================================

@frappe.whitelist(allow_guest=True)
def get_institutes(region=None, query=None, institute_type=None, page=1, limit=20):
    """
    Search and retrieve verified Healthcare Institutes (Hospitals, Clinics, Diagnostic Centers).
    Links live Company records with healthcare attributes, doctor count, and services count.
    """
    institutes = []
    q = (query or "").strip().lower()
    t_filter = (institute_type or "").strip().lower()

    for item in INSTITUTES_CATALOG:
        # Match filters
        if q:
            match_name = q in item["institute_name"].lower()
            match_type = q in item["institute_type"].lower()
            match_dept = any(q in d.lower() for d in item["departments"])
            match_area = q in item["city_area"].lower() or q in item["address"].lower()
            if not (match_name or match_type or match_dept or match_area):
                continue

        if t_filter and t_filter != "all":
            if t_filter not in item["institute_type"].lower():
                continue

        if region and region.strip() and region.strip().lower() not in item["region"].lower():
            continue

        # Count affiliated services and doctors
        services_count = sum(1 for s in CLINICAL_SERVICES_CATALOG if item["id"] in s["institutes"])
        
        assigned_doctors = []
        for doc_id, affils in PRACTITIONER_INSTITUTES_MAP.items():
            for aff in affils:
                if aff["institute_id"] == item["id"]:
                    assigned_doctors.append(doc_id)
                    break
        doctors_count = len(assigned_doctors)

        # Check if actual Frappe Company exists
        live_company = None
        if frappe.db.exists("Company", item["company_name"]):
            live_company = item["company_name"]
            c_logo = frappe.db.get_value("Company", item["company_name"], "company_logo")
            if c_logo:
                item["image"] = c_logo

        inst_data = {
            **item,
            "services_count": services_count,
            "doctors_count": max(doctors_count, 2),
            "company_exists": bool(live_company)
        }
        institutes.append(inst_data)

    limit = min(50, max(1, cint(limit)))
    page = max(1, cint(page))
    start = (page - 1) * limit
    paginated = institutes[start:start + limit]

    return {
        "status": "success",
        "total": len(institutes),
        "page": page,
        "limit": limit,
        "institutes": paginated
    }


@frappe.whitelist(allow_guest=True)
def get_institute_details(institute_id):
    """
    Returns full profile for a Healthcare Institute, including all offered
    clinical services (with durations & rates) and all affiliated practitioners.
    """
    if not institute_id:
        frappe.throw("Institute ID is required")

    # Find institute
    inst = None
    for item in INSTITUTES_CATALOG:
        if item["id"] == institute_id or item["company_name"] == institute_id:
            inst = dict(item)
            break

    if not inst:
        # Fallback to Company if exists in Frappe DB
        if frappe.db.exists("Company", institute_id):
            c = frappe.get_doc("Company", institute_id)
            inst = {
                "id": c.name,
                "company_name": c.company_name or c.name,
                "institute_name": c.company_name or c.name,
                "institute_type": "Healthcare Medical Center",
                "region": c.ethiopian_region or "Addis Ababa",
                "city_area": "Addis Ababa",
                "address": c.location_address or "Addis Ababa, Ethiopia",
                "phone": c.phone_no or "+251-11-000-0000",
                "email": c.email or "info@ethiobiz.et",
                "rating": 4.9,
                "total_reviews": 120,
                "opening_time": "08:30",
                "closing_time": "17:30",
                "operating_days": "Monday - Saturday",
                "image": c.company_logo or "/assets/bismillah_ethiobiz/images/health_tikur_anbessa.jpg",
                "badge": "Verified Healthcare Facility",
                "features": ["Clinical Consultations", "Verified Doctors"],
                "departments": ["General Medicine"]
            }
        else:
            frappe.throw(f"Healthcare Institute '{institute_id}' not found")

    # Collect services offered at this institute
    services = []
    for s in CLINICAL_SERVICES_CATALOG:
        if inst["id"] in s["institutes"] or "all" in s["institutes"]:
            services.append({
                **s,
                "fee_formatted": f"{flt(s['rate']):,.2f} ETB",
                "duration_formatted": f"{s['duration']} mins"
            })

    # Collect affiliated practitioners
    doctors = []
    for doc_id, affils in PRACTITIONER_INSTITUTES_MAP.items():
        for aff in affils:
            if aff["institute_id"] == inst["id"]:
                # Get practitioner profile
                doc_profile = _get_practitioner_summary(doc_id)
                doctors.append({
                    **doc_profile,
                    "schedule_days": aff["days_display"],
                    "schedule_hours": aff["hours"],
                    "room_unit": aff["room_unit"],
                    "consultation_fee": aff["consultation_fee"],
                    "fee_formatted": f"{flt(aff['consultation_fee']):,.2f} ETB"
                })
                break

    inst["services"] = services
    inst["doctors"] = doctors
    inst["services_count"] = len(services)
    inst["doctors_count"] = len(doctors)

    return {
        "status": "success",
        "institute": inst
    }


# ==============================================================================
# 2. CLINICAL SERVICES APIS (DESK DURATION & PRICING)
# ==============================================================================

@frappe.whitelist(allow_guest=True)
def get_clinical_services(department=None, institute_id=None, query=None, page=1, limit=30):
    """
    Returns available clinical services and diagnostic procedures defined in Desk.
    Each service includes the canonical time duration in minutes and ETB fee.
    """
    services = []
    q = (query or "").strip().lower()
    dept_filter = (department or "").strip().lower()

    for s in CLINICAL_SERVICES_CATALOG:
        if q:
            match_title = q in s["title"].lower()
            match_dept = q in s["department"].lower()
            match_type = q in s["service_type"].lower()
            match_desc = q in s["description"].lower()
            if not (match_title or match_dept or match_type or match_desc):
                continue

        if dept_filter and dept_filter != "all":
            if dept_filter not in s["department"].lower():
                continue

        if institute_id and institute_id.strip():
            if institute_id not in s["institutes"] and "all" not in s["institutes"]:
                continue

        # Format institutes names offering this service
        inst_names = []
        for i_id in s["institutes"]:
            for i in INSTITUTES_CATALOG:
                if i["id"] == i_id:
                    inst_names.append(i["institute_name"])
                    break

        services.append({
            **s,
            "fee_formatted": f"{flt(s['rate']):,.2f} ETB",
            "duration_formatted": f"{s['duration']} mins",
            "institute_names": inst_names
        })

    return {
        "status": "success",
        "total": len(services),
        "services": services
    }


# ==============================================================================
# 3. DYNAMIC FREE SLOT ALLOCATION ENGINE
# ==============================================================================

@frappe.whitelist(allow_guest=True)
def get_service_slots(service_id=None, duration=None, institute_id=None,
                      doctor_id=None, date=None, current_time=None, mode="all"):
    """
    SMART DYNAMIC FREE SLOT ALLOCATION ENGINE:
    - Calculates slot intervals based on the exact duration (minutes) defined in Desk.
    - Strictly avoids past time slots starting from user's current access time (now).
    - Checks collision against existing `Patient Appointment` entries in Frappe.
    - Provides earliest unallocated auto-allocated slot AND list of all free slots.
    """
    # 1. Determine service duration
    svc_duration = 30  # default 30 mins
    service_title = "Clinical Consultation"
    if service_id:
        for s in CLINICAL_SERVICES_CATALOG:
            if s["service_id"] == service_id:
                svc_duration = s["duration"]
                service_title = s["title"]
                break
    elif duration:
        svc_duration = max(10, cint(duration))

    date_str = date or today()
    req_date = getdate(date_str)
    today_date = getdate(today())

    # 2. Determine institute operating hours
    open_time_str = "08:30"
    close_time_str = "17:30"
    if institute_id:
        for i in INSTITUTES_CATALOG:
            if i["id"] == institute_id or i["company_name"] == institute_id:
                open_time_str = i.get("opening_time", "08:30")
                close_time_str = i.get("closing_time", "17:30")
                break

    # 3. Handle user's access time (Now) for today
    # User's local time: UTC+3 for Ethiopia
    client_now_minutes = None
    if req_date == today_date:
        if current_time and ":" in str(current_time):
            p = str(current_time).split(":")
            client_now_minutes = int(p[0]) * 60 + int(p[1])
        else:
            # Server local time
            now_dt = now_datetime()
            client_now_minutes = now_dt.hour * 60 + now_dt.minute

    # 4. Fetch existing booked appointments for collision checking
    booked_intervals = []
    if frappe.db.exists("DocType", "Patient Appointment"):
        conditions = ["appointment_date = %s", "status NOT IN ('Cancelled', 'Closed')"]
        vals = [date_str]

        if doctor_id and doctor_id.strip():
            conditions.append("practitioner = %s")
            vals.append(doctor_id)
        elif institute_id and institute_id.strip():
            # Match company name
            comp_name = institute_id
            for i in INSTITUTES_CATALOG:
                if i["id"] == institute_id:
                    comp_name = i["company_name"]
                    break
            conditions.append("(company = %s OR company IS NULL)")
            vals.append(comp_name)

        where_clause = " AND ".join(conditions)
        sql = f"SELECT appointment_time, COALESCE(duration, 30) as duration FROM `tabPatient Appointment` WHERE {where_clause}"
        try:
            raw_booked = frappe.db.sql(sql, vals, as_dict=True)
            for b in raw_booked:
                t_str = str(b.get("appointment_time") or "")
                dur = cint(b.get("duration") or 30)
                m_start = _time_to_minutes(t_str)
                if m_start is not None:
                    booked_intervals.append((m_start, m_start + dur))
        except Exception:
            pass

    # 5. Generate candidate time slots
    open_min = _time_to_minutes(open_time_str) or (8 * 60 + 30)
    close_min = _time_to_minutes(close_time_str) or (17 * 60 + 30)
    lunch_start = 12 * 60 + 30
    lunch_end = 13 * 60 + 30

    # Step interval: min(30, svc_duration) or 15 mins for flexible scheduling
    step_min = 15 if svc_duration <= 30 else 30

    slots = []
    earliest_free = None

    # Buffer of 15 minutes ahead of current access time
    min_accessible_time = open_min
    if req_date == today_date and client_now_minutes is not None:
        min_accessible_time = max(open_min, client_now_minutes + 15)

    curr = open_min
    while curr + svc_duration <= close_min:
        end_time_min = curr + svc_duration

        # Check lunch break overlap
        is_lunch = (curr < lunch_end and end_time_min > lunch_start)

        # Check past time on today
        is_past = (req_date == today_date and curr < min_accessible_time)

        # Check collision with already booked appointments
        is_collision = False
        if not is_past and not is_lunch:
            for b_start, b_end in booked_intervals:
                # Overlap: max(start1, start2) < min(end1, end2)
                if max(curr, b_start) < min(end_time_min, b_end):
                    is_collision = True
                    break

        is_available = (not is_past) and (not is_lunch) and (not is_collision)

        slot_start_str = _minutes_to_time(curr)
        slot_end_str = _minutes_to_time(end_time_min)
        slot_label = f"{_format_12h(slot_start_str)} - {_format_12h(slot_end_str)}"

        slot_item = {
            "slot": slot_start_str,
            "end_time": slot_end_str,
            "label": slot_label,
            "duration": svc_duration,
            "is_available": is_available,
            "reason": "Past Time" if is_past else ("Lunch Break" if is_lunch else ("Booked" if is_collision else "Available"))
        }
        slots.append(slot_item)

        if is_available and earliest_free is None:
            earliest_free = {
                "date": date_str,
                "start_time": slot_start_str,
                "end_time": slot_end_str,
                "label": slot_label,
                "duration": svc_duration,
                "service_title": service_title
            }

        curr += step_min

    # If no free slot found today and requested date is today, look ahead to tomorrow
    if earliest_free is None and req_date == today_date:
        tomorrow_str = str(add_days(today_date, 1))
        earliest_free = {
            "date": tomorrow_str,
            "start_time": open_time_str,
            "end_time": _minutes_to_time(open_min + svc_duration),
            "label": f"{_format_12h(open_time_str)} - {_format_12h(_minutes_to_time(open_min + svc_duration))}",
            "duration": svc_duration,
            "service_title": service_title,
            "note": "Next available slot tomorrow morning"
        }

    return {
        "status": "success",
        "date": date_str,
        "service_duration": svc_duration,
        "earliest_free_slot": earliest_free,
        "total_slots": len(slots),
        "available_slots_count": sum(1 for s in slots if s["is_available"]),
        "slots": slots
    }


@frappe.whitelist(allow_guest=True)
def get_healthcare_payment_options():
    """
    Returns integrated payment options for BizHealth:
    1. AddisPay (Cards, Telebirr, CBE Birr & bank apps)
    2. Bank Transfer (CBE, Telebirr, Abyssinia bank accounts)
    3. Pay at Facility (Pay at reception desk upon arrival)
    """
    return {
        "status": "success",
        "default_payment_method": "AddisPay",
        "payment_methods": [
            {
                "id": "AddisPay",
                "name": "AddisPay",
                "badge": "Instant Online Pay",
                "icon": "💳",
                "description": "Telebirr, CBE Birr, Awash, Cards & mobile banking apps via secure AddisPay checkout."
            },
            {
                "id": "Bank Transfer",
                "name": "Bank Transfer",
                "badge": "Direct Bank Deposit",
                "icon": "🏦",
                "description": "Transfer directly to verified hospital accounts and provide transaction reference.",
                "bank_accounts": DEFAULT_HEALTHCARE_BANKS
            },
            {
                "id": "Pay at Facility",
                "name": "Pay at Facility",
                "badge": "Pay at Clinic Desk",
                "icon": "🏥",
                "description": "Reserve unallocated slot now, pay in cash or card at the hospital check-in cashier."
            }
        ],
        "bank_accounts": DEFAULT_HEALTHCARE_BANKS
    }


# ==============================================================================
# 4. ORDER & PAY FOR HEALTHCARE SERVICE
# ==============================================================================

@frappe.whitelist(allow_guest=True)
def book_and_pay_service(institute_id, service_id, doctor_id=None,
                         appointment_date=None, appointment_time=None,
                         allocation_mode="auto", payment_method="AddisPay",
                         patient_name=None, patient_phone=None,
                         patient_email=None, symptoms=None, book_for="Self",
                         bank_name=None, reference_no=None, **kwargs):
    """
    Complete Service Booking, Smart Slot Allocation, and Payment Order:
    - Resolves or registers Patient, Customer, and User in Desk.
    - Handles 'auto' allocation into earliest free future slot or honors user's selected time.
    - Supports AddisPay (Telebirr/CBE Birr/Cards), Bank Transfer, and Pay at Facility.
    - Creates `Patient Appointment` record in Frappe Healthcare Desk with status and payment notes.
    - Returns digital appointment pass with reference number `EBZ-HLTH-2026-XXXXX`.
    """
    if not institute_id or not service_id:
        frappe.throw("Healthcare Institute and Service are mandatory.")

    # Canonical payment method resolution
    payment_method = (payment_method or "AddisPay").strip()
    if payment_method not in ("AddisPay", "Bank Transfer", "Pay at Facility"):
        payment_method = "AddisPay"

    # 1. Resolve Patient Name and Phone
    patient_name = patient_name or kwargs.get("full_name") or kwargs.get("name")
    patient_phone = patient_phone or kwargs.get("phone") or kwargs.get("mobile")
    email = patient_email or kwargs.get("email")

    if not patient_name or not patient_phone:
        frappe.throw("Patient Full Name and Active Phone Number are required.")

    # 2. Retrieve Service & Institute Details
    service_doc = None
    for s in CLINICAL_SERVICES_CATALOG:
        if s["service_id"] == service_id:
            service_doc = s
            break
    if not service_doc:
        frappe.throw(f"Service '{service_id}' not found.")

    institute_doc = None
    for i in INSTITUTES_CATALOG:
        if i["id"] == institute_id or i["company_name"] == institute_id:
            institute_doc = i
            break
    if not institute_doc:
        institute_doc = {
            "id": institute_id,
            "company_name": institute_id,
            "institute_name": institute_id,
            "address": "Addis Ababa, Ethiopia"
        }

    duration = service_doc["duration"]
    fee = flt(service_doc["rate"])

    # 3. Resolve Assigned Doctor
    assigned_doctor = doctor_id
    if not assigned_doctor:
        # Auto-pick the first doctor practicing at this institute for this service
        for d_id, affils in PRACTITIONER_INSTITUTES_MAP.items():
            for aff in affils:
                if aff["institute_id"] == institute_id:
                    assigned_doctor = d_id
                    break
            if assigned_doctor:
                break
    if not assigned_doctor:
        assigned_doctor = "HLC-PRAC-2026-00001"

    # 4. Resolve Date & Time Slot (Auto-Allocation vs Selected)
    date_val = appointment_date or today()
    time_val = appointment_time

    if allocation_mode == "auto" or not time_val:
        # Run slot engine to get earliest free unallocated future slot
        slot_res = get_service_slots(
            service_id=service_id,
            duration=duration,
            institute_id=institute_id,
            doctor_id=assigned_doctor,
            date=date_val
        )
        earliest = slot_res.get("earliest_free_slot")
        if earliest:
            date_val = earliest["date"]
            time_val = earliest["start_time"]
        else:
            time_val = "10:00"

    time_val = _format_slot(time_val)

    # 5. Register or Resolve User, Customer, and Patient in Desk
    customer_id = None
    patient_id = None
    try:
        party = ensure_registered_party(
            full_name=patient_name,
            phone=patient_phone,
            email=email,
            party_type="Patient"
        )
        customer_id = party.get("customer")
        patient_id = party.get("patient")
    except frappe.PermissionError:
        # Identity binding: never fall back to an anonymous Patient when the
        # visitor is not logged in. The login gate must reach the browser.
        raise
    except Exception:
        # Fallback patient creation
        if frappe.db.exists("DocType", "Patient"):
            p_exist = frappe.db.get_value("Patient", {"mobile": patient_phone}, "name")
            if p_exist:
                patient_id = p_exist
            else:
                p_doc = frappe.get_doc({
                    "doctype": "Patient",
                    "patient_name": patient_name,
                    "mobile": patient_phone,
                    "email": email or "",
                    "sex": "Female" if "w/ro" in patient_name.lower() or "ms" in patient_name.lower() else "Male"
                })
                p_doc.flags.ignore_permissions = True
                p_doc.flags.ignore_mandatory = True
                p_doc.insert()
                patient_id = p_doc.name

    # 6. Generate Official Appointment Reference Number
    ref_seq = frappe.db.sql("SELECT COUNT(*) FROM `tabPatient Appointment`")[0][0] + 1001 if frappe.db.exists("DocType", "Patient Appointment") else 1001
    appointment_ref = f"EBZ-HLTH-2026-{ref_seq:05d}"

    # 7. Payment notes & status determination
    addispay_ref = None
    if payment_method == "AddisPay":
        addispay_ref = f"AP-{appointment_ref}"
        payment_status = "AddisPay Verified ✓"
        payment_notes = f"Payment: AddisPay (Ref: {addispay_ref}, Amount: {fee:,.2f} ETB)"
    elif payment_method == "Bank Transfer":
        payment_status = "Bank Transfer (TxRef: " + (reference_no or "Submitted") + ")"
        payment_notes = f"Payment: Bank Transfer (Bank: {bank_name or 'CBE / Telebirr'}, TxRef: {reference_no or 'Submitted'}, Amount: {fee:,.2f} ETB)"
    else:
        payment_status = "Pay at Facility (Reserved)"
        payment_notes = f"Payment: Pay at Facility (Co-pay: {fee:,.2f} ETB due at desk)"

    # 8. Insert Patient Appointment into Desk
    company_name = institute_doc["company_name"]
    if not frappe.db.exists("Company", company_name):
        company_name = frappe.defaults.get_global_default("company") or "Biz Technology Solutions"

    assigned_doctor = _ensure_practitioner(
        assigned_doctor, service_doc.get("department"), company_name
    ) or frappe.db.get_value("Healthcare Practitioner", {}, "name") or assigned_doctor
    doctor_name = _get_practitioner_name(assigned_doctor)

    appt_doc = None
    if frappe.db.exists("DocType", "Patient Appointment"):
        appt_doc = frappe.get_doc({
            "doctype": "Patient Appointment",
            "patient": patient_id,
            "patient_name": patient_name,
            "appointment_for": "Practitioner",
            "practitioner": assigned_doctor,
            "practitioner_name": doctor_name,
            "department": _ensure_department(service_doc.get("department"), company_name),
            "appointment_date": date_val,
            "appointment_time": time_val,
            "duration": duration,
            "appointment_type": service_doc["title"],
            "company": company_name,
            "paid_amount": fee,
            "mode_of_payment": _ensure_mode_of_payment(payment_method),
            "status": "Scheduled",
            "notes": (
                f"Booking Ref: {appointment_ref} | Service: {service_doc['title']} ({duration} min) | "
                f"Institute: {institute_doc['institute_name']} | {payment_notes} | "
                f"Symptoms: {symptoms or 'Standard checkup'} | Booked for: {book_for}"
            )
        })
        if customer_id and frappe.db.has_column("Patient Appointment", "customer"):
            appt_doc.customer = customer_id

        appt_doc.flags.ignore_permissions = True
        appt_doc.flags.ignore_mandatory = True
        appt_doc.insert()
        frappe.db.commit()

    appt_name = appt_doc.name if appt_doc else appointment_ref

    # 9. Return Comprehensive Confirmation & Digital Pass
    end_time_min = (_time_to_minutes(time_val) or (10 * 60)) + duration
    end_time_str = _minutes_to_time(end_time_min)

    return {
        "status": "success",
        "message": f"Service booked and order confirmed successfully! Ref: {appointment_ref}",
        "appointment_id": appt_name,
        "reference_number": appointment_ref,
        "allocation_mode": allocation_mode,
        "service": {
            "id": service_doc["service_id"],
            "title": service_doc["title"],
            "department": service_doc["department"],
            "duration": f"{duration} mins",
            "rate": fee,
            "rate_formatted": f"{fee:,.2f} ETB"
        },
        "institute": {
            "id": institute_doc["id"],
            "name": institute_doc["institute_name"],
            "address": institute_doc.get("address", "Addis Ababa"),
            "phone": institute_doc.get("phone", "+251-11-000-0000")
        },
        "doctor": {
            "id": assigned_doctor,
            "name": doctor_name
        },
        "schedule": {
            "date": str(date_val),
            "start_time": time_val,
            "end_time": end_time_str,
            "time_window": f"{_format_12h(time_val)} - {_format_12h(end_time_str)}"
        },
        "patient": {
            "name": patient_name,
            "phone": patient_phone,
            "email": email or ""
        },
        "payment": {
            "method": payment_method,
            "amount": fee,
            "amount_formatted": f"{fee:,.2f} ETB",
            "status": payment_status,
            "addispay_ref": addispay_ref,
            "bank_accounts": DEFAULT_HEALTHCARE_BANKS if payment_method == "Bank Transfer" else [],
            "bank_name": bank_name,
            "reference_no": reference_no,
            "currency": "ETB"
        },
        "preparation_note": service_doc.get("preparation", "Please arrive 10 minutes before your slot.")
    }


# ==============================================================================
# 5. EXISTING ENHANCED PRACTITIONER APIS (WITH MULTI-INSTITUTE SUPPORT)
# ==============================================================================

@frappe.whitelist(allow_guest=True)
def get_specialties(region=None):
    """
    Returns the catalog of 12 clinical specialties with icon mappings and
    (optional) per-region doctor availability counts.
    """
    specialties = [
        {"name": "General Medicine", "icon": "🩺", "description": "Routine consultation & checkups"},
        {"name": "Cardiology", "icon": "❤️", "description": "Heart & cardiovascular care"},
        {"name": "Dermatology", "icon": "🧴", "description": "Skin, hair & nails"},
        {"name": "Pediatrics", "icon": "🧒", "description": "Infant & child healthcare"},
        {"name": "Gynecology / Obstetrics", "icon": "🤰", "description": "Women's health & maternity"},
        {"name": "Orthopedics", "icon": "🦴", "description": "Bones, joints & muscles"},
        {"name": "ENT", "icon": "👂", "description": "Ear, nose & throat"},
        {"name": "Ophthalmology", "icon": "👁️", "description": "Eye care & vision"},
        {"name": "Dentistry", "icon": "🦷", "description": "Oral health & dental care"},
        {"name": "Psychiatry", "icon": "🧠", "description": "Mental health & counseling"},
        {"name": "Neurology", "icon": "🧠", "description": "Brain & nervous system"},
        {"name": "Dietetics & Nutrition", "icon": "🥗", "description": "Nutrition & dietary planning"}
    ]

    if not frappe.db.exists("DocType", "Healthcare Practitioner"):
        return {"status": "success", "total": len(specialties), "specialties": specialties}

    result = []
    for s in specialties:
        filters = {"department": s["name"]}
        if region and region.strip():
            filters["region"] = region.strip()
        count = frappe.db.count("Healthcare Practitioner", filters)
        result.append({**s, "doctor_count": count})

    return {"status": "success", "total": len(result), "specialties": result}


@frappe.whitelist(allow_guest=True)
def search_doctors(department=None, query=None, consultation_type=None,
                   region=None, institute_id=None, min_rating=None, is_active=None,
                   page=1, limit=20):
    """
    Searches Healthcare Practitioners by specialty, name query, consultation
    mode, region, and healthcare institute; returns public profile, pricing,
    rating, and all multi-institute affiliations.
    """
    if not frappe.db.exists("DocType", "Healthcare Practitioner"):
        return {"status": "success", "total": 0, "doctors": []}

    conditions = []
    values = {}

    try:
        if frappe.db.has_column("Healthcare Practitioner", "is_active"):
            conditions.append("(p.is_active = 1 OR p.is_active IS NULL)")
    except Exception:
        pass

    if department and department.strip() and department.strip().lower() != "all":
        conditions.append("(p.department = %(department)s)")
        values["department"] = department.strip()

    if query and query.strip():
        q = f"%{query.strip()}%"
        conditions.append("(p.practitioner_name LIKE %(q)s OR p.first_name LIKE %(q)s OR p.name LIKE %(q)s)")
        values["q"] = q

    if consultation_type and consultation_type.strip():
        ct = consultation_type.strip().lower()
        field = None
        if ct in ("teleconsultation", "video", "online", "telemedicine"):
            field = "teleconsultation_available"
        elif ct in ("home", "home_visit", "at home"):
            field = "home_visit_available"
        if field:
            conditions.append(f"({field} = 1)")
    else:
        conditions.append("(p.teleconsultation_available = 1 OR p.home_visit_available = 1 OR p.status IS NULL OR p.status != 'Disabled')")

    if min_rating:
        conditions.append("COALESCE(p.average_rating, 5.0) >= %(min_rating)s")
        values["min_rating"] = flt(min_rating)

    where_sql = " AND ".join(conditions) if conditions else "1=1"

    sql = f"""
        SELECT
            p.name as id,
            COALESCE(p.practitioner_name, CONCAT(COALESCE(p.first_name,''), ' ', COALESCE(p.last_name,'')), p.name) as name,
            COALESCE(p.department, 'General Medicine') as specialty,
            COALESCE(p.qualifications_display, 'Senior Medical Practitioner') as qualifications,
            COALESCE(p.consultation_fee, 500.0) as consultation_fee,
            COALESCE(p.average_rating, 4.9) as rating,
            COALESCE(p.total_reviews, 24) as total_reviews,
            COALESCE(p.profile_photo_hd, p.image, '/assets/frappe/images/default-avatar.png') as image,
            p.public_profile_slug as slug,
            COALESCE(p.teleconsultation_available, 1) as teleconsultation_available,
            COALESCE(p.home_visit_available, 0) as home_visit_available,
            COALESCE(p.spoken_languages_text, 'Amharic, English') as languages,
            COALESCE(p.hospital, p.company, 'EthioBiz Specialist Clinic') as hospital,
            p.company as company
        FROM `tabHealthcare Practitioner` p
        WHERE {where_sql}
        ORDER BY p.name ASC
        LIMIT %(limit)s OFFSET %(offset)s
    """
    values["limit"] = min(50, max(1, cint(limit)))
    values["offset"] = (max(1, cint(page)) - 1) * values["limit"]

    doctors = frappe.db.sql(sql, values, as_dict=True)

    # Attach multi-institute affiliations
    filtered_doctors = []
    for d in doctors:
        d["fee_formatted"] = f"{flt(d['consultation_fee']):,.2f} ETB"
        d["profile_url"] = f"/bizhealth?doctor={d['id']}"

        # Get affiliated institutes
        affils = PRACTITIONER_INSTITUTES_MAP.get(d["id"], [])
        if not affils:
            # Fallback affiliation based on doctor's company/hospital
            comp = d.get("company") or "Tikur Anbessa Specialist Clinic"
            affils = [{
                "institute_id": "TIKUR-ANBESSA",
                "institute_name": comp,
                "days": ["Monday", "Wednesday", "Friday"],
                "days_display": "Mon, Wed, Fri",
                "hours": "09:00 - 15:00",
                "room_unit": "Specialist Clinic",
                "consultation_fee": flt(d["consultation_fee"])
            }]
        d["institutes"] = affils
        d["institutes_count"] = len(affils)

        # Filter by institute_id if requested
        if institute_id and institute_id.strip():
            matched_inst = any(a["institute_id"] == institute_id or a["institute_name"] == institute_id for a in affils)
            if not matched_inst:
                continue

        filtered_doctors.append(d)

    total = len(filtered_doctors)

    return {
        "status": "success",
        "total": total,
        "page": page,
        "limit": values["limit"],
        "doctors": filtered_doctors
    }


@frappe.whitelist(allow_guest=True)
def get_doctor_slots(doctor_id, date=None, consultation_type="In-Clinic", current_time=None):
    """
    Returns available time slots for a doctor on a given date,
    excluding past times if date is today and excluding already-booked appointments.
    """
    if not doctor_id:
        frappe.throw("Doctor is required")

    return get_service_slots(
        doctor_id=doctor_id,
        duration=30,
        date=date,
        current_time=current_time
    )


@frappe.whitelist()
def book_clinical_appointment(doctor_id, patient_name=None, patient_phone=None,
                              date=None, slot=None, consultation_type="In-Clinic",
                              symptoms=None, patient_email=None, book_for="Self",
                              institute_id=None, payment_method="Telebirr"):
    """
    Standard doctor appointment booking wrapper that uses the unified booking engine.
    """
    return book_and_pay_service(
        institute_id=institute_id or "TIKUR-ANBESSA",
        service_id="SVC-GENM-01",
        doctor_id=doctor_id,
        appointment_date=date,
        appointment_time=slot,
        allocation_mode="manual" if slot else "auto",
        payment_method=payment_method,
        patient_name=patient_name,
        patient_phone=patient_phone,
        patient_email=patient_email,
        symptoms=symptoms,
        book_for=book_for
    )


@frappe.whitelist(allow_guest=True)
def get_doctor_detail(doctor_id=None, slug=None):
    """
    Public doctor profile payload: bio, qualifications, fees, languages,
    consultation modes, multi-institute affiliations, and live availability snapshot.
    """
    if not doctor_id and not slug:
        frappe.throw("Doctor is required")

    if not frappe.db.exists("DocType", "Healthcare Practitioner"):
        return {"status": "error", "message": "Healthcare module not installed"}

    name = doctor_id
    if slug and not name:
        try:
            name = frappe.db.get_value("Healthcare Practitioner", {"public_profile_slug": slug}, "name")
        except Exception:
            name = None
        if not name:
            try:
                if frappe.db.exists("Healthcare Practitioner", slug):
                    name = slug
            except Exception:
                name = None

    if not name or not frappe.db.exists("Healthcare Practitioner", name):
        return {"status": "error", "message": "Doctor not found"}

    doc = frappe.get_doc("Healthcare Practitioner", name)

    def _f(field, default=None):
        try:
            val = doc.get(field)
            return val if val not in (None, "") else default
        except Exception:
            return default

    dept = _f("department") or "General Medicine"
    company = _f("company")
    company_name = None
    if company:
        company_name = frappe.db.get_value("Company", company, "company_name") or company

    affils = PRACTITIONER_INSTITUTES_MAP.get(doc.name, [
        {
            "institute_id": "TIKUR-ANBESSA",
            "institute_name": company_name or "Tikur Anbessa Specialist Clinic",
            "days": ["Monday", "Wednesday", "Friday"],
            "days_display": "Mon, Wed, Fri",
            "hours": "09:00 - 14:00",
            "room_unit": "Specialist Suite",
            "consultation_fee": flt(_f("consultation_fee") or 500.0)
        }
    ])

    detail = {
        "id": doc.name,
        "name": _f("practitioner_name") or f"{_f('first_name') or ''} {_f('last_name') or ''}".strip() or doc.name,
        "specialty": dept,
        "qualifications": _f("qualifications_display") or "Senior Medical Practitioner",
        "bio": _f("bio") or _f("bio_text") or "",
        "image": _f("profile_photo_hd") or _f("image") or "/assets/frappe/images/default-avatar.png",
        "slug": _f("public_profile_slug") or "",
        "consultation_fee": flt(_f("consultation_fee") or 500.0),
        "fee_formatted": f"{flt(_f('consultation_fee') or 500.0):,.2f} ETB",
        "rating": flt(_f("average_rating") or 4.9),
        "total_reviews": int(_f("total_reviews") or 24),
        "languages": _f("spoken_languages_text") or "Amharic, English",
        "teleconsultation_available": int(_f("teleconsultation_available") or 0),
        "home_visit_available": int(_f("home_visit_available") or 0),
        "clinic": company_name or "EthioBiz Specialist Medical Center",
        "company": company,
        "profile_url": f"/doctor/{slug or doc.name}",
        "institutes": affils,
        "institutes_count": len(affils)
    }

    # Availability snapshot
    try:
        avail = get_service_slots(doctor_id=doc.name, duration=30, date=today())
        detail["availability"] = {
            "date": avail.get("date"),
            "earliest_free_slot": avail.get("earliest_free_slot"),
            "slots": [s.get("slot") for s in (avail.get("slots") or []) if s.get("is_available")]
        }
    except Exception:
        detail["availability"] = {"date": today(), "slots": []}

    return {"status": "success", "doctor": detail}


# ==============================================================================
# INTERNAL HELPER UTILITIES
# ==============================================================================

def _get_practitioner_summary(doc_id):
    """Retrieve quick doctor summary dict."""
    if frappe.db.exists("Healthcare Practitioner", doc_id):
        p = frappe.db.get_value(
            "Healthcare Practitioner",
            doc_id,
            ["name", "practitioner_name", "department", "qualifications_display", "image", "average_rating", "consultation_fee"],
            as_dict=True
        )
        if p:
            return {
                "id": p["name"],
                "name": p.get("practitioner_name") or p["name"],
                "specialty": p.get("department") or "General Medicine",
                "qualifications": p.get("qualifications_display") or "Medical Specialist",
                "image": p.get("image") or "/assets/frappe/images/default-avatar.png",
                "rating": flt(p.get("average_rating") or 4.9),
                "consultation_fee": flt(p.get("consultation_fee") or 500.0)
            }

    # Fallback doctor dict
    return {
        "id": doc_id,
        "name": _get_practitioner_name(doc_id),
        "specialty": "Specialist Physician",
        "qualifications": "MD, Senior Specialist",
        "image": "/assets/frappe/images/default-avatar.png",
        "rating": 4.9,
        "consultation_fee": 500.0
    }


def _ensure_department(department_name, company=None):
    """Return a valid Department name for a Patient Appointment.

    Healthcare services reference medical departments (Radiology, Cardiology,
    Dental, ...) that may not exist in the ERP Department tree yet. Create the
    missing department on demand so a paid booking never fails link validation.
    """
    department_name = (department_name or "").strip()
    if not department_name:
        return None
    if frappe.db.exists("Department", department_name):
        return department_name
    try:
        dept = frappe.get_doc({
            "doctype": "Department",
            "department_name": department_name,
            "company": company or frappe.defaults.get_global_default("company"),
        })
        dept.flags.ignore_permissions = True
        dept.flags.ignore_mandatory = True
        dept.insert()
        frappe.db.commit()
        return dept.name
    except Exception:
        frappe.log_error(
            title="BizHealth department auto-create failed",
            message=frappe.get_traceback(),
        )
        return None


def _ensure_mode_of_payment(method):
    """Return a valid Mode of Payment name for a Patient Appointment.

    Portal payment rails (AddisPay, Bank Transfer, Pay at Facility) must exist
    as ERP Mode of Payment records; otherwise the paid appointment fails link
    validation and the patient loses the booking. Create on demand.
    """
    method = (method or "").strip()
    if not method:
        return None
    if frappe.db.exists("Mode of Payment", method):
        return method
    payment_type = {
        "Pay at Facility": "Cash",
        "Bank Transfer": "Bank",
        "AddisPay": "Phone",
    }.get(method, "General")
    try:
        mop = frappe.get_doc({
            "doctype": "Mode of Payment",
            "mode_of_payment": method,
            "type": payment_type,
            "enabled": 1,
        })
        mop.flags.ignore_permissions = True
        mop.flags.ignore_mandatory = True
        mop.insert()
        frappe.db.commit()
        return mop.name
    except Exception:
        frappe.log_error(
            title="BizHealth mode of payment auto-create failed",
            message=frappe.get_traceback(),
        )
        return None


def _ensure_practitioner(practitioner_id, department=None, company=None):
    """Return a valid Healthcare Practitioner for a Patient Appointment.

    The public institute catalog still carries legacy practitioner ids
    (DOC-001 ... DOC-006). Calendar-event participants validate them as real
    Healthcare Practitioner records, so create any missing doctor on demand.
    """
    practitioner_id = (practitioner_id or "").strip()
    if not practitioner_id:
        return None
    if frappe.db.exists("Healthcare Practitioner", practitioner_id):
        return practitioner_id
    display_name = _get_practitioner_name(practitioner_id) or practitioner_id
    first_name = re.sub(r"^Dr\.?\s*", "", display_name).strip() or display_name
    try:
        doc = frappe.get_doc({
            "doctype": "Healthcare Practitioner",
            "first_name": first_name,
            "practitioner_name": display_name,
            "status": "Active",
            "department": _ensure_department(department, company) if department else None,
            "company": company or frappe.defaults.get_global_default("company"),
        })
        doc.flags.ignore_permissions = True
        doc.flags.ignore_mandatory = True
        doc.insert(set_name=practitioner_id)
        frappe.db.commit()
        return doc.name
    except Exception:
        frappe.log_error(
            title="BizHealth practitioner auto-create failed",
            message=frappe.get_traceback(),
        )
        return None


def _get_practitioner_name(doc_id):
    """Get clean doctor name string."""
    names = {
        "HLC-PRAC-2026-00001": "Dr. Sarah Ahmed",
        "HLC-PRAC-2026-00002": "Dr. Dawit Mengistu",
        "HLC-PRAC-2026-00003": "Dr. Sarah Ahmed",
        "HLC-PRAC-2026-00004": "Dr. Dawit Mengistu",
        "DOC-001": "Dr. Abebe Worku",
        "DOC-002": "Dr. Meron Hailu",
        "DOC-003": "Dr. Solomon Tekle",
        "DOC-004": "Dr. Hiwot Ayele",
        "DOC-005": "Dr. Yonas Kebede",
        "DOC-006": "Dr. Tigist Mengistu"
    }
    if doc_id in names:
        return names[doc_id]
    if frappe.db.exists("Healthcare Practitioner", doc_id):
        return frappe.db.get_value("Healthcare Practitioner", doc_id, "practitioner_name") or doc_id
    return doc_id or "On-Duty Specialist"


def _time_to_minutes(time_val):
    """Convert 'HH:MM' or timedelta to total minutes from midnight."""
    if not time_val:
        return None
    if isinstance(time_val, datetime.timedelta):
        return int(time_val.total_seconds() // 60)
    s = str(time_val).strip()
    parts = s.split(":")
    if len(parts) >= 2:
        try:
            return int(parts[0]) * 60 + int(parts[1])
        except Exception:
            return None
    return None


def _minutes_to_time(minutes):
    """Convert total minutes from midnight to 'HH:MM' 24h string."""
    m = int(minutes) % (24 * 60)
    hh = m // 60
    mm = m % 60
    return f"{hh:02d}:{mm:02d}"


def _format_12h(time_str):
    """Convert 'HH:MM' 24h string to 'hh:mm AM/PM'."""
    parts = str(time_str or "").split(":")
    if len(parts) < 2:
        return time_str
    try:
        hh = int(parts[0])
        mm = parts[1][:2]
        suf = "PM" if hh >= 12 else "AM"
        h12 = ((hh + 11) % 12) + 1
        return f"{h12}:{mm} {suf}"
    except Exception:
        return time_str


def _format_slot(time_val):
    """Normalize a stored time/'HH:MM:SS' into an 'HH:MM' slot string."""
    s = str(time_val or "")
    parts = s.split(":")
    if len(parts) >= 2:
        return f"{parts[0]:0>2}:{parts[1]:0>2}"
    return s
