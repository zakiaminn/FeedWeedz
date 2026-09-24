import html
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

st.set_page_config(page_title="FeedWeedz", page_icon="icon.png", layout="centered")

# --- making it cute bc she deserves cute ---
st.markdown("""
<style>
    /* round bubbly font, the default one was too serious */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600&display=swap');

    /* soft pink blobs in the background so it's not just flat */
    .stApp {
        background-color: #FFF5F7;
        background-image:
            radial-gradient(circle at 8% 12%, #FFEAEE 0, #FFEAEE 140px, transparent 141px),
            radial-gradient(circle at 95% 30%, #FFEAEE 0, #FFEAEE 90px, transparent 91px),
            radial-gradient(circle at 90% 88%, #FFD3DA55 0, #FFD3DA55 160px, transparent 161px),
            radial-gradient(circle at 4% 70%, #FFEAEE 0, #FFEAEE 70px, transparent 71px);
        background-attachment: fixed;
        color: #5D4037;
    }

    html, body, [class*="st-"], p, h1, h2, h3, h4, h5, h6, button, textarea {
        font-family: 'Fredoka', sans-serif !important;
    }

    /* hide streamlit's top bar */
    header[data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none; }

    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 760px !important;
    }

    /* the big title */
    h1.main-title, .main-title {
        color: #FF8BA7 !important;
        padding: 0 !important;
        text-align: center;
        font-size: clamp(3rem, 12vw, 4.8rem);
        font-weight: 600;
        line-height: 1;
        margin: 0.5rem 0 1rem 0;
        letter-spacing: 1px;
        text-shadow: 3px 3px 0px #FFD3DA;
    }
    h1.main-title a, [data-testid="stHeaderActionElements"] { display: none !important; }

    /* little pill under the title */
    .subtitle-wrap { text-align: center; margin-bottom: 2rem; }
    .subtitle {
        display: inline-block;
        background: #FFFFFF;
        color: #B48484;
        border: 2px solid #FFD3DA;
        border-radius: 50px;
        padding: 0.45rem 1.3rem;
        font-size: 1.1rem;
        font-weight: 500;
    }

    /* white cards (the input one and the recipe ones) */
    .st-key-input-card, [class*="st-key-recipe-"] {
        background-color: #FFFFFF;
        border-radius: 28px !important;
        padding: 1.6rem 1.5rem !important;
        border: 3px solid #FFEAEE !important;
        box-shadow: 0 10px 25px rgba(255, 139, 167, 0.12);
    }

    /* labels on the text box + slider */
    [data-testid="stWidgetLabel"] p {
        color: #FF8BA7 !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
    }

    /* the box where she types her sad little grocery list */
    .stTextArea textarea {
        background-color: #FFF5F7 !important;
        border: 3px solid #FFD3DA !important;
        border-radius: 20px !important;
        color: #5D4037 !important;
        padding: 15px !important;
        font-size: 1.1rem !important;
    }
    .stTextArea textarea::placeholder { color: #B48484 !important; opacity: 0.7; }
    .stTextArea textarea:focus {
        border-color: #FF8BA7 !important;
        box-shadow: 0 0 0 4px rgba(255, 139, 167, 0.2) !important;
    }
    .stTextArea [data-baseweb="textarea"], .stTextArea [data-baseweb="base-input"] {
        border: none !important;
        background: transparent !important;
    }

    /* slider numbers */
    .stSlider [data-testid="stSliderTickBar"], .stSlider div[data-baseweb="tick-bar"] { color: #B48484 !important; }
    .stSlider [data-testid="stSliderThumbValue"] { color: #FF8BA7 !important; font-weight: 600; }

    /* the button, it bounces when you press it hehe */
    div.stButton > button {
        background-color: #FF8BA7 !important;
        color: white !important;
        border: none !important;
        width: 100%;
        padding: 0.8rem;
        border-radius: 50px;
        box-shadow: 0 5px 0px #E56A89 !important;
        transition: all 0.2s ease;
        margin-top: 0.5rem;
    }
    div.stButton > button p { font-size: 1.3rem !important; font-weight: 600 !important; letter-spacing: 0.5px; }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 0px #E56A89 !important;
    }
    div.stButton > button:active {
        transform: translateY(3px);
        box-shadow: 0 2px 0px #E56A89 !important;
    }

    /* loading text */
    [data-testid="stSpinner"] p { color: #B48484 !important; font-size: 1.1rem !important; }

    /* cute little message box instead of streamlit's yellow/red ones */
    .note {
        background: #FFFFFF;
        border: 3px dashed #FFD3DA;
        border-radius: 20px;
        padding: 1rem 1.3rem;
        color: #7A5C53;
        text-align: center;
        font-size: 1.1rem;
        margin-top: 1.2rem;
    }

    /* heading above the recipes */
    .results-title {
        color: #FF8BA7;
        text-align: center;
        font-size: 2rem;
        font-weight: 600;
        line-height: 1.2;
        margin: 2.5rem 0 0.4rem 0;
        text-shadow: 2px 2px 0px #FFD3DA;
    }
    .dots { text-align: center; margin-bottom: 1.5rem; }
    .dots span {
        display: inline-block; width: 9px; height: 9px; border-radius: 50%;
        background: #FFD3DA; margin: 0 4px;
    }
    .dots span:nth-child(2) { background: #FF8BA7; }

    /* recipe cards */
    .recipe-head { display: flex; align-items: flex-start; gap: 0.9rem; margin-bottom: 0.9rem; }
    .recipe-num {
        flex: none; width: 2.6rem; height: 2.6rem; border-radius: 50%;
        background: #FFF0F3; color: #FF8BA7; border: 3px solid #FFD3DA;
        display: flex; align-items: center; justify-content: center;
        font-weight: 600; font-size: 1.2rem;
    }
    .recipe-title { color: #FF8BA7; font-size: 1.6rem; font-weight: 600; line-height: 1.2; margin: 0 0 0.35rem 0; }
    .time-pill {
        display: inline-block; background: #FFF0F3; color: #B48484;
        border-radius: 50px; padding: 0.15rem 0.8rem; font-size: 0.95rem; font-weight: 500;
    }

    .harmony-box {
        background-color: #FFF0F3;
        padding: 0.9rem 1.2rem;
        border-radius: 18px;
        border-left: 5px solid #FF8BA7;
        margin-bottom: 1.3rem;
        color: #7A5C53;
        font-weight: 500;
    }

    .recipe-body { display: grid; grid-template-columns: 1fr 2fr; gap: 1.5rem; }
    @media (max-width: 640px) { .recipe-body { grid-template-columns: 1fr; gap: 1rem; } }

    .section-label { color: #FF8BA7; font-size: 1.15rem; font-weight: 600; margin: 0 0 0.6rem 0; }

    .ing-list, .step-list { list-style: none; padding: 0 !important; margin: 0 !important; }
    .ing-list li, .step-list li { margin-left: 0 !important; padding-left: 0; }
    .ing-list li {
        color: #5D4037; padding: 0.35rem 0; border-bottom: 2px dotted #FFEAEE;
        display: flex; gap: 0.5rem; align-items: baseline;
    }
    .ing-list li:last-child { border-bottom: none; }
    .ing-list li::before {
        content: ""; flex: none; width: 8px; height: 8px; border-radius: 50%;
        background: #FFD3DA; transform: translateY(-1px);
    }
    .ing-qty { color: #B48484; font-weight: 600; }

    .step-list li { display: flex; gap: 0.75rem; margin-bottom: 0.8rem; color: #5D4037; line-height: 1.5; }
    .step-num {
        flex: none; width: 1.7rem; height: 1.7rem; border-radius: 50%;
        background: #FF8BA7; color: #FFFFFF; font-weight: 600; font-size: 0.9rem;
        display: flex; align-items: center; justify-content: center; margin-top: 0.1rem;
    }

    .footer-love { text-align: center; color: #B48484; margin-top: 2.5rem; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)

# --- telling gemini exactly what shape the recipes should come back in ---
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

# --- setup stuff ---
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"],
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(attempts=2, initial_delay=1.0)
    )
)

# turns one recipe into a card (html.escape so weird gemini text can't break the page)
def recipe_card(num, recipe):
    e = html.escape
    ingredients_html = "".join(
        f'<li><span><span class="ing-qty">{e(ing.quantity)}</span> {e(ing.name)}</span></li>'
        for ing in recipe.ingredients
    )
    steps_html = "".join(
        f'<li><span class="step-num">{i}</span><span>{e(step)}</span></li>'
        for i, step in enumerate(recipe.instructions, 1)
    )
    return (
        f'<div class="recipe-head"><div class="recipe-num">{num}</div><div>'
        f'<div class="recipe-title">{e(recipe.title)}</div>'
        f'<span class="time-pill">ready in {recipe.prep_time} min</span></div></div>'
        f'<div class="harmony-box"><strong>Why it\'s good:</strong> {e(recipe.why_it_works)}</div>'
        f'<div class="recipe-body">'
        f'<div><div class="section-label">Ingredients</div><ul class="ing-list">{ingredients_html}</ul></div>'
        f'<div><div class="section-label">Instructions</div><ol class="step-list">{steps_html}</ol></div>'
        f'</div>'
    )

def note(text):
    st.markdown(f'<div class="note">{html.escape(text)}</div>', unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Feed Weedz</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-wrap"><span class="subtitle">Kya chahye aap ko aaj werdah?</span></div>', unsafe_allow_html=True)

# where she tells me what she has
with st.container(key="input-card"):
    ingredients = st.text_area(
        "put your very scarce grocery here",
        placeholder="e.g. zaki, pasta, boiled chicken ew",
        height=130
    )

    time = st.select_slider("how long can you stay in the kitchen?", options=[15, 30, 45, 60, 120], value=45)

    generate_btn = st.button("GIVE ME RECIPES, ZAKI", use_container_width=True)

# --- the actual cooking part ---
if generate_btn:
    if ingredients:
        with st.spinner("okay giving and since you're picky, it's gonna take a sec love"):

            # what i tell the chef
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
                        temperature=0.8, # a lil creative but not unhinged
                    ),
                )

                result = RecipeCollection.model_validate_json(response.text)

                st.markdown('<div class="results-title">mere dimaagh ke illawa ye khalo aaj instead</div>', unsafe_allow_html=True)
                st.markdown('<div class="dots"><span></span><span></span><span></span></div>', unsafe_allow_html=True)

                # --- showing her the recipes ---
                for num, recipe in enumerate(result.recipes, 1):
                    with st.container(key=f"recipe-{num}"):
                        st.markdown(recipe_card(num, recipe), unsafe_allow_html=True)

                st.markdown('<div class="footer-love">made with love (and your empty fridge)</div>', unsafe_allow_html=True)

            except Exception as e:
                note(f"sorry werdah the kitchen's busy {e}")
    else:
        note("You can't make food without food werdah")
