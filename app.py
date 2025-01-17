import streamlit as st
from ai import App, User

ai = App()

st.set_page_config(page_title="Diet Plan Generator",
                   page_icon="🍽️", layout="wide")

st.title("🍽️ Diet Plan Generator")
st.markdown(
    "Generate a personalized diet plan based on your preferences and goals.")


def calculate_bmi(height, weight):
    return weight / ((height / 100) ** 2)


# Initialize session state variables
if "response" not in st.session_state:
    st.session_state.response = None
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None

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

        if height > 0 and weight > 0:
            bmi = calculate_bmi(height, weight)
            st.metric("BMI", f"{bmi:.1f}")
            if bmi < 18.5:
                st.warning(
                    "You are underweight. Consider increasing your calorie intake.")
            elif 18.5 <= bmi <= 24.9:
                st.success("Your weight is normal. Keep it up!")
            elif 25 <= bmi <= 29.9:
                st.warning(
                    "You are overweight. Consider reducing your calorie intake.")
            else:
                st.error(
                    "You are obese. Please consult a doctor for a personalized plan.")

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

if submitted:
    if not name or not diet_type or not cuisine:
        st.error("Please fill in all required fields.")
    else:
        user_profile = User(
            id="1",
            name=name,
            age=age,
            gender=gender,
            height=height,
            weight=weight,
            diet_type=diet_type,
            cuisine=cuisine,
            allergies=allergies if "none" not in allergies else None,
            calorie_goal=calorie_goal
        )

        with st.spinner("Generating your personalized diet plan..."):
            try:
                response = ai.generate_response(user_profile)
                if response:
                    st.session_state.response = response
                    st.session_state.user_profile = user_profile
                    st.success("Diet plan generated successfully!")
                    st.subheader("Your Diet Plan")

                    for meal in response["meals"]:
                        with st.container():
                            st.markdown(f"### {meal['name']}")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Calories", f"{
                                          meal['calories']} kcal")
                            with col2:
                                st.metric("Protein", f"{meal['protein']}g")
                            with col3:
                                st.metric("Carbs", f"{meal['carbs']}g")
                            with col4:
                                st.metric("Fat", f"{meal['fat']}g")
                            st.markdown("---")
                else:
                    st.error("Failed to generate diet plan. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {e}")


if st.session_state.response:
    st.subheader("Not satisfied? Regenerate your plan!")
    query = st.text_input(
        "What would you like to change?",
        placeholder="e.g., more protein, less carbs, different cuisine"
    )
    if st.button("Regenerate"):
        with st.spinner("Regenerating your diet plan..."):
            try:
                regenerate_response = ai.regenerate_response(
                    query, st.session_state.user_profile, st.session_state.response
                )
                if regenerate_response:
                    st.session_state.response = regenerate_response
                    st.success("Diet plan regenerated successfully!")
                    st.subheader("Your New Diet Plan")

                    for meal in regenerate_response["meals"]:
                        with st.container():
                            st.markdown(f"### {meal['name']}")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Calories", f"{
                                          meal['calories']} kcal")
                            with col2:
                                st.metric("Protein", f"{meal['protein']}g")
                            with col3:
                                st.metric("Carbs", f"{meal['carbs']}g")
                            with col4:
                                st.metric("Fat", f"{meal['fat']}g")
                            st.markdown("---")
                else:
                    st.error("Failed to regenerate diet plan. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
