import streamlit as st
import requests

# API endpoint
API_URL = "http://localhost:8080"

# Page configuration
st.set_page_config(page_title="Diet Plan Generator",
                   page_icon="🍽️", layout="wide")

# Title
st.title("🍽️ Diet Plan Generator")
st.markdown(
    "Generate a personalized diet plan based on your preferences and goals.")

# User input form
with st.form("user_profile_form"):
    st.subheader("Your Profile")
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Name", placeholder="Enter your name")
        age = st.number_input("Age", min_value=1, max_value=120, value=25)
        gender = st.selectbox("Gender", ["male", "female", "other"])
        height = st.number_input(
            "Height (cm)", min_value=50, max_value=250, value=170)
        weight = st.number_input(
            "Weight (kg)", min_value=30, max_value=300, value=70)

    with col2:
        diet_type = st.multiselect(
            "Diet Type",
            options=["paleo", "vegan", "keto", "mediterranean", "dash"],
            default=["mediterranean"]
        )
        cuisine = st.multiselect(
            "Preferred Cuisine",
            options=["indian", "asian", "italian", "mexican", "american"],
            default=["indian", "asian"]
        )
        allergies = st.multiselect(
            "Allergies",
            options=["none", "gluten", "dairy", "nuts", "seafood", "beef"],
            default=["none"]
        )
        calorie_goal = st.number_input(
            "Daily Calorie Goal", min_value=1000, max_value=5000, value=2000)

    submitted = st.form_submit_button("Generate Diet Plan")

# Generate diet plan
if submitted:
    if not name or not diet_type or not cuisine:
        st.error("Please fill in all required fields.")
    else:
        user_profile = {
            "id": "1",
            "name": name,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "diet_type": diet_type,
            "cuisine": cuisine,
            "allergies": allergies if "none" not in allergies else None,
            "calorie_goal": calorie_goal
        }

        with st.spinner("Generating your personalized diet plan..."):
            try:
                response = requests.post(
                    f"{API_URL}/generate", json=user_profile)
                response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
                result = response.json()
                if result["success"]:
                    st.success("Diet plan generated successfully!")
                    st.subheader("Your Diet Plan")
                    st.json(result["response"])
                else:
                    st.error("Failed to generate diet plan. Please try again.")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the server: {e}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Regenerate diet plan
if "response" in locals() and response["success"]:
    st.subheader("Not satisfied? Regenerate your plan!")
    query = st.text_input("What would you like to change?",
                          placeholder="e.g., more protein, less carbs")
    if st.button("Regenerate"):
        with st.spinner("Regenerating your diet plan..."):
            try:
                regenerate_response = requests.post(
                    f"{API_URL}/regenerate",
                    json={"query": query, "user_profile": user_profile,
                          "prev_response": response["response"]}
                ).json()
                if regenerate_response["success"]:
                    st.success("Diet plan regenerated successfully!")
                    st.subheader("Your New Diet Plan")
                    st.json(regenerate_response["response"])
                else:
                    st.error("Failed to regenerate diet plan. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
