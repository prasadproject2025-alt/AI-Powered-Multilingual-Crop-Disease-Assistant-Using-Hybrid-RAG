"""
Gemini API integration for generating detailed responses.
Uses Google's Gemini API to provide farmer-friendly explanations.
"""

import os
from typing import Optional, Dict
import google.generativeai as genai

# Global model instance
_gemini_model = None

def initialize_gemini(api_key: Optional[str] = None):
    """
    Initialize Gemini API with API key.
    
    Args:
        api_key: Google Gemini API key. If None, tries:
                 1. Environment variable GEMINI_API_KEY
                 2. config.py file (if exists)
    """
    global _gemini_model
    
    if api_key is None:
        # Try environment variable first
        api_key = os.getenv("GEMINI_API_KEY")
        
        # If not found, try config.py file as fallback
        if not api_key:
            try:
                import config
                if hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY:
                    api_key = config.GEMINI_API_KEY
            except ImportError:
                pass  # config.py doesn't exist, that's okay
    
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Please:\n"
            "1. Set GEMINI_API_KEY environment variable, OR\n"
            "2. Add GEMINI_API_KEY to config.py file, OR\n"
            "3. Pass api_key parameter to initialize_gemini()"
        )
    
    genai.configure(api_key=api_key)
    
    # Try to list available models first
    try:
        available_models = [m.name for m in genai.list_models()]
        print(f"[INFO] Available models: {available_models}")
    except Exception as e:
        print(f"[INFO] Could not list models: {e}")
        available_models = []
    
    # Initialize model - try different model names in priority order
    # Based on available models, try newer versions first
    model_priority = [
        'models/gemini-2.5-flash',           # Latest fast model
        'models/gemini-2.0-flash',           # Stable 2.0 version
        'models/gemini-2.5-pro',             # Latest pro model
        'models/gemini-pro-latest',          # Latest stable pro
        'models/gemini-flash-latest',        # Latest flash
        'gemini-pro',                        # Fallback to old name format
        'models/gemini-pro',                 # With models/ prefix
    ]
    
    for model_name in model_priority:
        try:
            # Check if model is in available list (if we got it)
            if available_models:
                # Extract just the model name without 'models/' prefix for comparison
                model_base = model_name.replace('models/', '')
                available_base = [m.replace('models/', '') for m in available_models]
                if model_base not in available_base and model_name not in available_models:
                    continue  # Skip if not available
            
            # Try with the model name as-is
            _gemini_model = genai.GenerativeModel(model_name)
            # Test if it actually works by creating a test prompt
            test_config = {"max_output_tokens": 5}
            test_response = _gemini_model.generate_content("Hi", generation_config=test_config)
            print(f"[OK] Successfully initialized Gemini model: {model_name}")
            return  # Success, exit function
        except Exception as e:
            error_msg = str(e)
            # Skip silently for "not found" errors, these are expected
            continue
    
    # If all models fail, try without specifying model (use default)
    try:
        _gemini_model = genai.GenerativeModel('gemini-pro')
        print(f"[OK] Using fallback model: gemini-pro")
        return
    except:
        pass
    
    # If still failing, raise error with helpful message
    raise Exception(
        f"Failed to initialize any Gemini model.\n"
        f"Available models: {', '.join(available_models[:5]) if available_models else 'Could not fetch'}\n"
        f"Please check your API key and region access."
    )

def generate_response(
    crop_name: Optional[str],
    query: str,
    kb_results: Dict,
    output_lang: str = "en"
) -> str:
    """
    Generate detailed response using Gemini API based on KB results.
    
    Args:
        crop_name: Name of the crop
        query: Original user query (in English)
        kb_results: Results from search_kb() containing matches
        output_lang: Language code for output (default: "en")
    
    Returns:
        Generated response text
    """
    global _gemini_model
    
    if _gemini_model is None:
        initialize_gemini()
    
    # Build context from KB results
    kb_context = ""
    
    if kb_results.get('matches'):
        kb_context = "Knowledge Base Information:\n\n"
        for i, match in enumerate(kb_results['matches'][:3], 1):  # Top 3 matches
            kb_context += f"Match {i}:\n"
            kb_context += f"Crop: {crop_name or 'Unknown'}\n"
            kb_context += f"Disease: {match['disease']}\n"
            kb_context += f"Symptoms: {match['symptoms']}\n"
            kb_context += f"Solution: {match['solution']}\n\n"
    elif crop_name and kb_results.get('all_symptoms'):
        kb_context = f"For {crop_name}, common symptoms include:\n"
        kb_context += "\n".join([f"- {s}" for s in kb_results['all_symptoms'][:10]])
        kb_context += "\n\nPlease describe which symptom you are observing.\n"
    
    # Handle case where no crop detected
    if not crop_name:
        prompt = f"""You are a friendly agricultural assistant talking to a farmer.

The farmer asked: {query}

You couldn't identify which crop they're asking about, but you want to help them. Respond in a warm, helpful way:

- Acknowledge their question
- Politely ask them to specify the crop name
- Give 2-3 example queries to guide them
- Be encouraging and friendly
- Keep it short and conversational

Write naturally, like you're helping a friend. Use {output_lang if output_lang != 'en' else 'English'} language.

Your response:
"""
    elif not kb_results.get('matches') and not kb_results.get('all_symptoms'):
        prompt = f"""You are a friendly agricultural assistant talking to a farmer.

The farmer asked about: {query}
Crop: {crop_name}

Unfortunately, you don't have specific information about this exact problem in your database. Respond warmly and helpfully:

- Acknowledge their concern
- Apologize that you don't have exact information for this issue
- Ask them to describe the symptoms in more detail
- Suggest they might want to consult local agricultural experts or extension services
- Be encouraging and offer to help with what you do know about {crop_name}

Write naturally and conversationally in {output_lang if output_lang != 'en' else 'English'} language.

Your response:
"""
    else:
        # Build the main prompt with KB context - STRUCTURED BUT FRIENDLY
        prompt = f"""You are a friendly, knowledgeable agricultural assistant talking to a farmer. Help them understand and solve crop disease problems in a clear, structured way while being warm and conversational.

FARMER'S QUESTION: {query}

INFORMATION FROM DATABASE:
{kb_context}

IMPORTANT: You MUST structure your response EXACTLY as follows:

1. **Crop Name** (clearly state which crop)
2. **Disease Name** (the specific disease identified)
3. **Symptoms** (describe what the farmer should look for - be specific and clear)
4. **Solution** (explain treatment step-by-step in user-friendly way - this is the most important part!)

RESPONSE FORMAT REQUIREMENTS:
- Start with a brief warm acknowledgment (1-2 sentences max)
- Then clearly present information using this EXACT structure with these EXACT headings:
  
  **Crop:** [crop name]
  
  **Disease:** [disease name]
  
  **Symptoms:**
  [Describe symptoms clearly - use bullet points or simple sentences. Be specific about what to look for]
  
  **Solution:**
  [This is CRITICAL - explain the solution in a user-friendly, step-by-step way. Break it down so a farmer can easily follow:
  - Explain what to do first
  - What treatments/medicines to use (with clear names)
  - When and how to apply them
  - Any precautions or safety measures
  - Preventive measures for future
  - Make it practical and actionable]

- End with a supportive closing (1 sentence)

IMPORTANT GUIDELINES:
- Use simple, everyday language - avoid technical jargon
- For solutions, be VERY detailed and practical - assume the farmer needs clear step-by-step guidance
- If mentioning chemicals/pesticides, include exact product names from the database
- Explain WHY each step matters
- Be encouraging and supportive
- Make it feel like you're personally helping them

EXAMPLE OF GOOD SOLUTION SECTION:
"**Solution:**
Here's what you can do to treat this:

1. **Immediate Treatment:** For this season, you'll need to use a fungicide. The most effective one for this disease is [product name]. Mix it according to the instructions on the package - usually about 2-3 grams per liter of water. Spray this mixture on all parts of your plants, especially the leaves (both top and bottom). Do this early in the morning or late evening when the sun isn't too strong.

2. **When to Apply:** Start treatment as soon as you notice symptoms. You may need to spray every 7-10 days until the disease is under control. Keep an eye on your plants - if symptoms continue, repeat the treatment.

3. **Safety First:** Always wear gloves, a mask, and long sleeves when handling and spraying chemicals. Keep children and animals away during spraying. Wash your hands thoroughly after handling.

4. **Prevention for Next Season:** When planting next time, choose resistant varieties if available. Also, avoid planting too close together - give plants space for air to circulate. Don't over-water, and be careful with nitrogen fertilizer - too much can make plants more susceptible.

5. **Cultural Practices:** Remove and destroy any infected plant parts. Don't compost them - burn them or throw them away far from your fields. This prevents the disease from spreading."

RESPONSE LANGUAGE: {output_lang if output_lang != 'en' else 'English'}

Now, write a structured, helpful response following the format above:
"""
    
    try:
        # Use generation config for better responses
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        response = _gemini_model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # Extract text from response
        if hasattr(response, 'text'):
            return response.text.strip()
        elif hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content'):
                if hasattr(candidate.content, 'parts') and len(candidate.content.parts) > 0:
                    return candidate.content.parts[0].text.strip()
                elif hasattr(candidate.content, 'text'):
                    return candidate.content.text.strip()
            elif hasattr(candidate, 'text'):
                return candidate.text.strip()
        else:
            result = str(response).strip()
            # Clean up the result if it contains extra formatting
            if result:
                return result
        
        # If we get here, response structure is unexpected
        raise Exception("Unexpected response format from Gemini API")
    
    except Exception as e:
        error_str = str(e)
        # Log error for debugging but don't show to user
        print(f"[ERROR] Gemini API error: {error_str[:200]}")
        
        # Fallback to KB-only conversational response
        if not crop_name:
            return "I couldn't identify which crop you're asking about. Could you please specify the crop name in your question?"
        
        if not kb_results.get('matches'):
            if kb_results.get('all_symptoms'):
                symptoms = "\n".join([f"• {s}" for s in kb_results['all_symptoms'][:10]])
                return f"""I found information about **{crop_name}**, but I need a bit more detail about what you're seeing.

Here are some common symptoms I know about for {crop_name}:
{symptoms}

Can you describe which specific symptoms you're noticing? That will help me give you the best treatment advice."""
            else:
                return f"I don't have specific information about {crop_name} in my database yet. Please try asking about another crop or contact your local agricultural extension office."
        
        # Use the best matching KB entry - format conversationally
        best_match = kb_results['matches'][0]
        
        return f"""Based on what you've described, your **{crop_name}** plants might be affected by **{best_match['disease']}**.

**What to look for:**
{best_match['symptoms']}

**Here's what you can do:**

{best_match['solution']}

---

*If the symptoms don't match exactly or you need more help, feel free to ask me more questions!*"""
