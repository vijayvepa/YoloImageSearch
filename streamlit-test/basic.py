import streamlit as st


all_profiles = []

st.title("Streamlit Intro")
st.write("This is where we will learn streamlit")

# Getting user input
name = st.text_input("What is your name?", key="name")
if name:
		st.write(f"Welcome, {name}! Ready to build something amazing")

# More interactive widgets
age = st.slider("Select your age", 0, 100, 25, key="age")
if age:
		st.write(f"You are {age} years old")

gender = st.radio("Select your gender", ("Male", "Female", "Other"), key="gender")
if gender:
		st.write(f"You are {gender}")

interestedIn = st.selectbox("What are you interested in?", ("Computer Vision", "NLP", "Reinforcement Learning"), key="interest")
if interestedIn:
		st.write(f"You are interested in {interestedIn}")


new_profile = {"name": name, "age": age, "gender": gender, "interestedIn": interestedIn}
all_profiles.append(new_profile) 


if "profiles" not in st.session_state:
		st.session_state.profiles = []


if st.button("Submit"):
		st.session_state.profiles.append(new_profile)
		st.write(st.session_state.profiles)
