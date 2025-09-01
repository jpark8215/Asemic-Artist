import gradio as gr
import ollama
import tempfile
import re
import random
import threading
import socket
import time
import webbrowser
import sys
import os
from pathlib import Path

# Enhanced system prompt for better, more impressive output
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

# Expanded and more evocative prompts
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

def get_temp_dir():
    """Get appropriate temp directory for PyInstaller"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / 'temp'
    else:
        return Path(tempfile.gettempdir())

def generate_asemic_svg(prompt: str, model: str, chosen_colors: list, stroke_width: float, complexity: str):
    # Expanded color palette with more sophisticated options
    color_map = {
        # Original colors
        "Black": "#000000", "Crimson Red": "#DC143C", "Forest Green": "#228B22",
        "Royal Blue": "#4169E1", "Gold": "#FFD700", "Deep Purple": "#4B0082",
        "Teal": "#008080", "Magenta": "#FF00FF", "Orange": "#FF8C00",
        "Sky Blue": "#87CEEB", "Emerald": "#50C878",        
        "Midnight Blue": "#191970", "Coral": "#FF7F50", "Sage Green": "#9CAF88",
        "Burgundy": "#800020", "Copper": "#B87333", "Lavender": "#E6E6FA", 
        "Turquoise": "#40E0D0", "Rose Gold": "#E8B4B8", "Chartreuse": "#7FFF00",
        "Indigo": "#4B0082", "Salmon": "#FA8072", "Olive": "#808000",
        "Silver": "#C0C0C0", "Maroon": "#800000", "Navy": "#000080",
        "Lime": "#00FF00", "Fuchsia": "#FF00FF", "Aqua": "#00FFFF",
        "Pearl": "#F8F8FF", "Onyx": "#353839", "Amber": "#FFBF00"
    }
    
    if not chosen_colors:
        chosen_colors = ["Black", "Gold"]
    
    # Create color palette info with hex values
    color_palette = [f"{name}({color_map[name]})" for name in chosen_colors if name in color_map]
    color_info = ", ".join(color_palette)
    
    # Complexity settings
    complexity_settings = {
        "Simple": {
            "elements": "3-5 main elements",
            "animations": "1-2 subtle animations", 
            "detail": "clean, minimal details"
        },
        "Moderate": {
            "elements": "5-8 layered elements",
            "animations": "3-4 synchronized animations",
            "detail": "moderate complexity with patterns"
        },
        "Complex": {
            "elements": "8-12+ intricate elements", 
            "animations": "5+ dynamic animations",
            "detail": "maximum detail with gradients, patterns, and layering"
        }
    }
    
    settings = complexity_settings.get(complexity, complexity_settings["Moderate"])
    
    # Single, more efficient prompt that combines conceptual and technical requirements
    enhanced_prompt = f"""
Create a visually stunning asemic art SVG based on: "{prompt}"

SPECIFICATIONS:
- Colors: {color_info}
- Base stroke width: {stroke_width}
- Complexity: {settings['elements']}, {settings['animations']}, {settings['detail']}
- Canvas: 600x600 viewBox
- Style: Flowing, organic, otherworldly, sophisticated

MANDATORY ELEMENTS:
1. Use <defs> with gradients: <linearGradient> or <radialGradient>
2. Create {settings['elements']} with varied stroke-width from {stroke_width*0.5} to {stroke_width*3}
3. Add {settings['animations']} using <animate>, <animateTransform> 
4. Layer elements with <g> groups and varying opacity (0.3-1.0)
5. Include flowing paths, organic shapes, and geometric accents
6. Create visual depth through layering and scale variation

Make this a masterpiece that demonstrates the beauty of asemic art - something extraordinary and captivating.

Output ONLY the complete SVG code.
"""

    try:
        print(f"Generating {complexity.lower()} asemic entity...")
        start_time = time.time()
        
        # Single LLM call for efficiency
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": enhanced_prompt}
            ]
        )
        
        raw_output = response['message']['content']
        generation_time = time.time() - start_time
        
        # Extract SVG with better regex
        svg_match = re.search(r'<svg[^>]*>.*?</svg>', raw_output, re.DOTALL | re.IGNORECASE)
        if svg_match:
            svg_content = svg_match.group(0)
            
            # Ensure proper sizing if not present
            if 'viewBox' not in svg_content:
                svg_content = svg_content.replace('<svg', '<svg viewBox="0 0 600 600"', 1)
            if 'width' not in svg_content and 'height' not in svg_content:
                svg_content = svg_content.replace('<svg', '<svg width="600" height="600"', 1)
            
            # Save to temp file
            temp_dir = get_temp_dir()
            temp_dir.mkdir(exist_ok=True)
            
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".svg", mode="w", encoding="utf-8", dir=str(temp_dir)
            ) as tmp:
                tmp.write(svg_content)
                file_path = tmp.name
            
            print(f"Generated in {generation_time:.1f}s")
            return svg_content, file_path, f"Generated in {generation_time:.1f} seconds using {model}"
        
        else:
            return "<p style='color:red;'>Failed to extract valid SVG. The AI may not have followed the format.</p>", None, "Generation failed - no valid SVG found"

    except Exception as e:
        print(f"Generation error: {e}")
        return f"<p style='color:red;'>Error: {str(e)}</p>", None, f"Error during generation: {str(e)}"

def surprise_prompt():
    return random.choice(SURPRISE_PROMPTS)

def find_available_port(start_port=7860, max_attempts=10):
    """Find an available port starting from start_port"""
    for i in range(max_attempts):
        port = start_port + i
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def open_browser_with_delay(url, delay=3):
    """Open browser with a delay to ensure server is fully ready"""
    def delayed_open():
        time.sleep(delay)
        try:
            print(f"Opening browser to {url}")
            webbrowser.open(url)
            print("Browser opened successfully")
        except Exception as e:
            print(f"Failed to open browser automatically: {e}")
            print(f"Please manually open: {url}")
    
    threading.Thread(target=delayed_open, daemon=True).start()

# Enhanced Gradio Interface
with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="purple",
        secondary_hue="blue",
        neutral_hue="slate"
    ), 
    title="Asemic Artist",
    css="""
    .gradio-container {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    .prose h1 {color: ##ae65c2; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);}
    .prose p {color: #4a5568;}
    """
) as app:
    
    gr.Markdown(
        """
        # Asemic Artist
        ### Create abstract visual entities powered by advanced AI
        *Enter a concept or hit **Surprise Me** for otherworldly asemic art*
        """,
        elem_classes=["prose"]
    )

    with gr.Row():
        with gr.Column(scale=2):
            with gr.Group():
                prompt_input = gr.Textbox(
                    label="Creative Vision", 
                    placeholder="Describe your ethereal concept...", 
                    lines=3,
                    info="Be poetic and evocative for best results"
                )
                
                with gr.Row():
                    surprise_button = gr.Button("Surprise Me", variant="secondary", size="sm")
                    clear_button = gr.Button("Clear", variant="secondary", size="sm")
                
                model_selector = gr.Dropdown(
                    label="AI Model",
                    choices=["gpt-oss:20b", "gpt-oss-120b"],
                    value="gpt-oss:20b",
                    info="20b is faster, 120b is more creative"
                )
                
                complexity_slider = gr.Radio(
                    label="Complexity Level",
                    choices=["Simple", "Moderate", "Complex"],
                    value="Moderate",
                    info="Complex takes longer but produces more impressive results"
                )
            
            with gr.Group():
                color_selector = gr.CheckboxGroup(
                    label="Color Palette",
                    choices=[
                        "Black", "Gold", "Silver", "Pearl", 
                        "Crimson Red", "Burgundy", "Coral", "Salmon",
                        "Royal Blue", "Midnight Blue", "Navy", "Sky Blue", "Turquoise", "Aqua",
                        "Forest Green", "Sage Green", "Emerald", "Lime", "Chartreuse", "Olive",
                        "Deep Purple", "Indigo", "Lavender", "Magenta", "Fuchsia",
                        "Orange", "Amber", "Copper", "Rose Gold", "Maroon", "Onyx", "Teal"
                    ],
                    value=["Black", "Gold", "Deep Purple"],
                    info="Select 2-5 colors for best harmony"
                )
                
                stroke_slider = gr.Slider(
                    label="Base Stroke Width", 
                    minimum=0.5, 
                    maximum=5.0, 
                    step=0.1, 
                    value=2.0,
                    info="The AI will create variations around this base"
                )
            
            generate_button = gr.Button(
                "Generate Asemic Entity", 
                variant="primary", 
                size="lg"
            )

        with gr.Column(scale=3):
            with gr.Group():
                output_display = gr.HTML(
                    label="Generated Entity",
                    show_label=True
                )
                
                output_file = gr.File(
                    label="Download SVG", 
                    show_label=True
                )

                generation_info = gr.Textbox(
                    label="Generation Info",
                    show_label=True,
                    interactive=False
            )

    # Event handlers
    generate_button.click(
        fn=generate_asemic_svg,
        inputs=[prompt_input, model_selector, color_selector, stroke_slider, complexity_slider],
        outputs=[output_display, output_file, generation_info],
        show_progress=True
    )

    surprise_button.click(
        fn=surprise_prompt,
        outputs=[prompt_input]
    )
    
    clear_button.click(
        fn=lambda: "",
        outputs=[prompt_input]
    )

    with gr.Row():
        gr.Markdown(
            """
            ---
            **Asemic Art**: *Writing without words, meaning through pure visual form*  
            *Powered by advanced language models and creative algorithms*
            """,
            elem_classes=["prose"]
        )

def main():
    """Main function with proper error handling and PyInstaller compatibility"""
    print("=" * 70)
    print("Starting Asemic Artist Pro")
    print("=" * 70)
    
    is_frozen = getattr(sys, 'frozen', False)
    disable_browser = os.environ.get('DISABLE_BROWSER', '0') == '1'
    
    if is_frozen:
        print("Running as compiled executable")
        temp_dir = get_temp_dir()
        temp_dir.mkdir(exist_ok=True)
        print(f"Temp directory: {temp_dir}")
    else:
        print("Running as Python script")
    
    if disable_browser:
        print("Browser opening disabled (launched by launcher)")
    
    port = find_available_port(7860)
    if port is None:
        print("No available ports found. Please check for conflicts.")
        if is_frozen:
            input("Press Enter to exit...")
        return
    
    host = "127.0.0.1"
    url = f"http://{host}:{port}"
    
    print(f"Starting server on {url}")
    print(f"   Host: {host}")  
    print(f"   Port: {port}")
    if not disable_browser and is_frozen:
        print("   Browser will open automatically in 3 seconds...")
    print("-" * 70)
    
    try:
        if is_frozen and not disable_browser:
            # Only open browser if not disabled and running as executable
            open_browser_with_delay(url, delay=3)
            
            app.launch(
                server_name=host,
                server_port=port,
                inbrowser=False,
                show_error=True,
                quiet=True,
                share=False,
                favicon_path=None
            )
        elif not is_frozen and not disable_browser:
            # Regular Python execution with browser
            app.launch(
                server_name=host,
                server_port=port,
                inbrowser=True,
                show_error=True,
                quiet=False,
                share=False
            )
        else:
            # Browser disabled - just start server
            app.launch(
                server_name=host,
                server_port=port,
                inbrowser=False,
                show_error=True,
                quiet=True,
                share=False
            )
        
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error starting application: {e}")
        if is_frozen:
            input("Press Enter to exit...")
    finally:
        print("Asemic Artist Pro closed")

if __name__ == "__main__":
    main()
