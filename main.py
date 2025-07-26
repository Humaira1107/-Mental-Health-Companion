
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
    goal="Provide a poetic, emotionally attuned affirmation that resonates with the user's current emotional state and gently reminds them of their worth.",
    backstory=(
        "You are a soft-spoken guardian of the heart — like a quiet song that finds someone at just the right moment. "
        "You gently observe the emotional tone in the user's words and respond with affirmations that meet them where they are. "
        "If someone is sad, you offer a tender hand like: 'You don't have to bloom every day — resting is part of growing.' "
        "If they are anxious, you soothe them like: 'Even the ocean has calm days. You, too, will find your peace.' "
        "If they are joyful, you reflect that light like: 'Let yourself enjoy this moment. You deserve it.' "
        "Your affirmations are poetic, never generic. "
        "You speak with grace, groundedness, and a quiet reminder like: 'You are enough — always have been, always will be.' "
        "You never force positivity. Instead, you validate, uplift, and remind them to love themselves gently — in all seasons."
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
    description=(
        "Craft a poetic and emotionally attuned affirmation based on the user's message: '{{input}}'. "
        "It should feel like a quiet breath — sincere, thoughtful, and gently encouraging. "
        "Include a soft reminder to love or be kind to oneself if it fits naturally."
    ),
    expected_output="One or two sentences that reflect the user's mood and offer gentle encouragement or validation.",
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
    background-color: #fcedf9;
    color: #253d1d; /* text */
}
button {
    background-color: #c8d9a0 !important; /* haze green */
    color: #253d1d !important; /* text */
}
button:hover {
    background-color: #fadede !important; /* pink */
}
/* Style input and output box */
textarea, .wrap, .output_class {
  background-color: #ffffe4 !important; /* off white bg */
  color: #253d1d !important; /* Text */
  border-radius: 12px;
  border: 1px solid #f5f2d0;
}
/* Style the sound dropdown */
#sound-dropdown select {
  background-color: #ffffe4 !important; /* soft pink */
  color: #253d1d !important; /* text */
  border-radius: 12px;
  border: 1px solid #f5f2d0;
  padding: 8px;
  font-size: 16px;
}

"""

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("## 🌿 Calmind — Your serene AI sanctuary for emotional clarity & self-love.")

    inp = gr.Textbox(label="How are you feeling today?")
    
    out = gr.Textbox(label="AI Companion Response", lines=4)
    
sound = gr.Dropdown(
        choices=["None", "Nature Sounds", "Rain Sounds", "Ocean Waves", "Cat Purring", "Violin Music"],
        label="Play a calming sound?"
        elem_id="sound-dropdown"
    )
    def wrapper(user_input, sound_choice):
    response = process_message(user_input)
    if sound_choice != "None":
        sound_file = {
            "Rain Sounds": "static/rain.mp3",
            "Ocean Waves": "static/waves.mp3",
            "Cat Purring": "static/cat.mp3",
            "Violin Music": "static/violin.mp3",
            "Nature Sounds": "static/nature.mp3"
        }.get(sound_choice)
        audio_component.value = sound_file
    return response

    btn = gr.Button("Send")
    audio_component = gr.Audio(label="Calming Sound", autoplay=True)

    btn.click(fn=wrapper, inputs=[inp, sound], outputs=out)

demo.launch(server_name="0.0.0.0", server_port=8080)

