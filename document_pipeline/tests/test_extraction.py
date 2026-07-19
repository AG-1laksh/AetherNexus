import sys
from pathlib import Path

# Add parent dir to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from entity.extractor import extract_entities, merge_entities

def main():
    print("=== Testing Industrial Entity Extraction ===\n")
    
    # Synthetic chunks
    chunk_1 = (
        "Inspection Date: 2023-10-25. "
        "Maintenance was performed on Pump P-101 and Valve V-22 at the Houston facility. "
        "The ambient temperature was measured at 45 °C and system pressure was 200 psi. "
        "Engineer John Smith and Technician Sarah Connor were on site representing Flowserve Corp. "
    )
    
    chunk_2 = (
        "S/N: 98765-XYZ. "
        "Failure Cause: Seal rupture due to excessive vibration. "
        "Maintenance Action: Replaced primary mechanical seal and recalibrated Motor M-34. "
        "The Maintenance Dept will schedule a follow-up next month."
    )
    
    print("--- Extracting Chunk 1 ---")
    res_1 = extract_entities(chunk_1)
    print(res_1.model_dump_json(indent=2))
    
    print("\n--- Extracting Chunk 2 ---")
    res_2 = extract_entities(chunk_2)
    print(res_2.model_dump_json(indent=2))
    
    print("\n--- Merged Document Entities ---")
    merged = merge_entities([res_1, res_2])
    print(merged.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
