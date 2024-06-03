# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import RunnablePassthrough,RunnableSequence
import streamlit as st
from pymongo import MongoClient
import urllib,io,json
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

ANTHROPIC_API_KEY=os.getenv("ANTHROPIC_API_KEY")
ATLAS_CONNECTION_STRING=os.getenv("ATLAS_CONNECTION_STRING")

llm=ChatAnthropic(model_name="claude-3-opus-20240229",temperature=0.0,api_key=ANTHROPIC_API_KEY)

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

prompt1="""

        You are a very intelligent AI assitasnt who is expert in identifying relevant questions from user
        from user and converting into nosql mongodb agggregation pipeline query should be foramted in json.
        Note: You have to just return the query as to use in agggregation pipeline nothing else. Don't return any other thing
        Please use the below schema to write the mongodb queries , dont use any other queries.

       schema:

       This schema represents a food supplier company's database,where you have to act as an bot(waiter) to customer,
       the customer can talk to you in hindi, english or both. 
        

       The schema includes four main collections: user, orders, restaurants, and food_images.
       **user Collection**: Stores user information including _id, name, date of birth, email, delivery addresses with tags, food choices, preferences, health conditions, and days they avoid non-veg food.
       **orders Collection**: Stores order details including _id, order details (ID and date/time), dish details (name, portion, price), customer details (ID, name, contact), delivery address (address and Google PIN), restaurant details (name, address, Google PIN), distance from restaurant to delivery address, and UPI transaction details (acknowledgement ID and status).
       **restaurants Collection**: Stores restaurant information including _id, name, address, Google PIN, branch details (address and Google PIN), and menu details (dish name, portion, price, picture).
       **food_images Collection**: It stores _id,image_id and dish name where image_id is used to store the image file in binary mode and store it in GridFS, 
       which splits the file into chunks and saves it in fs.files and fs.chunks collections.

       This schema helps manage and streamline the company's operations, ensuring accurate tracking of user preferences, order details, and restaurant information. 
       your job is to get python code for the user question
       Here’s a breakdown of its schema with descriptions for each field:

##user Collection

1. **_id**: Unique identifier for the user.
2. **name**: Name of the user.
3. **dob**: Date of birth of the user.
4. **email**: Email address of the user.
5. **foodChoices**: The user's food choices (Veg, Non-Veg).
6. **contact**: contact number of user in string format.
##Embedded fields
7. **foodPreferences**: Array of the user's food preferences (e.g., Chinese, South Indian, etc.).
8. **healthConditions**: Array of any health conditions the user has (e.g., diabetes, blood sugar, etc.).
9. **nonVegDays**: Array of days the user does not eat non-veg.
10.**addresses**: Array of objects containing the addresses where the user mostly gets deliveries.
     -**address**: The delivery address.
     -**tag**: The tag for the address (e.g., office, hostel, PG, college, etc.).

##orders Collection

1. **_id**: Unique identifier for the order.
2.**distance**: Distance between the restaurant and the delivery address (in kms).
##Embedded fields
3.**upiDetails**: Object containing UPI details.
    -**ackId**: UPI acknowledgement ID.
    -**status**: UPI status.
4.**orderDetails**: Object containing details about the order.
   -**orderId**: The ID of the order.
   -**dateTime**: string Date and time when the order was placed.
5.**dishDetails**: Array of objects containing details about the dishes ordered.
    -**dish**: Name of the dish.
    -**portion**: Portion size of the dish.
    -**price**: Price of the dish.
6.**customerDetails**: Object containing details about the customer.
    -**customerId**: The ID of the customer.
    -**name**: Name of the customer.
    -**contact**: Contact information of the customer.
7.**deliveryAddress**: Object containing details about the delivery address.
    -**address**: The delivery address.
    -**googlePin**: Google PIN location of the delivery address.
8.**restoDetails**: Object containing details about the restaurant.
    -**name**: Name of the restaurant.
    -**address**: Address of the restaurant.
    -**googlePin**: Google PIN location of the restaurant.

##restaurants Collection

1.**_id**: Unique identifier for the restaurant.
2.**name**: Name of the restaurant.
3.**address**: Address of the restaurant.
4.**googlePin**: Google PIN location of the restaurant.
##Embedded fields
5.**branches**: Array of objects containing details about the branches of the restaurant.
    -**address**: Address of the branch.
    -**googlePin**: Google PIN location of the branch.
6.**menu**: Array of objects containing details about the menu.
   -**dish**: Name of the dish.
   -**portion**: Portion size of the dish.
   -**price**: Price of the dish.
 

## food_images Collection
1. **_id**: Unique identifier for the food image.
2. **dish**: Name of the dish.
3. **image_id**: unique identifier used to reference the image stored in GridFS ,which splits the file into chunks and saves it in fs.files and fs.chunks collections. 

This schema provides a comprehensive view of the data structure for an food_nest an food supplier company in MongoDB, 
including nested and embedded data structures that add depth and detail to the document.
use the below sample_examples to generate your queries perfectly
sample_example:

Below are several sample user questions related to the MongoDB document provided, 
and the corresponding MongoDB aggregation pipeline queries that can be used to fetch the desired data.
Use them wisely.

sample_question: {sample1}
As an expert you must use this sample_question whenever required and also use your knowledge to rectify the errors.
Note: You have to just return the query nothing else. Don't return any additional text with the query.Please follow this strictly.
input:{question}
output:

"""


query_with_prompt=PromptTemplate(
    template=prompt1,
    input_variables=["question","sample"]
)

# st.write(llm)
llmchain = (
query_with_prompt
| llm
)

# Function to extract collection names from the pipeline
def get_collection_names_from_pipeline(pipeline):
    collection_names = list()
    for stage in pipeline:
        if "$lookup" in stage:
            collection_names.append(stage["$lookup"]["from"])

    if len(collection_names) == 0:
        return "user"
    
    return collection_names[0]

results=""
if input is not None:
    button=st.button("Submit")
    if button:
        response=llmchain.invoke({
            "question":input,
            "sample":sample1
        })
        
        try:
            query=json.loads(response["text"])
            # Get the collection names from the pipeline
            collection_names = get_collection_names_from_pipeline(query)
            results=db[collection_names].aggregate(query)
        except:
            results="No data found!"

with io.open("sample2.txt","r",encoding="utf-8")as f1:
    sample2=f1.read()
    f1.close()


prompt2="""
You are an intelligent system capable of understanding and converting MongoDB NoSQL queries formatted in JSON to natural language explanations. 
Your task is to take a MongoDB NoSQL queries formatted in JSON and provide a clear and concise answer in natural language based on user question. 

sample_question: {sample}
As an expert you must use this sample_question whenever required and also use your knowledge to rectify the errors.
Note: You have to just return answer in natural language based on user. Please follow this strictly.
User's Question:{question}
MongoDB Query (JSON):{query}
output:

"""


answer_with_query=PromptTemplate(
    template=prompt2,
    input_variables=["sample","question","query"]
)

llmchain2= answer_with_query | llm

response=llmchain2.invoke({
            "sample":sample2,
            "question":input,
            "query": results
        })         
            
st.write(response["text"])

