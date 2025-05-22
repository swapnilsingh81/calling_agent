from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
from dotenv import load_dotenv
import os


app = Flask(__name__)

load_dotenv()  # loads variables from .env into environment

# Set your OpenAI API key as environment variable for security
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_openai(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful sales and onboarding AI agent for BFSI and Fintech companies."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
        temperature=0.7,
    )
    answer = response['choices'][0]['message']['content']
    return answer.strip()

@app.route("/voice", methods=['POST'])
def voice():
    response = VoiceResponse()
    speech_result = request.values.get('SpeechResult', '').strip()

    if not speech_result:
        gather = Gather(input='speech', timeout=5, hints='hello, savings account, apply, onboarding, fintech, insurance')
        gather.say("Hello! Welcome to RevRag AI Sales. How can I help you today?")
        response.append(gather)
    else:
        print(f"User said: {speech_result}")

        # Ask OpenAI for a reply
        ai_reply = ask_openai(speech_result)
        print(f"AI reply: {ai_reply}")

        response.say(ai_reply)
        
        # Continue gathering for follow-up conversation
        gather = Gather(input='speech', timeout=5, hints='yes, no, apply, more info')
        response.append(gather)

    return Response(str(response), mimetype='application/xml')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)