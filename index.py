from dotenv import load_dotenv
import gspread
import streamlit as st
import os, time
import openai
import streamlit.components.v1 as html

load_dotenv()

gc = gspread.service_account_from_dict(
    {
        "type": os.environ.get("type"),
        "project_id": os.environ.get("project_id"),
        "private_key_id": os.environ.get("private_key_id"),
        "private_key": os.environ.get("private_key"),
        "client_email": os.environ.get("client_email"),
        "client_id": os.environ.get("client_id"),
        "auth_uri": os.environ.get("auth_uri"),
        "token_uri": os.environ.get("token_uri"),
        "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
        "client_x509_cert_url": os.environ.get("client_x509_cert_url"),
        "universe_domain": os.environ.get("universe_domain"),
    }
)

sh = gc.open_by_url(
    "https://docs.google.com/spreadsheets/d/1MFytQYnb3xHhBW3-hWcPrb2vni0mBcYDkT9yca7UlwI"
)

promptTemplateSheet = sh.get_worksheet(2)


def api_get_available_index(worksheet):
    list_of_lists = worksheet.get_all_values()
    return len(list_of_lists) + 1


def saveToSheet():
    i = api_get_available_index(promptTemplateSheet)
    promptTemplateSheet.update(
        r"A{}:F{}".format(i, i),
        [
            [
                st.session_state["gpt_modal"],
                st.session_state["temperature"],
                st.session_state["system_msg"],
                st.session_state["human_msg"],
                st.session_state["response"],
                time.time(),
            ]
        ],
    )


def callGPT():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print(st.session_state)
    # temperature = (float("{:.1f}".format(st.session_state["temperature"])),)

    # return
    response = openai.ChatCompletion.create(
        model=st.session_state["gpt_modal"],
        messages=[
            {"role": "system", "content": st.session_state["system_msg"]},
            {"role": "user", "content": st.session_state["human_msg"]},
        ],
        temperature=float("{:.1f}".format(st.session_state["temperature"])),
        # max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    print(response)
    st.session_state["response"] = response.choices[0].message.content


if "temperature" not in st.session_state:
    st.session_state["temperature"] = 0.0

if "system_msg" not in st.session_state:
    st.session_state["system_msg"] = ""

if "human_msg" not in st.session_state:
    st.session_state["human_msg"] = ""

if "response" not in st.session_state:
    st.session_state["response"] = ""

if "gpt_modal" not in st.session_state:
    st.session_state["gpt_modal"] = ""

st.set_page_config(layout="wide")

st.title("Prompt Trial and Error System")


title_alignment = """
<style>
#the-title {
  text-align: center
}
.block-container {
padding: 2rem 1rem;
}
.stSlider  p{
margin-bottom: 15px
}
.stSlider  > div{
margin-bottom: 20px
}
</style>
"""
st.markdown(title_alignment, unsafe_allow_html=True)

col1, col2 = st.columns(2)

with st.form("my_form"):
    with col1:
        st.session_state["system_msg"] = st.text_area(
            "System Message",
            value="",
        )

    with col2:
        st.session_state["human_msg"] = st.text_area(
            "Human Message",
            value="",
        )

    col21, col22, col23, col24, col25 = st.columns(5)

    with col21:
        st.session_state["temperature"] = st.slider(
            "Select Temperature", 0.0, 1.0, step=0.1
        )

    with col22:
        st.session_state["gpt_modal"] = st.radio(
            "GPT-Modal (Awaiting GPT-4)",
            ("gpt-3.5-turbo", "gpt-3.5-turbo-16k"),
            index=0,
        )

    with col23:
        submitted = st.form_submit_button(
            "Execute", use_container_width=True, type="primary"
        )  # , on_click=callGPT)
        if submitted:
            callGPT()

with col25:
    # st.header("Section 1")
    st.markdown(
        "[Sheet Link](https://docs.google.com/spreadsheets/d/1MFytQYnb3xHhBW3-hWcPrb2vni0mBcYDkT9yca7UlwI/edit#gid=1074032545)"
    )


if st.session_state["response"]:
    st.header("AI: response")
    st.markdown(st.session_state["response"], unsafe_allow_html=False)

    st.button("Save to sheet", type="primary", on_click=saveToSheet)
