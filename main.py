import streamlit as st
from pymongo import MongoClient
import urllib,io,json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm=ChatOpenAI(model="gpt-4",temperature=0.0)
#mongo client
username="ronidas"
pwd="YFR85HiZLgqFtbPW"
client=MongoClient("mongodb+srv://"+urllib.parse.quote(username)+":"+urllib.parse.quote(pwd)+"@cluster0.lymvb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db=client["sample_airbnb"]
collection=db["listingsAndReviews"]

st.title("talk to MongoDB")
st.write("ask anything and get answer")
input=st.text_area("enter your question here")

with io.open("sample.txt","r",encoding="utf-8")as f1:
    sample=f1.read()
    f1.close()

prompt="""
        you are a very intelligent AI assitasnt who is expert in identifying relevant questions fro user
        from user and converting into nosql mongodb agggregation pipeline query.
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

sample_question: {sample}
As an expert you must use them whenever required.
Note: You have to just return the query nothing else. Don't return any additional text with the query.Please follow this strictly
input:{question}
output:
"""
query_with_prompt=PromptTemplate(
    template=prompt,
    input_variables=["question","sample"]
)
llmchain=LLMChain(llm=llm,prompt=query_with_prompt,verbose=True)

if input is not None:
    button=st.button("Submit")
    if button:
        response=llmchain.invoke({
            "question":input,
            "sample":sample
        })
        query=json.loads(response["text"])
        results=collection.aggregate(query)
        print(query)
        for result in results:
            st.write(result)
