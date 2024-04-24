import textwrap
from llama_index.core.tools import FunctionTool
import os


def code_generator_func(filename, code):
    try:
        with open(os.path.join("rag/storage", filename), "w") as f:
            f.write(textwrap.dedent(code))
        print("Saved file", filename)
    except:
        print("Error saving file...")


code_generator_tool = FunctionTool.from_defaults(
    fn=code_generator_func,
    name="code_generator_tool",
    description="""this tool is used to write only code to file, make sure you write the code before saving it to file. 
    Use this when you need to save or generate code to a file. Use this tool to save only code to a file named {filename}""",
)


def code_reader_func(file_name):
    path = os.path.join("rag/data", file_name)
    try:
        with open(path, "r") as f:
            content = f.read()
            return {"file_content": content}
    except Exception as e:
        return {"error": str(e)}


code_reader_tool = FunctionTool.from_defaults(
    fn=code_reader_func,
    name="code_reader_tool",
    description="""this tool can read the contents of code files and return 
    their results. Use this when you need to read the contents of a file""",
)