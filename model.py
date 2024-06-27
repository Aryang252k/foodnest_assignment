from langchain_huggingface import HuggingFaceEndpoint
# import streamlit as st
from pymongo import MongoClient
import urllib,io
from langchain.prompts import PromptTemplate
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import re
import requests

load_dotenv()


ATLAS_CONNECTION_STRING=os.getenv("ATLAS_CONNECTION_STRING")
HUGGING_FACE_KEY=os.getenv("HUGGING_FACE_KEY")
rep_id="mistralai/Mistral-7B-Instruct-v0.3"




# st.title("talk to MongoDB")
# st.write("ask anything and get answer")
# input=st.text_area("enter your question here")


def generate_embedding(text:str)-> list[float]:
   API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L12-v2"
   response=requests.post(
      API_URL,
      headers={"Authorization": f"Bearer {HUGGING_FACE_KEY}"},
      json={"inputs": text}
   )
   
   if response.status_code != 200:
      raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")
   
   return response.json()


def output_embedding(question,collection_nam,path,index_name):

    client = MongoClient(ATLAS_CONNECTION_STRING, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db_name = "foodnest"
    db=client[db_name]
    collection=db[collection_nam]

   
    results=collection.aggregate([
       {
          "$vectorSearch": {
            "queryVector": generate_embedding(question),
            "path":path,
            "numCandidates":100,
            "limit":4,
            "index": index_name
             }
       }
    ])
    ans=[x for x in results][0]
    ans.pop("embeddings",None)
    return ans


#helper
def remove_comments(query):
    # Remove single-line comments
    query = re.sub(r'//.*?\n', '\n', query)
    # Remove multi-line comments
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
    return query.strip()


 
def get_response(question):
    # reading files
    with io.open("sample1.txt","r",encoding="utf-8")as f1:
        sample1=f1.read()
        f1.close()

    with io.open("prompt1.txt","r",encoding="utf-8")as f1:
        prompt1=f1.read()
        f1.close()

    with io.open("no_query.txt","r",encoding="utf-8")as f1:
        no_query=f1.read()
        f1.close()

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
    
    results=[]
    query_with_prompt=PromptTemplate(
        template=prompt1,
        input_variables=["question","no_query","sample1"]
    )

    llmchain=(query_with_prompt | llm)

    # Function to extract collection names from the pipeline
    response=llmchain.invoke({
        "question":question,
        "no_query":no_query,
        "sample1":sample1
    })
    
    try:
      if response.split(".")[1]=="restaurants":
       ans=output_embedding(collection_nam='restaurants',question=question,path="embeddings",index_name="restaurants_vector")
    except:
        print("Not a list") 

    if response.replace('"',"").strip().lower() == question.strip().lower():
        return question
    else:
        # Get the collection names from the pipeline
        method = response.split(".")[2].split("(")[0]
        if method=="aggregate":
            try:
             results=eval(response)
             resul=[x for x in results]
             resul.append(ans)
             return resul
            except:
              return question
        else:
          try:
           results=exec(response)
           return results
          except:
           return question


def final_response(question,query,history):
    with io.open("assistant.txt","r",encoding="utf-8")as f1:
        assistant=f1.read()
        f1.close()

    with io.open("sample2.txt","r",encoding="utf-8")as f1:
        sample2=f1.read()
        f1.close()

    with io.open("prompt2.txt","r",encoding="utf-8")as f1:
        prompt2=f1.read()
        f1.close()

    llm=HuggingFaceEndpoint(repo_id=rep_id,max_new_tokens=4000,temperature=0.3,huggingfacehub_api_token=HUGGING_FACE_KEY)    
    answer_with_query=PromptTemplate(template=prompt2,input_variables=['query',"history",'question', 'sample2'])
    llmchain= (answer_with_query | llm)

    response=llmchain.invoke({
                 "assistant":assistant,
                 "history":history,
                "sample2":sample2,
                "question":question,
                "query": query
            })   

    return response

# x=st.button("Submit")
# if x:
#     results=get_response(input)
#     st.write(results)



def post_embedding(collection_nam):
    
    client = MongoClient(ATLAS_CONNECTION_STRING, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    db_name = "foodnest"
    db=client[db_name]
    collection=db[collection_nam]

    for doc in collection.find():
       doc["embeddings"]=generate_embedding(str(doc))
       collection.replace_one({'_id': doc["_id"]},doc)

    print("Successfully posted embeddings")




# post_embedding("restaurants")