from dotenv import load_dotenv
import os
from langchain_huggingface import HuggingFaceEndpoint

load_dotenv()

HUGGING_FACE_KEY=os.getenv("HUGGING_FACE_KEY")
rep_id="mistralai/Mistral-7B-Instruct-v0.3"

llm=HuggingFaceEndpoint(repo_id=rep_id,temperature=0.2,huggingfacehub_api_token=HUGGING_FACE_KEY)

x=llm.invoke("just return query no other text. Can you write nosql query in python for mongodb , give an example it should be in json formate.")
print(x)