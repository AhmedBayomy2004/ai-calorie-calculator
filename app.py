import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Page setup
st.set_page_config(
    page_title="AI Calorie Calculator", page_icon="🍽️", layout="wide"
)

st.title("🍽️ AI Calorie & Nutrition Calculator")
st.caption(
    "Describe your meal in natural language (English or Arabic), and AI will"
    " calculate your calories and macros."
)

# Sidebar API Configuration
st.sidebar.header("⚙️ API Configuration")
api_url = st.sidebar.text_input(
    "Ngrok Public URL:", placeholder="https://xxxx.ngrok-free.app"
)

# Initialize session state
if "nutrition_data" not in st.session_state:
  st.session_state.nutrition_data = None
if "user_input" not in st.session_state:
  st.session_state.user_input = ""


# Quick meal prompt presets
def set_prompt(text):
  st.session_state.user_input = text


st.write(" **Quick Examples:**")
q_col1, q_col2, q_col3 = st.columns([1, 1, 2])
with q_col1:
  st.button(
      "🍳 2 Eggs & Apple",
      on_click=set_prompt,
      args=("2 boiled eggs and an apple",),
  )
with q_col2:
  st.button(
      "🍗 Chicken & Rice",
      on_click=set_prompt,
      args=("200g grilled chicken breast with 150g cooked rice",),
  )
with q_col3:
  st.button(
      "🇸🇦 sample in Arabic",
      on_click=set_prompt,
      args=("أكلت بيضتين مسلوقين وتفاحة وجبنة",),
  )

# User meal Input
user_input = st.text_area(
    "What did you eat today?",
    key="user_input",
    placeholder=(
        "e.g., I had 2 boiled eggs, an apple, and 200g of grilled chicken"
        " breast"
    ),
    height=90,
)

# Calculation trigger
if st.button("Calculate Calories & Macros 🚀", type="primary"):
  if not api_url:
    st.error("⚠️ Please enter the Ngrok API URL in the sidebar first!")
  elif not user_input.strip():
    st.warning("⚠️ Please describe your meal first.")
  else:
    with st.spinner("Analyzing meal and querying USDA database..."):
      try:
        endpoint = f"{api_url.strip('/')}/calculate"
        response = requests.post(
            endpoint, json={"user_input": user_input}, timeout=60
        )

        if response.status_code == 200:
          st.session_state.nutrition_data = response.json()
        else:
          st.error(f"Server Error ({response.status_code}): {response.text}")

      except Exception as e:
        st.error(
            "Failed to connect to the server. Make sure Ngrok is running and"
            f" active.\n\nError: {e}"
        )

# Display stored results if available
if st.session_state.nutrition_data:
  data = st.session_state.nutrition_data
  st.divider()

  st.success(f"📌 **Meal:** {data.get('dish_name', 'Meal Summary')}")

  totals = data["grand_totals"]

  # Split screen: Left side metrics + Right side macros chart
  col_metrics, col_chart = st.columns([3, 2])

  with col_metrics:
    m1, m2 = st.columns(2)
    m1.metric("🔥 Total Calories", f"{totals['total_calories']} kcal")
    m2.metric("🥩 Protein", f"{totals['total_protein_g']} g")

    m3, m4 = st.columns(2)
    m3.metric("🍞 Carbs", f"{totals['total_carbs_g']} g")
    m4.metric("🥑 Fat", f"{totals['total_fat_g']} g")

  with col_chart:
    # Donut Chart for Macro Split
    macro_df = pd.DataFrame({
        "Macro": ["Protein", "Carbs", "Fat"],
        "Grams": [
            totals["total_protein_g"],
            totals["total_carbs_g"],
            totals["total_fat_g"],
        ],
    })
    fig = px.pie(
        macro_df,
        values="Grams",
        names="Macro",
        hole=0.5,
        color_discrete_sequence=["#EF553B", "#636EFA", "#00CC96"],
        title="Macro Breakdown (Grams)",
    )
    fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=200)
    st.plotly_chart(fig, use_container_width=True)

  st.subheader("📋 Itemized Breakdown")

  breakdown = data["itemized_breakdown"]
  df = pd.DataFrame(breakdown)

  df_display = df.rename(
      columns={
          "ingredient": "Ingredient",
          "weight_grams": "Weight (g)",
          "calories": "Calories (kcal)",
          "protein_g": "Protein (g)",
          "carbs_g": "Carbs (g)",
          "fat_g": "Fat (g)",
          "matched_db_food": "USDA Matched Item",
      }
  )

  st.dataframe(
      df_display[[
          "Ingredient",
          "Weight (g)",
          "Calories (kcal)",
          "Protein (g)",
          "Carbs (g)",
          "Fat (g)",
          "USDA Matched Item",
      ]],
      use_container_width=True,
      hide_index=True,
  )