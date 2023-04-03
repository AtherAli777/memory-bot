import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI 

#Initalize session sattes
# A session satate stores the sesson of current satate of user in form of dictionary i.e value and key pair
# It stores the cache of user input in one session so it don't go away and other user won't be effected by it.

if "generated" not in st.session_state:
    st.session_state['generated'] = [] #output
if "past" not in st.session_state:
    st.session_state['past'] = [] #past
if "input" not in st.session_state:
    st.session_state['input'] = "" #input
if "stored_session" not in st.session_state:
    st.session_state['stored_session'] = [] #stored_session

#we have defined the session by using key 
#now we define function to get user input

def get_text():
    """
    Get the user input text.
    Returns:
        (str): The text entered by the user
    """
    input_text = st.text_input("You: ", st.session_state["input"], key="input",
                            placeholder="Your AI assistant here! Ask me anything ...", 
                            label_visibility='hidden')
    return input_text

st.title("Memory Bot")

# API key, we w
# ill create a side bar where user can enter their won api key
api = st.sidebar.text_input("API-KEY", type="password")
#we will allow user to choce their own model name
MODEL = st.sidebar.selectbox(label="Model", options=['gpt-3.5-turbo', 'text-davinci-003','text-davinci-002'])

# output_size = st.sidebar.radio(label = "What kind of output do you want?", 
#                     options= ["To-The-Point", "Concise", "Detailed"])

# if output_size == "To-The-Point":
#     out_token = 50
# elif output_size == "Concise":
#     out_token = 128
# else:
#     out_token = 516


if api:
    #create openai instance
    llm = OpenAI(
        temperature=0,
        openai_api_key= api,
        model_name=MODEL,
        #max_tokens=len(output_size),
    )

# CREATE CONVERSATION MEMORY
# if entity is not in sesstion state we for the first time create a conversation entity
# we pass our large language model that we created above which is openai
# this will remember what the conversation was about
    if 'entity_memory' not in st.session_state:
        st.session_state['entity_memory'] = ConversationEntityMemory(llm=llm, k=10)

        #NEXT CREATE CONVERSATION CHAIN of what the chain of conversation is 
    Conversation = ConversationChain(
        llm = llm,
        prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        memory=st.session_state['entity_memory']
    )

else:
    st.error("No API found")

user_input = get_text()

# Generate the output using the conversationchain object and the user input,
if user_input:
    output = Conversation.run(input=user_input)
    st.session_state.past.append(user_input) #remembers input
    st.session_state.generated.append(output) #remembers output

with st.expander("Conversation"):
    for i in range(len(st.session_state['generated'])-1,-1,-1):
        st.info(st.session_state['past'][i])
        st.info(st.session_state['generated'][i])

def new_chat():
    """
    Clears session state and starts a new chat.
    """
    save = []
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])        
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.store = {}
    st.session_state.entity_memory.buffer.clear()
st.sidebar.button("New Chat", on_click = new_chat, type='primary')

# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
    with st.sidebar.expander(label= f"Conversation-Session:{i}"):
        st.write(sublist)

             

# # Allow the user to clear all stored conversation sessions
# if st.session_state.stored_session:   
#     if st.sidebar.checkbox("Clear-all"):
#         del st.session_state.stored_session