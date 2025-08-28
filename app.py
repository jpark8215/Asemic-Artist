import gradio as gr
import ollama
import tempfile
import re
import random

# --- System Prompt (safety + style) ---
SYSTEM_PROMPT = """
You are an Asemic Artist AI.
You design abstract, symbolic calligraphic "entities" as SVG.
Rules:
- Output ONLY valid <svg>…</svg> markup.
- Use <g> groups for structure.
- Colors must come from the given palette.
- Stroke width must follow user input.
- Be creative, surreal, and unexpected.
- Never output scripts, links, or external references.
"""

# --- Wild prompts for "Surprise Me" ---
SURPRISE_PROMPTS = [
    "A cathedral made of dreams, collapsing into music",
    "A serpent eating its own tail while turning into galaxies",
    "Whispers of forgotten alphabets drifting through clouds",
    "A library where books melt into rivers of ink",
    "An insect choir performing in a glass cathedral",
    "The blueprint of an impossible machine fueled by silence",
    "A dance between geometry and chaos inside a crystal cube",
    "Fragments of shattered constellations writing themselves",
    "A mask made of shifting languages and broken mirrors",
    "An ocean wave folding into the shape of an eye",
    "A tree growing upside down, roots reaching for the sky",
    "A clockwork god, dreaming of impossible geometry",
    "A labyrinth that rearranges itself with every step",
    "A phoenix rising from pages of ancient scripts",
    "A bridge woven from threads of light and shadow",
    "A cityscape built from the echoes of forgotten songs", 
    "A dance of fractals unfolding into infinity",
    "A mosaic of broken dreams forming a new reality",
    "A spiral staircase leading to a door that doesn't exist",
    "A constellation map of lost memories and hidden desires"
]

# --- Backend Function ---
def generate_asemic_svg(prompt: str, model: str, chosen_colors: list, stroke_width: float, remix: bool):
    """
    Two-step process: blueprint -> final SVG render.
    """
    color_map = {
        "Black": "#000000", "Crimson Red": "#DC143C", "Forest Green": "#228B22",
        "Royal Blue": "#4169E1", "Gold": "#FFD700", "Deep Purple": "#4B0082",
        "Teal": "#008080", "Magenta": "#FF00FF", "Orange": "#FF8C00",
        "Sky Blue": "#87CEEB", "Emerald": "#50C878"
    }
    if not chosen_colors:
        chosen_colors = ["Black"]
    color_info = ", ".join([f"{name} ({color_map.get(name)})" for name in chosen_colors])

    # Step 1: Generate Blueprint
    blueprint_prompt = f"""
    Design a conceptual blueprint (in XML-like structure) for an Asemic Entity based on:
    "{prompt}".
    Use these palette colors: {color_info}.
    Output ONLY the XML blueprint.
    """
    try:
        blueprint_response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": "You design abstract blueprints in XML-like format."},
                {"role": "user", "content": blueprint_prompt}
            ]
        )
        blueprint = blueprint_response['message']['content']

        # Step 2: Render SVG
        render_prompt = f"""
        Blueprint:
        {blueprint}

        Render this into a highly detailed, surreal SVG.
        Use only these colors: {color_info}.
        Base stroke width: {stroke_width}.
        Group components with <g>.
        Add subtle path variations and layered textures.
        Animate a few parts using <animate> or <animateTransform> for unexpected liveliness.
        Output ONLY raw SVG.
        """
        if remix:
            render_prompt += f"\nRemix mode: Randomly introduce surprising geometry (fractals, recursive curves, impossible shapes)."

        final_response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": render_prompt}
            ]
        )
        raw_output = final_response['message']['content']

        match = re.search(r"<svg.*?</svg>", raw_output, re.DOTALL)
        if match:
            svg_content = match.group(0)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".svg", mode="w", encoding="utf-8") as tmp:
                tmp.write(svg_content)
                file_path = tmp.name
            return svg_content, file_path, blueprint
        else:
            return "<p style='color:red'>❌ Failed to extract valid SVG.</p>", None, blueprint

    except Exception as e:
        return f"<p style='color:red'>❌ Error: {e}</p>", None, "Error during generation."


# --- Surprise Me function ---
def surprise_prompt():
    return random.choice(SURPRISE_PROMPTS)


# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft(), title="🎭 Asemic Artist") as app:
    gr.Markdown("# 🎭 Asemic Artist")
    gr.Markdown("Enter a concept or hit **Surprise Me**. The artist will design a blueprint and then render a surreal, animated SVG entity.")

    with gr.Row():
        with gr.Column(scale=2):
            prompt_input = gr.Textbox(label="Creative Prompt", placeholder="e.g., 'A cathedral made of dreams, collapsing into music'", lines=3)
            surprise_button = gr.Button("🎲 Surprise Me")
            model_selector = gr.Dropdown(
                label="Select Model",
                choices=["gpt-oss:20b"],  # extendable
                value="gpt-oss:20b"
            )
            color_selector = gr.CheckboxGroup(
                label="Choose Palette Colors",
                choices=["Black", "Crimson Red", "Forest Green", "Royal Blue", "Gold", "Deep Purple",
                         "Teal", "Magenta", "Orange", "Sky Blue", "Emerald"],
                value=["Black", "Gold"]
            )
            stroke_slider = gr.Slider(label="Base Stroke Width", minimum=0.5, maximum=5.0, step=0.1, value=1.5)
            generate_button = gr.Button("✨ Generate Entity", variant="primary")

        with gr.Column(scale=3):
            output_display = gr.HTML(label="Generated Entity")
            output_file = gr.File(label="⬇️ Download SVG")
            blueprint_display = gr.Code(label="AI Blueprint", language="html")

    generate_button.click(
        fn=generate_asemic_svg,
        inputs=[prompt_input, model_selector, color_selector, stroke_slider],
        outputs=[output_display, output_file, blueprint_display]
    )

    surprise_button.click(
        fn=surprise_prompt,
        inputs=[],
        outputs=[prompt_input]
    )

    gr.Markdown("---")
    gr.Markdown("Unexpected asemic creations powered by open models.")

# --- Launch ---
app.launch()