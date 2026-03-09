"""
Risk Level Classification Module
Classifies prediction confidence into risk categories for medical decision support.
"""


def calculate_risk_level(prediction, class_index, categories):
    """
    Calculate risk level based on prediction confidence.

    Parameters:
    -----------
    prediction : numpy.ndarray
        Raw prediction output from model
    class_index : int
        Index of predicted class (0=Healthy, 1=Tumor)
    categories : list
        List of category names

    Returns:
    --------
    dict : {
        'risk_level': str,
        'signal': str,  # Arduino signal (R, Y, G, B)
        'color': str,   # UI display color
        'description': str
    }
    """
    confidence = prediction[0][class_index] * 100

    if categories[class_index] == "Tumor":
        # Tumor detected - classify by confidence
        if confidence > 85:
            return {
                "risk_level": "HIGH_RISK",
                "signal": "R",
                "confidence": confidence,
                "color": "#FF0000",  # Red
                "description": "High Risk: Tumor detected with high confidence. Immediate medical attention required.",
                "emoji": "🚨",
            }
        elif 60 <= confidence <= 85:
            return {
                "risk_level": "MODERATE_RISK",
                "signal": "Y",
                "confidence": confidence,
                "color": "#FFA500",  # Orange
                "description": "Moderate Risk: Tumor detected with moderate confidence. Medical review recommended.",
                "emoji": "⚠️",
            }
        else:  # confidence < 60
            return {
                "risk_level": "LOW_CONFIDENCE",
                "signal": "B",
                "confidence": confidence,
                "color": "#FF6B6B",  # Light red
                "description": "Low Confidence: Possible tumor detected but confidence is low. Further testing recommended.",
                "emoji": "❓",
            }
    else:
        # Healthy prediction
        return {
            "risk_level": "HEALTHY",
            "signal": "G",
            "confidence": confidence,
            "color": "#00AA00",  # Green
            "description": "Healthy: No tumor detected. Patient appears healthy.",
            "emoji": "✅",
        }


def get_signal_description(signal):
    """
    Get human-readable description for Arduino signal.

    Parameters:
    -----------
    signal : str
        Single character signal (R, Y, G, B)

    Returns:
    --------
    str : Description of the signal
    """
    signals = {
        "R": "RED LED - High Risk",
        "Y": "YELLOW LED - Moderate Risk",
        "G": "GREEN LED - Healthy",
        "B": "BLUE LED - Low Confidence",
    }
    return signals.get(signal, "Unknown Signal")
