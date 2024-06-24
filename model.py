# from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough,RunnableSequence
from langchain_huggingface import HuggingFaceEndpoint
import streamlit as st
from pymongo import MongoClient
import urllib,io,json
from langchain_core.runnables import Runnable
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate,ChatPromptTemplate
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

# OPEN_AI_API_KEY=os.getenv("OPEN_AI_API_KEY")
ATLAS_CONNECTION_STRING=os.getenv("ATLAS_CONNECTION_STRING")
# api_key=OPEN_AI_API_KEY,organization='org-TO4u4wavOLSyW1cTGBaT4C2A'
# model_name="gpt-3.5-turbo",api_key=OPEN_AI_API_KEY
# llm=OpenAI(api_key=OPEN_AI_API_KEY)

HUGGING_FACE_KEY=os.getenv("HUGGING_FACE_KEY")
rep_id="mistralai/Mistral-7B-Instruct-v0.3"

llm=HuggingFaceEndpoint(repo_id=rep_id,max_new_tokens=4000,temperature=0.2,huggingfacehub_api_token=HUGGING_FACE_KEY)

client = MongoClient(ATLAS_CONNECTION_STRING, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db_name = "foodnest"
db=client[db_name]



st.title("talk to MongoDB")
st.write("ask anything and get answer")
input=st.text_area("enter your question here")

with io.open("sample1.txt","r",encoding="utf-8")as f1:
    sample1=f1.read()
    f1.close()

with io.open("prompt1.txt","r",encoding="utf-8")as f1:
    prompt1=f1.read()
    f1.close()


query_with_prompt=PromptTemplate(
    template=prompt1,
    input_variables=["question","sample1"]
)


# st.write(llm)
llmchain=(query_with_prompt | llm)

# Function to extract collection names from the pipeline
# def get_collection_names_from_pipeline(pipeline):
#     collection_names = list()
#     for stage in pipeline:
#         if "$lookup" in stage:
#             collection_names.append(stage["$lookup"]["from"])

#     if len(collection_names) == 0:
#         return "user"
    
#     return collection_names[0]

results=""
if input is not None:
    button=st.button("Submit")
    if button:
        response=llmchain.invoke({
            "question":input,
            "sample1":sample1
        })
  
       
        query=json.loads(response)
        # Get the collection names from the pipeline
        # collection_names = get_collection_names_from_pipeline(query)

        results=db.command('aggregate','user',pipeline=query,explain=False)




with io.open("sample2.txt","r",encoding="utf-8")as f1:
    sample2=f1.read()
    f1.close()


prompt2="""
You are an intelligent system capable of understanding and converting MongoDB NoSQL queries formatted in JSON to natural language explanations. 
Your task is to take a MongoDB NoSQL queries formatted in JSON and provide a clear and concise answer in natural language based on user question. 

sample_question: {sample2}
As an expert you must use this sample_question whenever required and also use your knowledge to rectify the errors.
Note: You have to just return answer in natural language based on user. Please follow this strictly.
User's Question:{question}
MongoDB Query (JSON):{query}
output:

"""


answer_with_query=PromptTemplate(template=prompt2,input_variables=['query', 'question', 'sample2'])


llmchain2= (answer_with_query | llm)

response=llmchain2.invoke({
            "sample2":sample2,
            "question":input,
            "query": results
        })         

       
st.write(response)


