from datetime import datetime
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from pydantic import BaseModel
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from prompts import context, code_parser_template
from agents.system.tools.coding_tools import code_reader_tool, code_generator_tool
from llama_index.readers.file import UnstructuredReader

llm = Ollama(model="brainiakk", request_timeout=30.0)

# parser = LlamaParse(result_type="markdown")

# file_extractor = {".pdf": parser}
documents = SimpleDirectoryReader("./rag/knowledge_base/docs", file_extractor={".pdf": UnstructuredReader(), ".txt": UnstructuredReader(), ".json": UnstructuredReader(), ".html": UnstructuredReader()}).load_data()

embed_model = FastEmbedEmbedding(
            model_name="BAAI/bge-base-en-v1.5",
            cache_dir="embeddings"
            
        )
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
query_engine = vector_index.as_query_engine(llm=llm)

tools = [
    QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="api_documentation",
            description="this gives documentation about code for an API. Use this for reading docs for the API",
        ),
    ),
    code_generator_tool,
    code_reader_tool,
]

code_llm = Ollama(model="brainiakk")
agent = ReActAgent.from_tools(tools, llm=code_llm, verbose=True, prompt="DO NOT use tools if you know the answer to a question. Your name is Tech AI. You're Tech AI.", context=context)


# class CodeOutput(BaseModel):
#     code: str
#     description: str
#     filename: str

# parser = PydanticOutputParser(CodeOutput)
json_prompt_str = code_parser_template
json_prompt_tmpl = PromptTemplate(json_prompt_str)
print(json_prompt_tmpl)
output_pipeline = QueryPipeline(chain=[json_prompt_tmpl, llm])

   
while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    retries = 0

    while retries < 3:
        try:
            result = agent.query(prompt)
            print(result)
            next_result = output_pipeline.run(response=result)
            cleaned_json = str(next_result).replace("assistant:", "").strip()
            break
        except Exception as e:
            retries += 1
            print(f"Error occured, retry #{retries}:", e)

        # print(cleaned_json)
    if retries >= 3:
        print("Unable to process request, try again... ")
        continue

    print("Code generated")
    # print(cleaned_json)
    # # Remove the unwanted text from the given string
    # pattern = re.compile(r'```json\n(.*?)\n```', re.DOTALL)
    # cleaned_string = pattern.search(cleaned_json).group(1)

    # # Load the cleaned string into a dictionary
    # data_dict = json.loads(cleaned_string)

    # # Access the "code" value from the dictionary
    # code = data_dict.get("code")
    # filename = data_dict.get("filename")
    # print(code)
    # # print(cleaned_json)
    # # print("\n\nDesciption:", cleaned_json["description"])

    # # filename = cleaned_json["filename"]

    # try:
    #     with open(os.path.join("outputs", filename), "w") as f:
    #         f.write(textwrap.dedent(code))
    #     print("Saved file", filename)
    # except:
    #     print("Error saving file...")
#read contents of test.py and write a python script that calls the post endpoint to make a new item
