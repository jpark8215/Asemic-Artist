import gradio as gr
import tempfile
import re
import random
import time
from pathlib import Path
from huggingface_hub import InferenceClient
import os

# Hugging Face API Token (set in Space "Repository secrets")
HF_TOKEN = os.environ.get("HF_TOKEN")
client = InferenceClient(token=HF_TOKEN)

# --- System Prompt ---
SYSTEM_PROMPT = """
You are an Asemic Master Artist AI specializing in creating breathtaking, otherworldly SVG entities.
CRITICAL RULES:
- Output ONLY valid <svg>...</svg> markup, nothing else
- Create complex, layered compositions with multiple <g> groups
- Use flowing, organic shapes combined with geometric precision  
- Add subtle animations using <animate>, <animateTransform>, or <animateMotion>
- Employ gradients, patterns, and sophisticated color relationships
- Create depth through layering, opacity, and stroke variations
- Make it visually stunning - something that would stop viewers in their tracks
TECHNICAL REQUIREMENTS:
- Viewport: 600x600 minimum
- Use provided colors only
- Vary stroke widths (base ± 0.5 to base × 3)
- Include at least 3-5 animated elements
- Create visual hierarchy through scale and positioning
"""

# --- Surprise prompts ---
SURPRISE_PROMPTS = [
    "A cosmic jellyfish swimming through dimensions of crystallized time",
    "Ancient runes dissolving into butterflies made of liquid starlight", 
    "A mechanical heart pumping rivers of aurora through crystal veins",
    "Fragments of forgotten symphonies crystallizing into geometric flowers",
    "A dragon made of intertwining calligraphy breathing mathematical equations",
    "Portals to parallel worlds opening like blossoming ink flowers",
    "A lighthouse made of pure mathematics guiding ships through thought-storms",
    "Celestial clockwork gears grinding out new constellations",
    "A tree of knowledge with books for leaves, stories for roots",
    "Quantum butterflies emerging from shattered mirror dimensions",
    "A phoenix composed of flowing scripts rising from paper ashes",
    "Architectural blueprints for impossible cities floating in void",
    "Molecular structures blooming into abstract garden mazes",
    "A compass rose navigating through seas of liquid typography",
    "Sacred geometry temples built from crystallized music",
    "Metamorphic alphabets evolving into cybernetic organisms",
    "A spiral galaxy of interconnected neural pathways and dreams",
    "Ancient symbols transforming into futuristic biotechnology",
    "Fractal mantras spinning through digital prayer wheels",
    "A cosmic dance between order and chaos in pure visual form",
    "Ethereal creatures emerging from algorithmic poetry",
    "A map of consciousness drawn with threads of pure light",
    "Transforming pictographs that bridge reality and imagination",
    "A symphony of shapes conducting themselves through space-time",
    "Living calligraphy that writes itself across dimensional boundaries"
]

def query_model(model, system_prompt, user_prompt):
    """Call Hugging Face Inference API chat completion"""
    response = client.chat_completion(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2048,
        temperature=0.8,
    )
    return response.choices[0].message["content"]

def generate_asemic_svg(prompt: str, model: str, chosen_colors: list, stroke_width: float, complexity: str, max_retries=5):
    color_map = {
        "Black": "#000000", "Crimson Red": "#DC143C", "Forest Green": "#228B22",
        "Royal Blue": "#4169E1", "Gold": "#FFD700", "Deep Purple": "#4B0082",
        "Teal": "#008080", "Magenta": "#FF00FF", "Orange": "#FF8C00",
        "Sky Blue": "#87CEEB", "Emerald": "#50C878", "Midnight Blue": "#191970",
        "Coral": "#FF7F50", "Sage Green": "#9CAF88", "Burgundy": "#800020",
        "Copper": "#B87333", "Lavender": "#E6E6FA", "Turquoise": "#40E0D0",
        "Rose Gold": "#E8B4B8", "Chartreuse": "#7FFF00", "Indigo": "#4B0082",
        "Salmon": "#FA8072", "Olive": "#808000", "Silver": "#C0C0C0",
        "Maroon": "#800000", "Navy": "#000080", "Lime": "#00FF00",
        "Fuchsia": "#FF00FF", "Aqua": "#00FFFF", "Pearl": "#F8F8FF",
        "Onyx": "#353839", "Amber": "#FFBF00"
    }

    if not chosen_colors:
        chosen_colors = ["Black", "Gold"]

    color_palette = [f"{name}({color_map[name]})" for name in chosen_colors if name in color_map]
    color_info = ", ".join(color_palette)

    complexity_settings = {
        "Simple": {"elements": "3-5 main elements", "animations": "1-2 subtle animations", "detail": "clean, minimal details"},
        "Moderate": {"elements": "5-8 layered elements", "animations": "3-4 synchronized animations", "detail": "moderate complexity with patterns"},
        "Complex": {"elements": "8-12+ intricate elements", "animations": "5+ dynamic animations", "detail": "maximum detail with gradients, patterns, and layering"}
    }
    settings = complexity_settings.get(complexity, complexity_settings["Moderate"])

    enhanced_prompt = f"""
Create a visually stunning asemic art in SVG code ONLY based on: "{prompt}"
SPECIFICATIONS:
- Colors: {color_info}
- Base stroke width: {stroke_width}
- Complexity: {settings['elements']}, {settings['animations']}, {settings['detail']}
- Canvas: 600x600 viewBox
- Style: Flowing, organic, otherworldly, sophisticated
MANDATORY ELEMENTS:
1. Use <defs> with gradients
2. Create {settings['elements']} with varied stroke-width from {stroke_width*0.5} to {stroke_width*3}
3. Add {settings['animations']} using <animate>, <animateTransform>
4. Layer elements with <g> groups and varying opacity (0.3-1.0)
5. Include flowing paths, organic shapes, and geometric accents
6. Create visual depth through layering and scale variation
Output ONLY the complete SVG code.
"""

    attempt = 0
    while attempt < max_retries:
        try:
            start_time = time.time()
            raw_output = query_model(model, SYSTEM_PROMPT, enhanced_prompt)
            generation_time = time.time() - start_time

            svg_match = re.search(r'<svg[^>]*>[\s\S]*?</svg>', raw_output, re.IGNORECASE)
            if svg_match:
                svg_content = svg_match.group(0)
                # Ensure viewport and size
                if 'viewBox' not in svg_content:
                    svg_content = svg_content.replace('<svg', '<svg viewBox="0 0 600 600"', 1)
                if 'width' not in svg_content and 'height' not in svg_content:
                    svg_content = svg_content.replace('<svg', '<svg width="600" height="600"', 1)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".svg", mode="w", encoding="utf-8") as tmp:
                    tmp.write(svg_content)
                    file_path = tmp.name

                return svg_content, file_path, f"Generated in {generation_time:.1f} seconds using {model} (attempt {attempt+1})"

            else:
                attempt += 1  # Retry if no SVG
        except Exception as e:
            attempt += 1
            if attempt >= max_retries:
                fallback_svg = """
                <svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
                    <rect width="600" height="600" fill="white"/>
                    <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
                          font-size="24" fill="red">[Error: {}</text>
                </svg>
                """.format(str(e))
                return fallback_svg, None, f"Error after {attempt} attempts: {str(e)}"

    # If all retries fail
    fallback_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
        <rect width="600" height="600" fill="white"/>
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
              font-size="24" fill="red">[No valid SVG found]</text>
    </svg>
    """
    return fallback_svg, None, f"No valid SVG after {max_retries} attempts"


def surprise_prompt():
    return random.choice(SURPRISE_PROMPTS)



# --- Gradio UI ---
with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="purple", secondary_hue="blue", neutral_hue="slate"), 
    title="Asemic Artist",
    css="""
    /* Add a subtle transition for the accordion */
    .gradio-accordion { transition: all 0.2s ease-in-out; }
    """
) as app:
    
    gr.Markdown(
        """
        # Asemic Artist
        ### Create abstract visual entities powered by AI
        *Enter a concept or hit **Surprise Me** for otherworldly asemic art*
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            with gr.Tabs():
                # --- Tab 1: The core creative input ---
                with gr.TabItem("Vision", id=0):
                    with gr.Group():
                        prompt_input = gr.Textbox(label="Creative Vision", placeholder="Describe your ethereal concept...", lines=5)
                        with gr.Row():
                            surprise_button = gr.Button("Surprise Me", variant="secondary")
                            clear_button = gr.Button("Clear", variant="secondary")
                
                # --- Tab 2: All the fine-tuning controls ---
                with gr.TabItem("Style & Details", id=1):
                    with gr.Group():
                        model_selector = gr.Dropdown(
                            label="AI Model",
                            choices=["openai/gpt-oss-20b", "openai/gpt-oss-120b", "mistralai/Mixtral-8x7B-Instruct-v0.1"], 
                            value="openai/gpt-oss-20b"
                        )
                        complexity_slider = gr.Radio(
                            label="Complexity Level",
                            choices=["Simple", "Moderate", "Complex"],
                            value="Moderate"
                        )
                        stroke_slider = gr.Slider(label="Base Stroke Width", minimum=0.5, maximum=5.0, step=0.1, value=1.5)

                    with gr.Accordion("Color Palette (Select 2-5)", open=False):
                        color_selector = gr.CheckboxGroup(
                            label="Color Palette",
                            choices=[
                                # Neutrals
                                "Black", "Onyx", "Silver", "Pearl",
                                # Reds & Pinks
                                "Crimson Red", "Burgundy", "Maroon", "Coral", "Salmon", "Rose Gold",
                                # Blues
                                "Royal Blue", "Midnight Blue", "Navy", "Sky Blue", "Turquoise", "Aqua", "Teal",
                                # Greens
                                "Forest Green", "Sage Green", "Emerald", "Lime", "Chartreuse", "Olive",
                                # Purples & Pinks
                                "Deep Purple", "Indigo", "Lavender", "Magenta", "Fuchsia",
                                # Oranges & Yellows
                                "Orange", "Amber", "Gold", "Copper"
                            ],
                            value=["Black", "Gold", "Deep Purple"]
                        )
            
            generate_button = gr.Button("Generate Asemic Entity", variant="primary", size="lg")

        with gr.Column(scale=3):
            with gr.Group():
                output_display = gr.HTML(label="Generated Entity", show_label=False)
                output_file = gr.File(label="Download SVG")
                generation_info = gr.Textbox(label="Generation Info", interactive=False)

    generate_button.click(
        fn=generate_asemic_svg,
        inputs=[prompt_input, model_selector, color_selector, stroke_slider, complexity_slider],
        outputs=[output_display, output_file, generation_info]
    )

    surprise_button.click(fn=surprise_prompt, outputs=[prompt_input])
    clear_button.click(fn=lambda: "", outputs=[prompt_input])


    with gr.Row():
        gr.Markdown(
            """
            ---
            **Asemic Art** *Writing without words, through pure visual form. Powered by language models and creative algorithms*
            """,
            elem_classes=["prose"]
    )

if __name__ == "__main__":
    app.launch()
