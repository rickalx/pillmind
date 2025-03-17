import os
from google import genai
from google.genai import types

def get_prompt(prompt_name):
    from diccionario_prompts import FACTIBILITY_PROMPTS
    return FACTIBILITY_PROMPTS.get(prompt_name, "")

def generate(texto):
    prompt = get_prompt("prompt_general_compacto")
    client = genai.Client(
        api_key=os.environ.get("IA_API_KEY"),
    )

    model = "gemini-2.0-flash-thinking-exp-01-21"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"{prompt} {texto}"),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.3,
        top_p=0.8,
        top_k=30,
        max_output_tokens=65536,
        response_mime_type="text/plain",
    )

    full_response = ""  # Variable para acumular la respuesta completa

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        full_response += chunk.text  # Acumular cada fragmento de texto en la variable

    return full_response  # Retornar la respuesta completa

if __name__ == "__main__":
    prompt = "Tu prompt aquí"
    texto = "Tu texto aquí"
    response = generate(prompt, texto)
    print(response)  # Imprimir la respuesta completa