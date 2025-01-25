from transformers import pipeline


pipeline = pipeline(
    "text-generation",
    model="Nexusflow/NexusRaven-13B",
    torch_dtype="auto",
    device_map="auto",
)

prompt_template = """
<human>:
OPTION:
<func_start>def hello_world(n : int)<func_end>
<docstring_start>
\"\"\"
Prints hello world to the user.

Args:
n (int) : Number of times to print hello world.
\"\"\"
<docstring_end>

OPTION:
<func_start>def hello_universe(n : int)<func_end>
<docstring_start>
\"\"\"
Prints hello universe to the user.

Args:
n (int) : Number of times to print hello universe.
\"\"\"
<docstring_end>

User Query: Question: {question}

Please pick a function from the above options that best answers the user query and fill in the appropriate arguments.<human_end>
"""
prompt = prompt_template.format(question="Please print hello world 10 times.")

result = pipeline(prompt, max_new_tokens=100, return_full_text=False, do_sample=False)[0]["generated_text"]

# Get the "Initial Call" only
start_str = "Initial Answer: "
end_str = "\nReflection: "
start_idx = result.find(start_str) + len(start_str)
end_idx = result.find(end_str)
function_call = result[start_idx: end_idx]

print (f"Generated Call: {function_call}")