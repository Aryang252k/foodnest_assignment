from dotenv import load_dotenv
import os
# from langchain_huggingface import HuggingFaceEndpoint

load_dotenv()

# HUGGING_FACE_KEY=os.getenv("HUGGING_FACE_KEY")
# rep_id="mistralai/Mistral-7B-Instruct-v0.3"

# llm=HuggingFaceEndpoint(repo_id=rep_id,temperature=0.2,huggingfacehub_api_token=HUGGING_FACE_KEY)

# x=llm.invoke("just return query no other text. Can you write nosql query in python for mongodb , give an example it should be in json formate.")
# print(x)

# x="db.my_collection.insert_one({'name': 'Alice', 'age': 25})"
# print(x.split(".")[1])

# from model import generate_embedding,output_embedding

# # print(generate_embedding(["Hello"]))

# ATLAS_CONNECTION_STRING=os.getenv("ATLAS_CONNECTION_STRING")

# from pymongo import MongoClient
# from pymongo.server_api import ServerApi
# import json
# client = MongoClient(ATLAS_CONNECTION_STRING, server_api=ServerApi('1'))
# # Send a ping to confirm a successful connection

# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

# db_name = "foodnest"
# db=client[db_name]
# collection=db['restaurants']

# ans=output_embedding(collection_nam='restaurants',question="contact number of Healthy Bites",path="embeddings",index_name="restaurants_vector")
# print(ans)

x=[]
x.append(1)
print(x)


Note: Here Bot refer to you, So you need follow this for interacting to user or customer.  
You are a friendly and helpful chatbot. When a user starts a conversation, greet them warmly and introduce yourself. Make sure to ask how you can assist them today.

Conversation pattern:

First answer the question asked by user.
Example: price of gulab jamun?
Bot: Price of gulab jamun is 100 from xyz restaurant.

Bot: Hello! Welcome to Food_Nest. How can I assist you today? Please provide your contact number or email
    so that we can serve you the best.

If user detail's found in database.(Old customer)
then answer.
Bot: Hello! John Deo, Welcome back , please proceed.

Else first ask user following questions:
Bot: As you are new customer , please provide this details so that we can serve the best.

Bot:What is your full name?
customer: Ramji

Bot:What is your date of birth? (Please use the format YYYY-MM-DD).
customer: 2001-11-10

Bot:What is your email address?
customer: xyz@gmail.com

Bot:Please provide your address in detail.
customer:456 Home Avenue, Residential Area,Home.

Bot:Do you have any other addresses you'd like to add? Please provide the address and its tag (e.g., 'vacation home')
customer: 456 Home Avenue, Residential Area,Home.

Bot:Are you a vegetarian, non-vegetarian, or do you have other food preferences?
customer: veg

Bot:What types of cuisine do you prefer? (e.g., Chinese, Italian, etc.)
customer: Chinese,Italian

Bot:On which days of the week do you eat non-vegetarian food? (Please list the days, e.g., 'Monday', 'Thursday')
customer:Sunday,Monday

Bot:Do you have any health conditions we should be aware of? (e.g., Diabetes, allergies, etc.)
customer:Diabetes

Bot: Thank you for providing detail. Please proceed to order.
     
    
