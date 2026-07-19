import re
import logging
from typing import List, Optional, Any
from pydantic import BaseModel

import spacy
from spacy.cli import download

logger = logging.getLogger(__name__)

class ExtractedEntities(BaseModel):
    equipment: List[str] = []
    fault: Optional[str] = None
    temperature: Optional[str] = None
    pressure: Optional[str] = None
    date: Optional[str] = None
    engineer: Optional[str] = None
    technician: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    maintenance_action: Optional[str] = None

# Global spacy model to avoid reloading
_nlp = None

def load_spacy():
    global _nlp
    if _nlp is not None:
        return _nlp
        
    try:
        _nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("spaCy model 'en_core_web_sm' not found. Downloading now...")
        # Actually download it
        download("en_core_web_sm")
        _nlp = spacy.load("en_core_web_sm")
        
    return _nlp

def extract_entities(text: str) -> ExtractedEntities:
    """
    Extract structured entities from text using Regex and spaCy.
    """
    if not text:
        return ExtractedEntities()
        
    entities = ExtractedEntities()
    
    # 1. REGEX EXTRACTIONS
    
    # Equipment (e.g. Pump P-101)
    eq_pattern = r'(?i)\b(?:pump|valve|motor|compressor|tank|generator|turbine)\s+[A-Z0-9-]+\b'
    equipment_matches = re.findall(eq_pattern, text)
    if equipment_matches:
        # Title case to normalize
        entities.equipment = list(set([e.title() for e in equipment_matches]))
        
    # Temperature (e.g. 100 °C, 250F)
    temp_pattern = r'\b\d+(?:\.\d+)?\s*(?:°C|°F|C|F)\b'
    temp_match = re.search(temp_pattern, text)
    if temp_match:
        entities.temperature = temp_match.group(0)
        
    # Pressure (e.g. 200 psi, 1.5 bar)
    pres_pattern = r'\b\d+(?:\.\d+)?\s*(?:bar|psi|kPa|MPa)\b'
    pres_match = re.search(pres_pattern, text, re.IGNORECASE)
    if pres_match:
        entities.pressure = pres_match.group(0).lower()
        
    # Serial Number (e.g. S/N 12345-ABC)
    sn_pattern = r'(?i)\b(?:s/n|serial no\.?|serial number)\s*[:-]?\s*([A-Z0-9-]+)\b'
    sn_match = re.search(sn_pattern, text)
    if sn_match:
        entities.serial_number = sn_match.group(1).upper()
        
    # Dates (e.g. 2023-10-25, 25/10/2023)
    date_pattern = r'\b(?:\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})\b'
    date_match = re.search(date_pattern, text)
    if date_match:
        entities.date = date_match.group(0)

    # Heuristics for Fault and Maintenance Action
    fault_pattern = r'(?i)\b(?:cause|fault|failure|issue|problem)[s]?\s*[:-]\s*([^.\n]+)'
    fault_match = re.search(fault_pattern, text)
    if fault_match:
        entities.fault = fault_match.group(1).strip()
        
    action_pattern = r'(?i)\b(?:action|repair|maintenance|resolution)\s*[:-]\s*([^.\n]+)'
    action_match = re.search(action_pattern, text)
    if action_match:
        entities.maintenance_action = action_match.group(1).strip()
        
    # 2. SPACY NER EXTRACTIONS
    nlp = load_spacy()
    doc = nlp(text)
    
    persons = []
    orgs = []
    locs = []
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            persons.append(ent.text)
        elif ent.label_ == "ORG":
            orgs.append(ent.text)
        elif ent.label_ in ("GPE", "LOC"):
            locs.append(ent.text)
            
    # Map to schema fields (heuristic assignments)
    # Filter out obvious false positives (spaCy sometimes misidentifies equipment or headers)
    valid_persons = [p for p in persons if not re.search(r'(?i)(?:valve|pump|motor|compressor|action|maintenance|cause|fault|issue|s/n)', p)]
    if valid_persons:
        # Assign first person to engineer, second to technician if multiple
        entities.engineer = valid_persons[0]
        if len(valid_persons) > 1:
            entities.technician = valid_persons[1]
            
    valid_orgs = [o for o in orgs if not re.search(r'(?i)(?:s/n|serial|valve|pump|motor|inspection|date)', o)]
    for org in valid_orgs:
        # Try to infer manufacturer vs department based on keywords
        if re.search(r'(?i)dept|department|division', org):
            if entities.department is None:
                entities.department = org
        else:
            if entities.manufacturer is None:
                entities.manufacturer = org
            
    if locs:
        entities.location = locs[0]
        
    return entities

def merge_entities(entities_list: List[ExtractedEntities]) -> ExtractedEntities:
    """
    Merge a list of chunk-level entities into a single document-level summary.
    Lists are unioned, singletons take the first non-null value (or could be enhanced to most-frequent).
    """
    merged = ExtractedEntities()
    
    all_equipment = set()
    
    for e in entities_list:
        all_equipment.update(e.equipment)
        
        # Simple first-non-null assignment for singletons
        if merged.fault is None and e.fault: merged.fault = e.fault
        if merged.temperature is None and e.temperature: merged.temperature = e.temperature
        if merged.pressure is None and e.pressure: merged.pressure = e.pressure
        if merged.date is None and e.date: merged.date = e.date
        if merged.engineer is None and e.engineer: merged.engineer = e.engineer
        if merged.technician is None and e.technician: merged.technician = e.technician
        if merged.department is None and e.department: merged.department = e.department
        if merged.location is None and e.location: merged.location = e.location
        if merged.manufacturer is None and e.manufacturer: merged.manufacturer = e.manufacturer
        if merged.serial_number is None and e.serial_number: merged.serial_number = e.serial_number
        if merged.maintenance_action is None and e.maintenance_action: merged.maintenance_action = e.maintenance_action
        
    merged.equipment = list(all_equipment)
    
    return merged
