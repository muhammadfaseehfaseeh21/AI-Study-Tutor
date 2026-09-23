import json

# 1. Tool execution logic
def generate_quiz(topic: str, num_questions: int = 3):
    """Generates practice questions on a given topic."""
    return json.dumps({
        "status": "success",
        "instruction": f"Generate a {num_questions}-question multiple-choice quiz on '{topic}'. Format each question clearly with options A, B, C, D and include explanations at the bottom."
    })

def create_summary(text_or_topic: str):
    """Creates key bullet-point study notes for a topic."""
    return json.dumps({
        "status": "success",
        "instruction": f"Provide a structured study summary for '{text_or_topic}'. Include Core Concepts, Key Terms & Definitions, and 3 Practical Examples."
    })

def solve_math(expression: str):
    """Evaluates mathematical operations safely."""
    try:
        result = eval(expression, {"__builtins__": None}, {})
        return json.dumps({"expression": expression, "result": str(result)})
    except Exception as e:
        return json.dumps({"error": f"Invalid math expression: {str(e)}"})

# Function Registry
AVAILABLE_FUNCTIONS = {
    "generate_quiz": generate_quiz,
    "create_summary": create_summary,
    "solve_math": solve_math,
}

# 2. Tool Schemas for Groq
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "generate_quiz",
            "description": "Generate practice quiz questions when the student asks for practice, test, or quiz.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The subject or topic for the quiz, e.g., 'Quantum Physics' or 'World History'"
                    },
                    "num_questions": {
                        "type": "integer",
                        "description": "Number of questions to generate (default 3)"
                    }
                },
                "required": ["topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_summary",
            "description": "Generate structured study notes/summaries when the user asks for notes, summary, or cheat sheet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text_or_topic": {
                        "type": "string",
                        "description": "Topic or text to generate key study points for."
                    }
                },
                "required": ["text_or_topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "solve_math",
            "description": "Perform direct math calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate, e.g., '145 * 12 + 80'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]
