"""
Knowledge Base search utilities.
Loads and searches the crop disease knowledge base CSV file.
"""

import pandas as pd
import re
from typing import Optional, Dict, List
from rapidfuzz import process, fuzz

# Global KB cache
_kb_cache = None

def load_kb(kb_path: str) -> pd.DataFrame:
    """
    Load knowledge base from CSV file.
    
    Args:
        kb_path: Path to the CSV file
    
    Returns:
        DataFrame with crop disease knowledge base
    """
    global _kb_cache
    
    if _kb_cache is not None:
        return _kb_cache
    
    try:
        kb = pd.read_csv(kb_path)
        # Normalize column names
        kb.columns = [c.strip().lower() for c in kb.columns]
        
        # Ensure required columns exist
        required_cols = ['crop', 'disease', 'symptoms', 'solution']
        for col in required_cols:
            if col not in kb.columns:
                raise ValueError(f"Knowledge base missing required column: {col}")
        
        _kb_cache = kb
        return kb
    except Exception as e:
        raise Exception(f"Failed to load knowledge base: {e}")

def detect_crop_name(query: str, kb: pd.DataFrame) -> Optional[str]:
    """
    Detect crop name from query using keyword matching.
    Improved to avoid false positives.
    
    Args:
        query: User query text (should be in English)
        kb: Knowledge base DataFrame
    
    Returns:
        Crop name if found, None otherwise
    """
    if not query or not query.strip():
        return None
    
    query_lower = query.lower()
    crops = kb['crop'].dropna().unique()
    crops_lower = [str(c).lower() for c in crops]
    
    # Create word list from query
    query_words = set(query_lower.split())
    
    # First: Check for exact crop name match (whole word)
    for crop, crop_l in zip(crops, crops_lower):
        # Check if crop name appears as a whole word (not just substring)
        crop_words = crop_l.split()
        
        # If crop is a single word, check for exact match
        if len(crop_words) == 1:
            if crop_words[0] in query_words:
                return str(crop)
        else:
            # Multi-word crop - check if all words are present
            if all(word in query_words for word in crop_words):
                return str(crop)
    
    # Second: Check for substring match (but require minimum length)
    for crop, crop_l in zip(crops, crops_lower):
        # Only match if crop name is at least 4 characters (avoid false positives)
        if len(crop_l) >= 4 and crop_l in query_lower:
            # Make sure it's not just matching part of another word
            # Check if surrounded by word boundaries or spaces
            pattern = r'\b' + re.escape(crop_l) + r'\b'
            if re.search(pattern, query_lower):
                return str(crop)
    
    # Third: Fuzzy match with higher threshold (only if exact fails)
    match = process.extractOne(query_lower, crops_lower, scorer=fuzz.WRatio, score_cutoff=70)
    if match:
        # Verify the match is reasonable
        matched_crop = crops[crops_lower.index(match[0])]
        matched_crop_lower = str(matched_crop).lower()
        
        # Check if matched crop name appears as substring with word boundaries
        pattern = r'\b' + re.escape(matched_crop_lower) + r'\b'
        if re.search(pattern, query_lower):
            return str(matched_crop)
    
    return None

def search_kb(query: str, crop_name: Optional[str] = None, kb: pd.DataFrame = None) -> Dict:
    """
    Search knowledge base for relevant diseases/symptoms.
    
    Args:
        query: User query text (should be in English)
        crop_name: Optional crop name to filter results
        kb: Knowledge base DataFrame (will load if not provided)
    
    Returns:
        Dictionary with search results containing:
        - 'crop': Crop name
        - 'matches': List of matching rows with disease, symptoms, solution
        - 'all_symptoms': List of all symptoms for the crop (if crop found but no specific match)
    """
    if kb is None:
        raise ValueError("Knowledge base not provided. Call load_kb() first.")
    
    results = {
        'crop': crop_name,
        'matches': [],
        'all_symptoms': []
    }
    
    # If crop name provided, filter by crop
    if crop_name:
        crop_rows = kb[kb['crop'].str.lower() == crop_name.lower()]
    else:
        crop_rows = kb.copy()
    
    if crop_rows.empty:
        return results
    
    query_lower = query.lower()
    
    # Search for matching symptoms and diseases
    for _, row in crop_rows.iterrows():
        disease = str(row.get('disease', ''))
        symptoms = str(row.get('symptoms', ''))
        solution = str(row.get('solution', ''))
        
        # Check if query matches symptoms or disease
        symptoms_lower = symptoms.lower()
        disease_lower = disease.lower()
        
        match_score = 0
        if query_lower in symptoms_lower or symptoms_lower in query_lower:
            match_score += 100
        if query_lower in disease_lower or disease_lower in query_lower:
            match_score += 50
        
        # Fuzzy matching for symptoms
        if not match_score:
            symptom_list = [s.strip() for s in symptoms.split(',')]
            for symptom in symptom_list:
                if symptom.strip():
                    score = fuzz.partial_ratio(query_lower, symptom.lower())
                    if score > 60:
                        match_score += score / 2
                        break
        
        if match_score > 30:
            results['matches'].append({
                'disease': disease,
                'symptoms': symptoms,
                'solution': solution,
                'score': match_score
            })
    
    # Sort by score
    results['matches'].sort(key=lambda x: x['score'], reverse=True)
    
    # Collect all symptoms for the crop (for suggestions if no match)
    if crop_name and not results['matches']:
        all_symptoms = set()
        for _, row in crop_rows.iterrows():
            symptoms = str(row.get('symptoms', ''))
            for s in symptoms.split(','):
                s_clean = s.strip()
                if s_clean:
                    all_symptoms.add(s_clean)
        results['all_symptoms'] = sorted(list(all_symptoms))
    
    return results
