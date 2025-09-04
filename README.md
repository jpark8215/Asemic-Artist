# Asemic Artist

Create abstract, asemic visual entities powered by GPT-OSS.  
Live demo: [Asemic Artist on Hugging Face Spaces](https://huggingface.co/spaces/jpark8215/AsemicArtist)

## What is Asemic Artist?
Asemic Artist is a creative AI tool that transforms textual concepts into intricate, abstract visual art. It leverages the power of Large Language Models to generate "asemic writing" a form of wordless script that conveys emotion and aesthetic flow without any semantic meaning.

Users can describe a vision (e.g., "a mechanical heart pumping rivers of aurora"), choose a style, and the AI will generate a unique, downloadable SVG artwork. This project explores the boundary between language and pure form, using an AI built for meaning to create something beautifully meaningless.

## How It Works: The AI Pipeline
This application uses the Hugging Face Inference API to call gpt-oss models directly. The architecture is designed for efficiency and power, with a user-friendly interface that communicates with a high-performance model backend.

The process is as follows:

1. **User Input**: The user provides a creative prompt and selects stylistic parameters (colors, complexity, stroke width) through the Gradio interface.

2. **Prompt Engineering**: The Python backend takes these inputs and programmatically constructs a detailed enhanced_prompt. This prompt combines the user's vision with strict technical and artistic instructions.

3. **API Call**: The huggingface_hub.InferenceClient is used to send this prompt to the specified gpt-oss model (e.g., openai/gpt-oss-120b). The core of this interaction is the query_model function in app.py:


```yaml
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
```yaml


 4. **SVG Generation**: The gpt-oss model processes the complex prompt and generates a response that is pure SVG code.

5. **Output**: The application extracts the SVG from the model's response and displays it in the Gradio interface, making it available for download. A retry-loop is built-in to ensure robustness against API errors or malformed outputs.

## Features
**Multiple GPT-OSS Models**: Choose between different high-performance models like gpt-oss-120b and gpt-oss-20b to balance speed and creativity.

**Complexity Control**: Guide the AI to generate simple, moderate, or highly complex and detailed artwork.

**Rich Color Palettes**: Select from over 30 curated colors to define the entity's aesthetic.

**Animated SVG**: The AI is prompted to include subtle SVG animations, bringing the entities to life.

"**Surprise Me**" Button: Instantly generate a creative, evocative prompt to kickstart your imagination.

**SVG Download**: Save your creations as high-quality, scalable vector graphics for use in other projects.

## How to Run
To run this application on your own machine, follow these steps:


## Tech Stack
Language: Python

Framework: Gradio

Platform: Hugging Face Spaces

API: Hugging Face Inference API (huggingface_hub)

Core AI Models: openai/gpt-oss-120b, openai/gpt-oss-20b, mistralai/Mixtral-8x7B-Instruct-v0.1

## Hugging Face Configuration
This repository is configured to run as a Gradio app on Hugging Face Spaces.

```yaml
title: AsemicArtist
emoji: 🔥
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 5.44.1
app_file: app.py
pinned: false
license: apache-2.0
short_description: Create abstract visual entities powered by gpt-oss
