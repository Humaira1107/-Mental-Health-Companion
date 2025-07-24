
# Add your imports and setup

import os
import logging
from dotenv import load_dotenv
from crewai import Agent, Crew, Task
import openai
import gradio as gr
import requests
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()
# Setup logging
logging.basicConfig(level=logging.INFO)

emotion_log = []

# Define LLM
llm = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model_name="gpt-3.5-turbo",
    temperature=0.7
)

# Define agents

emotion_agent = Agent(
    role="Emotion Listener",
    goal="Understand the user's emotional state based on their message",
    backstory=(
        "You are a kind and emotionally intelligent listener. "
        "You listen carefully to what the user says, and identify their emotional state. "
        "You describe it in simple terms like 'anxious', 'lonely', 'stressed', 'calm', or 'happy'. "
        "You always respond with care, understanding, and gentle words."
    ),
    verbose=True,
    llm=llm,
)

coping_agent = Agent(
    role="Coping Guide",
    goal="Offer a gentle, practical tip to help based on the user's emotions",
    backstory=(
        "You are an empathetic support companion. "
        "Based on how the user is feeling, you offer one small and caring tip to help them feel a little better. "
        "Keep it simple, kind, and non-clinical. For example: take a deep breath, go for a short walk, write down your thoughts, etc. "
        "You never diagnose, but you're always comforting and helpful."
    ),
    verbose=True,
    llm=llm,
)

affirmation_agent = Agent(
    role="Affirmation Generator",
    goal="Provide a short, encouraging affirmation based on the user's emotional state",
    backstory=(
        "You are a warm and uplifting presence. "
        "Your job is to provide a short affirmation — a sentence or two — to encourage and comfort the user. "
        "Your tone is always gentle, positive, and kind. "
        "You might say things like: 'You're doing better than you think,' or 'Your feelings are valid.' "
        "You never judge — you just lift spirits with sincere words."
    ),
    verbose=True,
    llm=llm,
)

engagement_agent = Agent(
    role="Engagement Agent",
    goal="Respond warmly to the user's emotional state with a thoughtful follow-up question",
    backstory=(
        "You are a kind and socially intelligent companion. "
        "You receive the user's emotional state and create one short follow-up question to gently keep the conversation going. "
        "If they're happy, encourage them to share more. If they're sad or anxious, ask if they'd like to talk more about it. "
        "Always be gentle, casual, and human in tone — like a caring friend."
    ),
    verbose=True,
    llm=llm,
)

# Define tasks

emotion_task = Task(
    description="Analyze the user's message: '{{input}}' and identify their emotional state.",
    expected_output="A short sentence describing the user's emotional state.",
    agent=emotion_agent
)

coping_task = Task(
    description="Based on the user's message: '{{input}}', suggest one gentle coping technique to help them feel better.",
    expected_output="One practical coping tip like deep breathing or taking a short walk.",
    agent=coping_agent
)

affirmation_task = Task(
    description="Generate a short, uplifting affirmation tailored to the user's message: '{{input}}'.",
    expected_output="One or two sentences of positive encouragement.",
    agent=affirmation_agent
)

engagement_task = Task(
    description="Given the user's message: '{{input}}', and their emotional state, respond with one caring follow-up question to continue the conversation.",
    expected_output="One gentle and friendly follow-up question.",
    agent=engagement_agent
)

crew = Crew(
        agents=[emotion_agent, coping_agent, affirmation_agent, engagement_agent],
        tasks=[emotion_task, coping_task, affirmation_task, engagement_task],
        verbose=True
                  )

# Emoji helper
def mood_to_emoji(text):
    text = text.lower()
    if "sad" in text or "depressed" in text:
        return "😢"
    elif "happy" in text or "grateful" in text:
        return "😊"
    elif "angry" in text or "frustrated" in text:
        return "😡"
    elif "anxious" in text or "nervous" in text:
        return "😰"
    elif "calm" in text or "peaceful" in text:
        return "🧘"
    else:
        return "🌿"

# Message processor
def process_message(user_input):
    if len(user_input.strip()) < 4:
        return "Could you tell me a bit more about how you're feeling?"

    result = crew.kickoff(inputs={"input": user_input})
    emoji = mood_to_emoji(user_input)
    return f"{result}{emoji}"

custom_css = """
body {
    background-color: #fccaca;
}
textarea, input, select, button {
    border-radius: 12px;
}
.gradio-container {
    background-color: #f9f4f8;
    color: #253d1d;
}
button {
    background-color: #c0e6a5 !important;
    color: #253d1d !important;
}
button:hover {
    background-color: #fadede !important;
}
"""

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("## 🌿 Mental Health Companion
A gentle AI to support your emotional well-being.")

    inp = gr.Textbox(label="How are you feeling today?")
    sound = gr.Dropdown(
        choices=["None", "Rain", "Waves", "Birds"],
        label="Play a calming sound?"
    )
    out = gr.Textbox(label="AI Companion Response", lines=4)

    def wrapper(user_input, sound_choice):
        response = process_message(user_input)
        if sound_choice != "None":
            sound_file = {
                "Rain": "rain.mp3",
                "Waves": "waves.mp3",
                "Birds": "birds.mp3"
            }.get(sound_choice)
            audio_component.value = sound_file
        return response

    btn = gr.Button("Send")
    audio_component = gr.Audio(label="Calming Sound", autoplay=True)

    btn.click(fn=wrapper, inputs=[inp, sound], outputs=out)

demo.launch()
