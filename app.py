import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import base64 

st.set_page_config(page_title="FeedWeedz", page_icon="icon.png", layout="wide")

# --- Custom App Icon Hack ---
def set_mobile_icon(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            
        st.markdown(f"""
            <style>
                /* Hidden div to contain the meta tags */
                .mobile-icon-hack {{ display: none; }}
            </style>
            <div class="mobile-icon-hack">
                <link rel="apple-touch-icon" href="data:image/png;base64,{encoded_string}">
                <link rel="icon" href="data:image/png;base64,{encoded_string}">
            </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        pass # If the image is missing, the app won't crash

# Call the function
set_mobile_icon("icon.png")

st.set_page_config(page_title="FeedWeedz", layout="wide")

# --- Custom CSS for the "Cute & Playful" Aesthetic ---
st.markdown("""
<style>
    /* Import a cute, rounded font from Google */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600&display=swap');

    .stApp {
        background-color: #FFF5F7; 
        color: #5D4037; 
    }

    html, body, [class*="st-"], p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Fredoka', sans-serif !important;
    }

    /* Main Title Specifics */
    .main-title {
        color: #FF8BA7; 
        text-align: center;
        font-size: clamp(3rem, 10vw, 4.5rem);
        font-weight: 600;
        margin-top: 1rem;
        text-shadow: 2px 2px 0px #FFD3DA; 
    }
    
    .subtitle {
        text-align: center;
        color: #B48484; 
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }

    /* Fix: Text Area Input */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        border: 3px solid #FFD3DA !important;
        border-radius: 20px !important; 
        color: #5D4037 !important;
        padding: 15px !important;
        font-size: 1.1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #FF8BA7 !important;
        box-shadow: 0 0 0 3px rgba(255, 139, 167, 0.2) !important;
    }

    /* Fix: Slider Labels */
    .stSlider [data-testid="stWidgetLabel"] p {
        color: #FF8BA7 !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    .stSlider div[data-baseweb="tick-bar"] {
        color: #5D4037 !important;
    }

    /* Recipe Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border-radius: 25px; 
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 3px solid #FFEAEE !important;
        box-shadow: 0 8px 15px rgba(255, 139, 167, 0.1);
    }

    /* Buttons */
    div.stButton > button {
        background-color: #FF8BA7 !important;
        color: white !important;
        border: none !important;
        width: 100%; 
        padding: 0.8rem;
        font-size: 1.3rem;
        font-weight: 600;
        border-radius: 50px; 
        box-shadow: 0 4px 0px #E56A89 !important; 
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 7px 0px #E56A89 !important;
    }
    
    div.stButton > button:active {
        transform: translateY(2px); 
        box-shadow: 0 2px 0px #E56A89 !important;
    }

    .harmony-box {
        background-color: #FFF0F3;
        padding: 1rem 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #FF8BA7;
        margin-bottom: 1.5rem;
        color: #7A5C53;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. The Blueprint (Structured Output) ---
class Ingredient(BaseModel):
    name: str = Field(description="Name of the ingredient.")
    quantity: str = Field(description="Quantity, including units.")

class Recipe(BaseModel):
    title: str = Field(description="A fun, cute, and appetizing title for the dish.")
    prep_time: int = Field(description="Total time in minutes.")
    why_it_works: str = Field(description="A friendly, 1-sentence explanation of why these ingredients taste great together.")
    ingredients: list[Ingredient]
    instructions: list[str] = Field(description="Numbered step-by-step instructions. Keep the tone light and easy to follow.")

class RecipeCollection(BaseModel):
    recipes: list[Recipe] = Field(description="Exactly 5 distinct recipes based on the input.")

# --- 2. App Setup ---
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"],
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(attempts=2, initial_delay=1.0)
    )
)

st.markdown('<h1 class="main-title">Feed Weedz</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Kya chahye aap ko aaj werdah?</p>', unsafe_allow_html=True)

# Main centered input area 
with st.container():
    ingredients = st.text_area(
        "put your very scarce grocery here", 
        placeholder="e.g. zaki, pasta, boiled chicken ew",
        height=130
    )
    
    time = st.select_slider("how long can you stay in the kitchen?", options=[15, 30, 45, 60, 120], value=45)
    
    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("GIVE ME RECIPES, ZAKI", use_container_width=True)

# --- 3. Generation and UI ---
if generate_btn:
    if ingredients:
        with st.spinner("okay giving and since you're picky, it's gonna take a sec love"):
            
            # prompt
            prompt = f"""
            You are a friendly, upbeat personal chef creating a fun menu for Weedz.
            Available ingredients: {ingredients}
            Maximum time: {time} minutes.
            
            CRITICAL RULES:
            1. Provide exactly 5 distinct recipe options.
            2. Assume she has basic pantry staples (salt, pepper, olive oil, water).
            3. The tone should be super friendly, upbeat, and casual (not stiff or corporate).
            4. ABSOLUTELY NO EMOJIS anywhere in the output.
            """
            
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RecipeCollection,
                        temperature=0.8, # temp for creativity
                    ),
                )
                
                result = RecipeCollection.model_validate_json(response.text)
                
                st.markdown('<p class="main-title" style="font-size: 2.5rem; margin-top: 2rem;"> mere dimaagh ke illawa ye khalo aaj instead</p>', unsafe_allow_html=True)
                
                # --- 4. Cute Recipe Cards ---
                for recipe in result.recipes:
                    with st.container(border=True):
                        st.markdown(f"<h2 style='color: #FF8BA7; margin-top: 0;'>{recipe.title}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #B48484; font-weight: 500; margin-bottom: 1rem;'>Ready in {recipe.prep_time} minutes</p>", unsafe_allow_html=True)
                        
                        st.markdown(f'''
                        <div class="harmony-box">
                            <strong>Why it's good:</strong> {recipe.why_it_works}
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        col_ing, col_inst = st.columns([1, 2])
                        
                        with col_ing:
                            st.markdown("<h3 style='color: #FF8BA7;'>Ingredients</h3>", unsafe_allow_html=True)
                            for ing in recipe.ingredients:
                                st.markdown(f"- **{ing.quantity}** {ing.name}")
                                
                        with col_inst:
                            st.markdown("<h3 style='color: #FF8BA7;'>Instructions</h3>", unsafe_allow_html=True)
                            for step_num, step_text in enumerate(recipe.instructions, 1):
                                st.markdown(f"**{step_num}.** {step_text}")
                                
            except Exception as e:
                st.error(f"sorry werdah the kitchen's busy {e}")
    else:
        st.warning("You can't make food without food werdah")