from datetime import datetime
import os
import time
import json
from dotenv import load_dotenv
# Using with chat history
from langchain_openai import ChatOpenAI
import gc, json, re
import xml.etree.ElementTree as ET
from functools import partial
import os
import transformers
import torch

from langchain_core.utils.function_calling import convert_pydantic_to_openai_function
# from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.pydantic_v1 import BaseModel, Field, validator
# from langchain_mistralai.chat_models import ChatMistralAI
load_dotenv()

client_type = "ollama"

if client_type == "ollama":
    model = ChatOpenAI(model="wizardlm2:7b-q4_K_M", api_key=os.getenv("OLLAMA_API_KEY"), base_url=os.getenv("OLLAMA_API_URL"))
else:
    model = ChatOpenAI(model="Meta-Llama-3-8B-Instruct-Q4_K_M.gguf", api_key=os.getenv("LMSTUDIO_API_KEY"), base_url=os.getenv("LMSTUDIO_API_URL"))


# Load API key from .env file
load_dotenv()

tokenizer = transformers.AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B", token=os.getenv("HF_API_KEY"), cache_dir="tokenizers")
# model = ChatOpenAI(model="Meta-Llama-3-8B-Instruct-Q4_K_M.gguf", api_key=os.getenv("LMSTUDIO_API_KEY"), base_url=os.getenv("LMSTUDIO_API_URL"))

def delete_model(*args):
    for var in args:
        if var in globals():
            del globals()[var]

    gc.collect()
    torch.cuda.empty_cache()

class BookRecommendation(BaseModel):
    """Provides book recommendations based on specified interest."""
    interest: str = Field(description="question of user interest about a book.")
    recommended_book: str = Field(description="answer to recommend a book")

    @validator("interest")
    def interests_must_not_be_empty(cls, field):
        if not field:
            raise ValueError("Interest cannot be empty.")
        return field

class Joke(BaseModel):
    """Get a joke that includes the setup and punchline"""
    setup: str = Field(description="question to set up a joke")
    punchline: str = Field(description="answer to resolve the joke")

    # You can add custom validation logic easily with Pydantic.
    @validator("setup")
    def question_ends_with_question_mark(cls, field):
        if field[-1] != "?":
            raise ValueError("Badly formed question!")
        return field

class SongRecommendation(BaseModel):
    """Provides song recommendations based on specified genre."""
    genre: str = Field(description="question to recommend a song.")
    song: str = Field(description="song you want to recommend")

    @validator("genre")
    def genre_must_not_be_empty(cls, field):
        if not field:
            raise ValueError("genre cannot be empty.")
        return field

convert_pydantic_to_openai_function(SongRecommendation)

def extract_function_calls(completion):
    if isinstance(completion, str):
        content = completion
    else:
        content = completion.content

    pattern = r"<multiplefunctions>(.*?)</multiplefunctions>"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return None

    multiplefn = match.group(1)
    functions = []
    for fn_match in re.finditer(r"<functioncall>(.*?)</functioncall>", multiplefn, re.DOTALL):
        fn_text = fn_match.group(1)
        try:
            functions.append(json.loads(fn_text))
        except json.JSONDecodeError:
            pass  # Ignore invalid JSON

    return functions

def generate_hermes(prompt, model, tokenizer, generation_config_overrides={}):
    fn = """{"name": "function_name", "arguments": {"arg_1": "value_1", "arg_2": value_2, ...}}"""
    prompt = f"""system
You are a helpful assistant with access to the following functions:

{convert_pydantic_to_openai_function(Joke)}

{convert_pydantic_to_openai_function(BookRecommendation)}

{convert_pydantic_to_openai_function(SongRecommendation)}

To use these functions respond with:
<multiplefunctions>
    <functioncall> {fn} </functioncall>
    <functioncall> {fn} </functioncall>
    ...
</multiplefunctions>

Edge cases you must handle:
- If there are no functions that match the user request, you will respond politely that you cannot help.
user
{prompt}
assistant"""

    with torch.inference_mode():
        completion = model.invoke([{"role": "user", "content": prompt}])

    if isinstance(completion, str):
        # Handle the case where completion is a string
        content = completion.strip()
    else:
        # Handle the case where completion is an AIMessage object
        content = completion.content.strip()

    functions = extract_function_calls(content)

    if functions:
        print(functions)
    else:
        print(content)
    print("="*100)

generation_func = partial(generate_hermes, model=model, tokenizer=tokenizer)

prompts = [
    "Tell me a joke about kenyan athletes",
    "Song for working out",
    "Recommend me a book on singularity."
]

total_start_time = time.time()
for prompt in prompts:
    start_time = time.time()
    generation_func(prompt)
    end_time = time.time()
    print("⏰ Single Prompt Execution Time: ", end_time - start_time)
    

total_end_time = time.time()
print("⏰ Total Prompts Execution Time: ", total_end_time - total_start_time)