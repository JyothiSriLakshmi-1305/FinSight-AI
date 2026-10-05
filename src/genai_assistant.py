import requests
import json
from config.settings import GENAI_CONFIG, CURRENCY_SYMBOL

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

def check_ollama_connection() -> bool:
    if not OLLAMA_AVAILABLE:
        return False
    try:
        host = GENAI_CONFIG.get("host", "http://localhost:11434")
        response = requests.get(f"{host}/api/tags", timeout=3)
        return response.status_code == 200
    except Exception:
        return False

def build_financial_context(profile: dict, prediction: float = None, anomalies: dict = None, recommendations: list = None) -> str:
    context = [f"User Profile Summary:"]
    context.append(f"- Monthly Budget: {CURRENCY_SYMBOL}{profile.get('monthly_budget', 0):,.2f}")
    
    if prediction:
        context.append(f"- Projected Next Month Expense: {CURRENCY_SYMBOL}{prediction:,.2f}")
        
    if anomalies and anomalies.get('count', 0) > 0:
        context.append(f"- Recent Anomalies: {anomalies['count']} transactions flagged totaling {CURRENCY_SYMBOL}{anomalies.get('amount', 0):,.2f}")
        
    if recommendations:
        context.append("\nTop Recommendations:")
        for r in recommendations[:3]:
            context.append(f"- {r['title']}: {r['message']}")
            
    return "\n".join(context)

def _query_ollama(prompt: str, system_prompt: str = '') -> str:
    if not check_ollama_connection():
        raise ConnectionError("Ollama is not available.")
        
    try:
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
    except Exception as e:
        raise RuntimeError(f"Ollama generation failed: {str(e)}")

def _fallback_explanation(context: str, explanation_type: str) -> str:
    fallbacks = {
        "prediction": "Based on your recent spending history and trends, the machine learning model has projected your expenses for next month. Please review the specific factors provided to see what is driving this forecast.",
        "anomaly": "This transaction was flagged because it deviates significantly from your usual spending patterns in this category. It may be an unexpected large purchase.",
        "recommendation": "These recommendations are generated based on rules applied to your spending behavior. Following them can help you stay within budget and optimize your savings.",
        "chat": "I am currently running in simple mode without AI capabilities. I can show you your data and statistics, but I cannot answer complex financial questions right now."
    }
    return fallbacks.get(explanation_type, fallbacks["chat"])

def explain_prediction(context: str) -> str:
    prompt = f"Given this financial context:\n{context}\n\nExplain the projected next month expense in simple terms to the user. Do not invent numbers."
    system = "You are a helpful, factual financial advisor."
    try:
        return _query_ollama(prompt, system)
    except Exception:
        return _fallback_explanation(context, "prediction")

def explain_anomaly(anomaly: dict, profile: dict) -> str:
    prompt = f"Explain why a transaction of {CURRENCY_SYMBOL}{anomaly.get('amount', 0)} in category '{anomaly.get('category', 'Unknown')}' is unusual for a user with a {CURRENCY_SYMBOL}{profile.get('monthly_budget', 0)} budget."
    system = "You are an AI financial analyst."
    try:
        return _query_ollama(prompt, system)
    except Exception:
        return _fallback_explanation(str(anomaly), "anomaly")

def explain_recommendations(recommendations: list[dict], context: str) -> str:
    recs_str = "\n".join([r['title'] + ": " + r['message'] for r in recommendations])
    prompt = f"Context:\n{context}\n\nRecommendations:\n{recs_str}\n\nProvide an encouraging summary elaborating on why the user should follow these steps."
    system = "You are a motivating financial coach."
    try:
        return _query_ollama(prompt, system)
    except Exception:
        return _fallback_explanation(context, "recommendation")

def financial_chat(user_message: str, context: str) -> str:
    prompt = f"Context:\n{context}\n\nUser Question: {user_message}\n\nProvide a concise, helpful answer relying ONLY on the context provided."
    system = "You are a personalized FinSight AI assistant."
    try:
        return _query_ollama(prompt, system)
    except Exception:
        return _fallback_explanation(context, "chat")
