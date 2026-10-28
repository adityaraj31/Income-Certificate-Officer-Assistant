# फॉलबैक AI (की उपलब्ध न होने पर)
from typing import Dict, Any


def fallback_suggestion(flags: list) -> Dict[str, Any]:
    if not flags:
        return {
            "summary": "सभी आवश्यक जाँचें पूर्ण प्रतीत होती हैं।",
            "reasoning": "नियमों के आधार पर कोई स्पष्ट झंडा नहीं मिला है।",
            "suggestion": "सामान्य जाँच के बाद अनुमोदन पर विचार करें।",
        }
    return {
        "summary": f"{len(flags)} संभावित समस्या(एँ) पाई गईं।",
        "reasoning": "; ".join(flags),
        "suggestion": "संबंधित दस्तावेज़ों की जाँच कर निर्णय लें।",
    }
