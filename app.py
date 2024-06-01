import streamlit as st
import getpass, os, pymongo, pprint,gridfs
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from PIL import Image
import io
from dotenv import load_dotenv
from bson.objectid import ObjectId
from datetime import datetime
from pathlib import Path
import json

load_dotenv()
ATLAS_CONNECTION_STRING=os.getenv("ATLAS_CONNECTION_STRING")

#connencting mongodb db
client = MongoClient(ATLAS_CONNECTION_STRING, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db_name = "foodnest"
db=client[db_name]

users_collection = db['user']
restaurants_collection = db['restaurants']
orders_collection = db['orders']
food_images_collection = db['food_images']
admin_collection = db['admin']

# Helper function to display collections
def display_collection(collection):
    st.write([doc for doc in collection.find()])

# CRUD operations for Users
def user_operations():
    st.subheader("User Operations")
    action = st.selectbox("Select Action", ["Create", "Read", "Update", "Delete", "Search"])

    if action == "Create":
        name = st.text_input("Name")
        dob = st.date_input("DOB")
        contact=st.text_input("Contact No")
        email = st.text_input("Email")
        address = st.text_area("Addresses (comma-separated -address1 tag , address2 tag)")
        addresses = [{"address": addr.strip().lower(), "tag": addr.split(" ")[-1].lower()} for addr in address.split(",")]
        food_choices = st.selectbox("Food Choices", ["Veg", "Non-Veg"])
        food_preferences = st.text_area("Food Preferences (comma-separated)")
        health_conditions = st.text_area("Health Conditions (comma-separated)")
        non_veg_days = st.text_area("Non-Veg Days (comma-separated)")

        if st.button("Create User"):
            users_collection.insert_one({
                "name": name,
                "dob": str(dob),
                "email": email,
                "contact":contact,
                "addresses": addresses,
                "foodChoices": food_choices,
                "foodPreferences": food_preferences.split(","),
                "healthConditions": health_conditions.split(","),
                "nonVegDays": non_veg_days.split(",")
            })
            st.success("User created successfully!")

    elif action == "Read":
        display_collection(users_collection)

    elif action == "Update":
        user_id = st.text_input("Enter User ID to update")
       
        if 'button1' not in st.session_state:
             st.session_state.button1 = False
        if 'button2' not in st.session_state:
             st.session_state.button2 = False
        if 'button3' not in st.session_state:
             st.session_state.button3 = False

        if st.button("Search User"):
             st.session_state.button1 = True
             st.session_state.button2 = False
             st.session_state.button3 = False
        if not user_id:
            st.stop()
        if st.session_state.button1:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            
            st.write(user)
            if st.button("Edit User"):
               st.session_state.button2= True
               st.session_state.button3 = False

            if st.session_state.button2:
                  st.write(f"**user id: {user_id}**")
                  name = st.text_input("Name",value=user['name'])
                  year,month,day = user["dob"].split('-')
                  new_date_string = f'{day}-{month}-{year}'
                  dob = st.text_input("DOB",value=new_date_string)
                  email = st.text_input("Email",value=user["email"])
                  contact=st.text_input("Contact No",value=user['contact'])
                  st1=""
                  if type(user["addresses"])== str:
                    u=user["addresses"].replace("'", '"')
                    for i in json.loads(u):
                        st1=st1+i["address"]+" "
                  else:
                    for i in user["addresses"]:
                       st1=st1+i["address"].replace(","," ")+" "+","
                  address = st.text_area("Addresses (comma-separated -address1 tag , address2 tag)",value=st1.strip(","))
                  addresses = [{"address": addr.strip().lower(), "tag": addr.split(" ")[-1].lower()} for addr in address.split(",")]
                  idx=0
                  if user['foodChoices']=="Non-Veg":
                      idx=1
                  food_choices = st.selectbox("Food Choices", ["Veg", "Non-Veg"],index=idx)
                  l=""
                  for i in user["foodPreferences"]:
                     l=l+i+","
                  food_preferences = st.text_area("Food Preferences (comma-separated)",value=l.strip(","))
                  l=""
                  for i in user["healthConditions"]:
                     l=l+i+","
                  health_conditions = st.text_area("Health Conditions (comma-separated)",value=l.strip(","))
                  l=""
                  for i in user["nonVegDays"]:
                     l=l+i+","
                  non_veg_days = st.text_area("Non-Veg Days (comma-separated)",value=l.strip(","))
                
                  if st.button("Update"):
                      st.session_state.button3= True
                      
                  if st.session_state.button3:
                      users_collection.update_one({"_id": ObjectId(user_id)}, 
                                        {"$set": {"name":name,"email": email,"dob":dob,"contact":contact,"addresses":addresses,
                                                 "foodChoices": food_choices,"foodPreferences":food_preferences.split(","),
                                                 "healthConditions":health_conditions.split(","),"nonVegDays":non_veg_days.split(",")}})
                      st.session_state.button3=False
                      st.success("User updated successfully!")
                     

    elif action == "Delete":
        user_id = st.text_input("Enter User ID to delete")
        
        if 'button1' not in st.session_state:
             st.session_state.button1 = False
        if 'button2' not in st.session_state:
             st.session_state.button2 = False

        if st.button("Search User"):
             st.session_state.button1 = not st.session_state.button1
        if not user_id:
            st.stop()
        if st.session_state.button1:
             user = users_collection.find_one({"_id": ObjectId(user_id)})
             st.write(user)
             if st.button("Delete User"):
               st.session_state.button2 = not st.session_state.button2
             if st.session_state.button2:
                 users_collection.delete_one({"_id": ObjectId(user_id)})
                 st.success("User deleted successfully!")

    elif action == "Search":
        user_id = st.text_input("Enter User ID to search")
        if st.button("Search User"):
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            st.write(user)

# CRUD operations for Restaurants
def restaurant_operations():
    st.subheader("Restaurant Operations")
    action = st.selectbox("Select Action", ["Create", "Read", "Update", "Delete", "Search"])

    if action == "Create":
        name = st.text_input("Restaurant Name")
        address = st.text_input("Address")
        contact=st.text_input("Contact")
        google_pin = st.text_input("Google Pin")
        branches = st.text_area("Branches (comma-separated)")
        menu = st.text_area("Menu (dish : portion : price,comma-separated)")
        menu = [{"dish": item.split(":")[0].strip(), "portion": item.split(":")[1].strip(), "price": int(item.split(":")[2].strip())} for item in menu.split(",") if item.strip()]

        if st.button("Create Restaurant"):
            restaurants_collection.insert_one({
                "name": name,
                "address": address,
                "googlePin": google_pin,
                "branches": branches,
                "menu": menu,
                "contact":contact
            })
            st.success("Restaurant created successfully!")

    elif action == "Read":
        display_collection(restaurants_collection)

    elif action == "Update":
        rest_id = st.text_input("Enter Restaurant ID to update")
        if 'button1' not in st.session_state:
             st.session_state.button1 = False
        if 'button2' not in st.session_state:
             st.session_state.button2 = False
        if 'button3' not in st.session_state:
             st.session_state.button3 = False

        if st.button("Search User"):
             st.session_state.button1 =True
             st.session_state.button2 = False
             st.session_state.button3 = False
        if not rest_id:
            st.stop()
        if st.session_state.button1:
            user = restaurants_collection.find_one({"_id": ObjectId(rest_id)})
            st.write(user)
            if st.button("Edit User"):
               st.session_state.button2= True
               st.session_state.button3 = False

            if st.session_state.button2:
                  st.write(f"**rest id: {rest_id}**")
                  name = st.text_input("Name",value=user['name'])
                  st1=""
                  if type(user["menu"])== str:
                    u=user["menu"].replace("'", '"')
                    for i in json.loads(u):
                        st1=st1+i["dish"]+":"+i["portion"]+":"+str(i["price"])+","
                  else:
                    for i in user['menu']:
                        st1=st1+i["dish"]+":"+i["portion"]+":"+str(i["price"])+","

                  menu=st.text_input("Menu",value=st1.strip(","))
                  menu = [{"dish": item.split(":")[0].strip(), "portion": item.split(":")[1].strip(), "price": int(item.split(":")[2].strip())} for item in menu.split(",") if item.strip()]
                  contact=st.text_input("Contact No",value=user['contact'])
                  addresses = st.text_area("Addresses ",value=user["address"])
                  googlePin = st.text_input("GooglePin",value=user['googlePin'])
                  branches=st.text_area("Branches ",value=user["branches"])
                
                  if st.button("Update"):
                      st.session_state.button3= True
                      
                  if st.session_state.button3:
                      restaurants_collection.update_one({"_id": ObjectId(rest_id)}, 
                                        {"$set": {"name":name,"menu": menu ,"contact":contact,"address":addresses,
                                                 "googlePin":googlePin,"branches":branches}})
                      st.session_state.button3= False
                      st.success("Restaurant updated successfully!")
            

    elif action == "Delete":
        rest_id = st.text_input("Enter Restaurant ID to delete")
        if 'button1' not in st.session_state:
             st.session_state.button1 = False
        if 'button2' not in st.session_state:
             st.session_state.button2 = False

        if st.button("Search User"):
             st.session_state.button1 = True
             st.session_state.button2 = False
        if not rest_id:
            st.stop()
        if st.session_state.button1:
             user = users_collection.find_one({"_id": ObjectId(rest_id)})
             st.write(user)
             if st.button("Delete Restaurant"):
               st.session_state.button2 = True
             if st.session_state.button2:
                 users_collection.delete_one({"_id": ObjectId(rest_id)})
                 st.session_state.button2 = False
                 st.success("Restaurant deleted successfully!")


    elif action == "Search":
        rest_id = st.text_input("Enter Restaurant ID to search")
        if st.button("Search Restaurant"):
            restaurant = restaurants_collection.find_one({"_id": ObjectId(rest_id)})
            st.write(restaurant)

# CRUD operations for Orders
def order_operations():
    st.subheader("Order Operations")
    action = st.selectbox("Select Action", ["Create", "Read", "Update", "Delete", "Search"])

    if action == "Create":
        order_id = st.text_input("Order ID")
        date=st.date_input("Date")
        time = st.time_input("Time")
        customer_id = st.text_input("Customer ID")
        customer_name = st.text_input("Customer Name")
        customer_contact = st.text_input("Customer Contact")
        delivery_address = st.text_input("Delivery Address")
        delivery_pin = st.text_input("Delivery Google Pin")
        resto_name = st.text_input("Restaurant Name")
        resto_address = st.text_input("Restaurant Address")
        resto_pin = st.text_input("Restaurant Google Pin")
        distance = st.number_input("Distance (in kms)")
        upi_ack_id = st.text_input("UPI Acknowledgement ID")
        upi_status = st.text_input("UPI Status")
        dish_details = st.text_area("Dish Details (dish : portion : price, comma-separated)")
        dish_details = [{"dish": item.split(":")[0].strip(), "portion": item.split(":")[1].strip(), "price": int(item.split(":")[2].strip())} for item in dish_details.split(",") if item.strip()]

        if st.button("Create Order"):
            orders_collection.insert_one({
                "orderDetails": {"orderId": order_id, "datetime": str(date)+" "+str(time)},
                "dishDetails": dish_details,
                "customerDetails": {"customerId": customer_id, "name": customer_name, "contact": customer_contact},
                "deliveryAddress": {"address": delivery_address, "googlePin": delivery_pin},
                "restoDetails": {"name": resto_name, "address": resto_address, "googlePin": resto_pin},
                "distance": distance,
                "upiDetails": {"ackId": upi_ack_id, "status": upi_status}
            })
            st.success("Order created successfully!")

    elif action == "Read":
        display_collection(orders_collection)

    elif action == "Update":
        order_id = st.text_input("Enter Order ID or _id to update")
        if 'button1' not in st.session_state:
             st.session_state.button1 = False
        if 'button2' not in st.session_state:
             st.session_state.button2 = False
        if 'button3' not in st.session_state:
             st.session_state.button3 = False
             

        if st.button("Search order"):
             st.session_state.button1 = True
             st.session_state.button2 = False
             st.session_state.button3 = False
        if not order_id:
            st.stop()
        if st.session_state.button1:
            order = orders_collection.find_one({"_id": ObjectId(order_id)})
            st.write(order)
            if st.button("Edit User"):
               st.session_state.button2= True
               st.session_state.button3 = False

            if st.session_state.button2:
                  st.write(f"**rest id: {order_id}**")
                  date=st.date_input("Date")
                  time = st.time_input("Time")
                  customer_id = st.text_input("Customer ID",value=order["customerDetails"]["customerId"])
                  customer_name = st.text_input("Customer Name",value=order["customerDetails"]['name'])
                  customer_contact = st.text_input("Customer Contact",value=order["customerDetails"]['contact'])
                  delivery_address = st.text_input("Delivery Address",value=order["deliveryAddress"]["address"])
                  delivery_pin = st.text_input("Delivery Google Pin",value=order["deliveryAddress"]["googlePin"])
                  resto_name = st.text_input("Restaurant Name",value=order["restoDetails"]["name"])
                  resto_address = st.text_input("Restaurant Address",value=order["restoDetails"]["address"])
                  resto_pin = st.text_input("Restaurant Google Pin",value=order["restoDetails"]["googlePin"])
                  distance = st.number_input("Distance (in kms)",value=order["distance"])
                  upi_ack_id = st.text_input("UPI Acknowledgement ID",value=order["upiDetails"]["ackId"])
                  upi_status = st.text_input("UPI Status",value=order["upiDetails"]["status"])
                  st_l=""
                  for i in order["dishDetails"]:
                     i=list(i.values())
                     l_str = [str(item) for item in i]
                     l=":".join(l_str)
                     st_l=st_l + l + ","
                  dish_details = st.text_area("Dish Details (dish : portion : price, comma-separated)",value=st_l.strip(','))
                  dish_details = [{"dish": item.split(":")[0].strip(), "portion": item.split(":")[1].strip(), "price": int(item.split(":")[2].strip())} for item in dish_details.split(",") if item.strip()]
                
                  if st.button("Update"):
                      st.session_state.button3= True
                      
                  if st.session_state.button3:
                      orders_collection.update_one({"_id": ObjectId(order_id)}, 
                                        {"$set": {"orderDetails":{"datetime": str(date)+" "+str(time)},"dishDetails": dish_details,
                "customerDetails": {"customerId": customer_id, "name": customer_name, "contact": customer_contact},
                "deliveryAddress": {"address": delivery_address, "googlePin": delivery_pin},
                "restoDetails": {"name": resto_name, "address": resto_address, "googlePin": resto_pin},
                "distance": distance,
                "upiDetails": {"ackId": upi_ack_id, "status": upi_status}}})
                      st.session_state.button3= False
                      st.success("Restaurant updated successfully!")

    elif action == "Delete":
        order_id = st.text_input("Enter Order ID to delete")
        if 'button1' not in st.session_state:
             st.session_state.button1 = False
        if 'button2' not in st.session_state:
             st.session_state.button2 = False

        if st.button("Search order"):
             st.session_state.button1 = True
             st.session_state.button2 = False
        if not order_id:
            st.stop()
        if st.session_state.button1:
             user = orders_collection.find_one({"_id": ObjectId(order_id)})
             st.write(user)
             if st.button("Delete Order"):
               st.session_state.button2 = True
             if st.session_state.button2:
                 orders_collection.delete_one({"_id": ObjectId(order_id)})
                 st.session_state.button2 = False
                 st.success("Order deleted successfully!")

    elif action == "Search":
        order_id = st.text_input("Enter Order ID to search")
        if st.button("Search Order"):
            order = orders_collection.find_one({"_id": ObjectId(order_id)})
            st.write(order)

# CRUD operations for Food Images
def food_image_operations():
    st.subheader("Food Image Operations")
    action = st.selectbox("Select Action", ["Create", "Read", "Update", "Delete", "Search"])
    fs = gridfs.GridFS(db)
    if action == "Create":
        dish_name = st.text_input("Dish Name")
        image = st.file_uploader("Upload image",type=["jpg","png","jpeg"])
        
        if not image:
            st.stop()
        save_img="food_images"
        save_path=Path(save_img,image.name)
       

        with open(save_path,mode='wb') as w:
            w.write(image.getvalue())
        
        if st.button("Add Food Image"):
            with open(save_path, "rb") as f:
                image_data = f.read()

         # Store the image in GridFS
            image_id = fs.put(image_data, filename=str(save_path))

          # Store the dish details in the collection
            dish_document = {
            "dish": dish_name,
            "image_id": image_id
          }

            food_images_collection.insert_one(dish_document)
            st.success("Food name and image added successfully!")

    elif action == "Read":
        for food_image in food_images_collection.find():
            dish_name = food_image["dish"]
            image_id = food_image["image_id"]

            # Retrieve the image by its ID
            stored_image = fs.get(image_id)

            # Read the image data
            image_data = stored_image.read()

            # Convert binary data to an image
            image = Image.open(io.BytesIO(image_data))

            # Display the dish name and image
            st.write(dish_name)
            st.image(image)
            

    elif action == "Update":
        dish_name = st.selectbox("Enter Dish Name to search", [food_image["dish"] for food_image in food_images_collection.find()]) 
        if 'button1' not in st.session_state:
             st.session_state.button1 = False
        if 'button2' not in st.session_state:
             st.session_state.button2 = False
        if 'button3' not in st.session_state:
             st.session_state.button3 = False

        if st.button("Search food"):
             st.session_state.button1 = True
             st.session_state.button2 = False
             st.session_state.button3 = False
        if st.session_state.button1:
            try:
                food_image=food_images_collection.find_one({"dish":f"{dish_name}"})
                dish_name = food_image["dish"]
                orig=dish_name
                image_id = food_image["image_id"]
                # Retrieve the image by its ID
                stored_image = fs.get(image_id)

                # Read the image data
                image_data = stored_image.read()

                # Convert binary data to an image
                image = Image.open(io.BytesIO(image_data))

                # Display the dish name and image
                st.write(dish_name)
                st.image(image)
            except:
                st.write("Image not found / check the spelling as it is casesensitive")
            if st.button("Edit Image"):
                 st.session_state.button2 = True
                 st.session_state.button3 = False
            if st.session_state.button2:
                dish_name = st.text_input("Update Dish Name",value=dish_name)
                image = st.file_uploader("Update image",type=["jpg","png","jpeg"])
                if not image:
                    st.stop()
              
                save_img="food_images"
                save_path=Path(save_img,image.name)
                
                with open(save_path,mode='wb') as w:
                   w.write(image.getvalue())
                with open(save_path, "rb") as f:
                  image_data = f.read()
                st.image(save_img+"/"+image.name)
                if st.button("Update Image"):
                    st.session_state.button3= True
                if st.session_state.button3:
                    # delete
                    fs.delete(image_id)
                    id=food_images_collection.find_one({"dish": orig})
                    food_images_collection.delete_one({"_id": ObjectId(id["_id"])})
                    # add
                    image_id=fs.put(image_data,filename=str(save_path))
                    dish_document = {
                    "dish": dish_name,
                    "image_id": image_id}
                    food_images_collection.insert_one(dish_document)
                    st.session_state.button3=False
                    st.success("Image updated successfully!")
                    

    elif action == "Delete":
        dish_name = st.selectbox("Enter Dish Name to delete", (food_image["dish"] for food_image in food_images_collection.find())) 
        if not dish_name:
            st.warning("No image found, please upload!")
            st.stop()
        if 'button1' not in st.session_state:
             st.session_state.button1 = False
        if 'button2' not in st.session_state:
             st.session_state.button2 = False
        if st.button("Search food"):
            st.session_state.button1 = True
            st.session_state.button2 = False
        if st.session_state.button1: 
            food_image=food_images_collection.find_one({"dish":f"{dish_name}"})
            dish_name = food_image["dish"]
            orig=dish_name
            image_id = food_image["image_id"]
            # Retrieve the image by its ID
            stored_image = fs.get(image_id)
            # Read the image data
            image_data = stored_image.read()
            # Convert binary data to an image
            image = Image.open(io.BytesIO(image_data))
            # Display the dish name and image
            st.write(dish_name)
            st.image(image)

            if st.button("Delete food image"):
               st.session_state.button2 = True
            if st.session_state.button2: 
                food_image=food_images_collection.find_one({"dish":f"{dish_name}"})
                dish_name = food_image["dish"]
                orig=dish_name
                image_id = food_image["image_id"]
                # Delete the dish name and image
                fs.delete(image_id)
                id=food_images_collection.find_one({"dish": orig})
                food_images_collection.delete_one({"_id": ObjectId(id["_id"])})
                st.success("Image deleted successfully!")
                st.session_state.button2 = False
                st.stop()
      
                

    elif action == "Search":
        dish_name = st.selectbox("Enter Dish Name to search", (food_image["dish"] for food_image in food_images_collection.find())) 
        if st.button("Search Image"):
            try:
                food_image=food_images_collection.find_one({"dish":f"{dish_name}"})
                dish_name = food_image["dish"]
                image_id = food_image["image_id"]
                # Retrieve the image by its ID
                stored_image = fs.get(image_id)

                # Read the image data
                image_data = stored_image.read()

                # Convert binary data to an image
                image = Image.open(io.BytesIO(image_data))

                # Display the dish name and image
                st.write(dish_name)
                st.image(image)
            except:
                st.write("Image not found / check the spelling as it is casesensitive")

# Main function to run the app
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            admin = admin_collection.find_one({"admin_id": username, "password": password})
            if admin:
                st.session_state['logged_in'] = True
                st.success("Login successful!")
            else:
                st.error("Invalid username or password.")
    else:
        st.title("Admin Dashboard")
        option = st.sidebar.selectbox("Choose an option", ["User Operations", "Restaurant Operations", "Order Operations", "Food Image Operations"])
        
        if option == "User Operations":
            user_operations()
        elif option == "Restaurant Operations":
            restaurant_operations()
        elif option == "Order Operations":
            order_operations()
        elif option == "Food Image Operations":
            food_image_operations()
        
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False

if __name__ == "__main__":
    main()