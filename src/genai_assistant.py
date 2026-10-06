"""
FinSight AI — Generative AI Financial Assistant Module
Integrates Google Gemini API (default, high speed, cloud) and local Ollama
with comprehensive financial context grounding and reliable rule fallbacks.
"""

import os
import requests
import json
from config.settings import GENAI_CONFIG, CURRENCY_SYMBOL

# Try importing google-genai
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Try importing ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


def get_ai_status() -> dict:
    """Check which AI backend is available (Gemini or Ollama)."""
    api_key = os.getenv("GEMINI_API_KEY") or GENAI_CONFIG.get("gemini_api_key", "")
    if GEMINI_AVAILABLE and api_key and len(api_key.strip()) > 10:
        model = os.getenv("GEMINI_MODEL") or GENAI_CONFIG.get("gemini_model", "gemini-flash-latest")
        return {
            "available": True,
            "provider": "gemini",
            "model": model,
            "message": f"Connected to Google Gemini ({model})"
        }
    
    # Check Ollama fallback
    if OLLAMA_AVAILABLE:
        try:
            host = GENAI_CONFIG.get("host", "http://localhost:11434")
            res = requests.get(f"{host}/api/tags", timeout=2)
            if res.status_code == 200:
                model = GENAI_CONFIG.get("model", "llama3.1")
                return {
                    "available": True,
                    "provider": "ollama",
                    "model": model,
                    "message": f"Connected to local Ollama ({model})"
                }
        except Exception:
            pass

    return {
        "available": False,
        "provider": "none",
        "model": "rule_fallback",
        "message": "AI key not configured. Using rule-based financial reasoning."
    }


def check_ollama_connection() -> bool:
    """Backward compatible check for Ollama or any active AI engine."""
    status = get_ai_status()
    return status.get("available", False)


def build_financial_context(profile: dict, prediction: float = None, anomalies: dict = None, recommendations: list = None) -> str:
    """Construct structured context for LLM grounding so responses are strictly factual."""
    context = ["=== USER FINANCIAL SUMMARY ==="]
    
    if profile:
        monthly_income = profile.get('monthly_income', profile.get('income', 0))
        monthly_budget = profile.get('monthly_budget', profile.get('budget', 0))
        savings_goal = profile.get('financial_goal', profile.get('goal', 'Not specified'))
        avg_monthly = profile.get('avg_monthly_expense', 0)
        volatility = profile.get('expense_volatility', 0)
        
        context.append(f"- Monthly Income: {CURRENCY_SYMBOL}{monthly_income:,.2f}")
        context.append(f"- Monthly Budget: {CURRENCY_SYMBOL}{monthly_budget:,.2f}")
        context.append(f"- Financial Goal: {savings_goal}")
        if avg_monthly > 0:
            context.append(f"- Historical Average Monthly Spending: {CURRENCY_SYMBOL}{avg_monthly:,.2f}")
        if volatility > 0:
            context.append(f"- Monthly Spending Volatility (Std Dev): {CURRENCY_SYMBOL}{volatility:,.2f}")
            
    if prediction is not None:
        context.append(f"- Forecasted Next Month Expenditure: {CURRENCY_SYMBOL}{prediction:,.2f}")
        
    if anomalies and anomalies.get('count', 0) > 0:
        context.append(f"- Flagged Anomalies: {anomalies['count']} unusual transactions detected totaling {CURRENCY_SYMBOL}{anomalies.get('amount', 0):,.2f}")
        if 'recent_anomalies' in anomalies:
            context.append("  Details: " + "; ".join(anomalies['recent_anomalies'][:3]))
            
    if recommendations and len(recommendations) > 0:
        context.append("\n=== ACTIVE RECOMMENDATIONS ===")
        for r in recommendations[:4]:
            context.append(f"- [{r.get('priority', 'MEDIUM')}] {r.get('title', '')}: {r.get('message', '')}")
            
    return "\n".join(context)


def _query_gemini(prompt: str, system_prompt: str = "") -> str:
    """Query Google Gemini API with SSL resilience and automatic model fallback."""
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    api_key = os.getenv("GEMINI_API_KEY") or GENAI_CONFIG.get("gemini_api_key", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
        
    configured_model = os.getenv("GEMINI_MODEL") or GENAI_CONFIG.get("gemini_model", "gemini-flash-latest")
    candidate_models = [configured_model, "gemini-flash-latest", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
    
    # Deduplicate while preserving order
    seen = set()
    models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

    http_opts = types.HttpOptions(client_args={'verify': False})
    client = genai.Client(api_key=api_key, http_options=http_opts)
    
    config = types.GenerateContentConfig(
        system_instruction=system_prompt or "You are FinSight AI, a senior financial consultant. Provide concise, grounded, realistic financial advice using INR (₹). Never invent data not present in the user context.",
        temperature=float(GENAI_CONFIG.get("temperature", 0.3)),
        max_output_tokens=int(GENAI_CONFIG.get("max_tokens", 1000)),
    )
    
    last_err = None
    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            continue
            
    if last_err:
        raise last_err
    return "No response generated by model."


def _query_ollama(prompt: str, system_prompt: str = "") -> str:
    """Query local Ollama instance."""
    client = ollama.Client(host=GENAI_CONFIG.get("host", "http://localhost:11434"))
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})
    
    response = client.chat(
        model=GENAI_CONFIG.get("model", "llama3.1"),
        messages=messages,
        options={
            "temperature": GENAI_CONFIG.get("temperature", 0.3),
            "num_predict": GENAI_CONFIG.get("max_tokens", 1000)
        }
    )
    return response.get('message', {}).get('content', "No response generated.")


def _generate_ai(prompt: str, system_prompt: str = "") -> str:
    """Intelligent dispatcher: Tries Gemini first, falls back to Ollama, then template."""
    status = get_ai_status()
    
    if status["provider"] == "gemini":
        try:
            return _query_gemini(prompt, system_prompt)
        except Exception as e:
            # If Gemini fails (e.g. rate limit), try Ollama if available
            if OLLAMA_AVAILABLE:
                try:
                    return _query_ollama(prompt, system_prompt)
                except Exception:
                    pass
            raise e
            
    elif status["provider"] == "ollama":
        return _query_ollama(prompt, system_prompt)
        
    raise RuntimeError("No AI provider available.")


def _fallback_explanation(context: str, explanation_type: str) -> str:
    """Deterministic, high-quality rule-based fallback responses."""
    fallbacks = {
        "prediction": "Based on your historical spending records and linear trend velocity, the forecasting engine projected your expenditure for the upcoming cycle. Key drivers include recurring monthly commitments (rent, utilities) combined with recent category averages.",
        "anomaly": "This transaction was flagged because its magnitude deviates significantly (Z-score threshold exceeded) from your typical category baseline. It represents an irregular one-time spike rather than an ongoing recurring expense.",
        "recommendation": "These recommendations were derived by comparing your category-level expenditure against standard 50/30/20 financial allocations and checking for category-month inflation rates over 15%.",
        "chat": "AI Assistant is running in offline template mode. To unlock conversational advice powered by Google Gemini, please add your GEMINI_API_KEY in the .env file."
    }
    return fallbacks.get(explanation_type, fallbacks["chat"])


def explain_prediction(context: str) -> str:
    """Generate human-readable explanation of next month's forecast."""
    prompt = f"Given this financial context:\n{context}\n\nExplain the projected next month expense in 2-3 clear, professional bullet points. Reference specific numbers from the context. Do not invent any numbers."
    system = "You are a senior financial advisor at FinSight AI. Be precise, encouraging, and strictly grounded in data."
    try:
        return _generate_ai(prompt, system)
    except Exception:
        return _fallback_explanation(context, "prediction")


def explain_anomaly(anomaly: dict, profile: dict) -> str:
    """Generate contextual explanation for an irregular transaction."""
    budget = profile.get('monthly_budget', profile.get('budget', 0))
    prompt = f"Explain why a transaction of {CURRENCY_SYMBOL}{anomaly.get('amount', 0):,.2f} on {anomaly.get('date', 'recent date')} in category '{anomaly.get('category', 'Unknown')}' with description '{anomaly.get('description', '')}' is classified as an anomaly for a user with a {CURRENCY_SYMBOL}{budget:,.2f} monthly budget."
    system = "You are an AI financial fraud and anomaly analyst."
    try:
        return _generate_ai(prompt, system)
    except Exception:
        return _fallback_explanation(str(anomaly), "anomaly")


def explain_recommendations(recommendations: list, context: str) -> str:
    """Elaborate on algorithmic recommendations."""
    recs_str = "\n".join([f"- {r.get('title', '')}: {r.get('message', '')}" for r in recommendations])
    prompt = f"Financial Context:\n{context}\n\nRecommended Actions:\n{recs_str}\n\nProvide a motivating, concise summary of how adopting these recommendations helps the user achieve their financial goal."
    system = "You are a motivating, data-driven personal wealth coach."
    try:
        return _generate_ai(prompt, system)
    except Exception:
        return _fallback_explanation(context, "recommendation")


def financial_chat(user_message: str, context: str) -> str:
    """Handle interactive user questions with full financial profile grounding."""
    prompt = f"User Financial Context:\n{context}\n\nUser Question: {user_message}\n\nAnswer the question directly, accurately, and concisely. Keep your tone encouraging and professional. If calculations are needed, use the exact figures given above."
    system = "You are FinSight AI, an expert personal finance consultant. You provide mathematically sound, empathetic financial advice grounded strictly in the user's spending data."
    try:
        return _generate_ai(prompt, system)
    except Exception as e:
        status = get_ai_status()
        if not status["available"]:
            return f"💡 **Offline Note:** { _fallback_explanation(context, 'chat')}\n\n*Your Question:* \"{user_message}\""
        return f"⚠️ Could not generate AI response: {str(e)}"
