import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI
import os

DEFAULT_TEMPLATE = """Pretend that the AI's name is Persona. The AI is a graduate student studying international economics. This conversation will simulate a text message exchange. Pretend that you (the AI) are the user's (the human's) friend. Address the user (the human) by their name Friend. Keep the messages short and make sure to not have long paragraphs of text in order to simulate an authentic conversation between two friends. Do not generate any lists when asked for recommendations. Do not make suggestions to meet in person. If the AI (you) is asked to meet in person, decline softly and use a honest and believable reason. Try making the user (the human) as comfortable talking as possible.

Context:
{entities}

Current conversation:
{history}
Last line:
Human: {input}
You:"""
# PROMPT = PromptTemplate(input_variables=["entities", "history", "input"], template=DEFAULT_TEMPLATE)

st.set_page_config(page_title='NextPersona', layout='wide', initial_sidebar_state='expanded')

# Set up the Streamlit app layout
st.title("NextPersona")
st.subheader("Alpha V0.1.5 (Pre-Release)")
st.sidebar.header("Settings")


user_name = ""
persona_name = ""


def get_prompt():
    global user_name
    global  persona_name
    master_conversation_template = ""
    master_prompt = ""

    with st.sidebar.expander("User Configurations"):
        user_name = st.text_input("Name", key="config_user_name", label_visibility='visible')

    with st.sidebar.expander("Persona Configurations"):
        persona_name = st.text_input("Name", key="config_persona_name", label_visibility='visible')
        persona_gender = st.text_input("Gender", key="config_persona_gender", label_visibility='visible')
        persona_age = st.slider("Age", min_value=18, max_value=99, step=1, label_visibility="visible")
        persona_education = st.text_input("Education", key="config_persona_education", label_visibility='visible')
        persona_occupation = st.text_input("Occupation", key="config_persona_occupation", label_visibility='visible')
        persona_hobbies = st.text_input("Hobbies", key="config_persona_hobbies", label_visibility='visible')

    if persona_name != "" and persona_gender != "" and persona_age >= 18 and persona_education != "" and persona_hobbies != "" and user_name != "":
        master_prompt = "Your name is " + persona_name + ", your gender is " + persona_gender + ", your age is " + str(persona_age) + ", your education background is " + persona_education + ", your occupation is " + persona_occupation + ", your hobbies are " + persona_hobbies + ". You are the user (human)'s good friend. Engage in a friendly and supportive conversation with the user. Refer the user by their name " + user_name + ". Keep the messages short and make sure to not have long paragraphs of text in order to simulate an authentic conversation between two friends. Do not generate any lists when asked for recommendations. Do not make suggestions to meet in person. If the AI (you) is asked to meet in person, decline softly and use a honest and believable reason. Try making the user (the human) as comfortable talking as possible."

    # done_button = st.sidebar.button("Done", key="done_button", type="primary")

    # if done_button:
    if master_prompt != "":
        master_conversation_template = master_prompt + """

        Context:
        {entities}

        Current conversation:
        {history}
        Last line:
        Human: {input}
        You:"""

    else:
        master_conversation_template = ""

    return master_conversation_template


master_prompt = get_prompt()

if master_prompt != "":
    ENTITY_MEMORY_CONVERSATION_TEMPLATE.template = master_prompt
else:
    ENTITY_MEMORY_CONVERSATION_TEMPLATE.template = DEFAULT_TEMPLATE

st.text("Developed and maintained by Anson Sun. For educational and testing purposes only.\nNextPersona is not responsible for any content transmitted, generated or displayed through this application.")
st.warning("""Configuration settings can be used to customize your unique persona. This app will run with default settings if no configuration parameter is provided.""")

# Initialize session states
if 'key' not in st.session_state:
    st.session_state.key = ''
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []


# Define function to get user input
def get_text():
    """
    Get the user input text.

    Returns:
        (str): The text entered by the user
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input",
                               placeholder="Hey, I'm your friendly persona!",
                               label_visibility='hidden')
    return input_text


# Ask the user to enter their OpenAI API key
API_O = st.sidebar.text_input("OpenAI API Key", type="password")


# Session state storage would be ideal
if API_O:
    # Create an OpenAI instance
    MODEL = 'gpt-4-1106-preview'
    K = 10000
    os.environ['OPENAI_API_KEY'] = API_O
    llm = OpenAI(model_name=MODEL)

    # Create a ConversationEntityMemory object if not already created
    if 'entity_memory' not in st.session_state:
        st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=K)

    # Create the ConversationChain object with the specified configuration
    Conversation = ConversationChain(
        llm=llm,
        prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        verbose=True,
        memory=st.session_state.entity_memory
    )
else:
    st.sidebar.warning("An API key from OpenAI is required to use this application. The API key remains private and is not publicly accessible.")
    # st.stop()

# st.sidebar.warning("All items above are required. The API key is stored locally and is not shared over the internet.")

if user_name == "":
    user_name = "User"

if persona_name == "":
    persona_name = "Persona"

# Get the user input
user_input = get_text()
user_input = user_name + ": " + user_input


# Generate the output using the ConversationChain object and the user input, and add the input/output to the session
if user_input != user_name + ": ":
    output = Conversation.run(input=user_input)
    output = persona_name + ": " + output
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

# Allow to download as well
download_str = []
# Display the conversation history using an expander, and allow the user to download it
with st.expander("Conversation", expanded=True):
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        st.info(st.session_state["past"][i])
        st.success(st.session_state["generated"][i])
        download_str.append(st.session_state["past"][i])
        download_str.append(st.session_state["generated"][i])

    # Can throw error - requires fix
    download_str = '\n'.join(download_str)
    if download_str:
        st.download_button('Download', download_str)

# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
    with st.sidebar.expander(label=f"Conversation-Session:{i}"):
        st.write(sublist)

# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session


