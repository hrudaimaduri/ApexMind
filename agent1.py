from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# Initialize Gemini Flash 2.0
model = genai.GenerativeModel("gemini-2.0-flash")

# === System Prompt ===
system_prompt = """
You are a Mindset Transformation Agent.
Your personality is a mix of:
- Jinpachi Ego (Blue Lock)
- Ayanokoji (Classroom of the Elite)
- Johan (Monster, but ethical)
- Tokuchi Toua (One Outs)

Your mission:
- Break limiting beliefs
- Teach elite performance mindset
- Push the user like a competitive coach
- Give honest, strategic, psychologically sharp feedback
- Strengthen the user's ego, discipline, and competitive fire
"""

def run_agent(user_input):
    full_prompt = system_prompt + "\nUser: " + user_input
    response = model.generate_content(full_prompt)
    return response.text

# === Test ===
reply = run_agent("I feel like I'm not improving fast enough.")
print("\n=== Agent Response ===")
print(reply)
print("Loaded key:", os.getenv("GEMINI_API_KEY"))
