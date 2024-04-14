import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3
from sqlalchemy import create_engine

def image_to_text(path):

    input_img= Image.open(path)

    #converting image to array format
    image_arr= np.array(input_img)

    reader= easyocr.Reader(['en'])
    text= reader.readtext(image_arr,detail= 0)
    return text,input_img

def extracted_text(texts):
    extrd_dict = {"NAME":[],"DESIGNATION":[],"COMPANY_NAME":[],"CONTACT":[],"EMAIL":[],
                  "WEBSITE":[],"ADDRESS":[],"PINCODE":[]}
    extrd_dict["NAME"].append(texts[0])
    extrd_dict["DESIGNATION"].append(texts[1])

    for i in range(2,len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
            extrd_dict["CONTACT"].append(texts[i])

        elif "@" in texts[i] and ".com" in texts[i]:
            small =texts[i].lower()
            extrd_dict["EMAIL"].append(small)

        elif "www" in texts[i].lower():
            small = texts[i].lower()
            extrd_dict["WEBSITE"].append(small)

        elif "Tamil Nadu" in texts[i]  or "TamilNadu" in texts[i] or texts[i].isdigit():
            extrd_dict["PINCODE"].append(texts[i])

        elif re.match(r'^[A-Za-z]',texts[i]):
            extrd_dict["COMPANY_NAME"].append(texts[i])

        else:
            remove_colon = re.sub(r'[,;]', '', texts[i])
            extrd_dict["ADDRESS"].append(remove_colon)

    for key,value in extrd_dict.items():
        if len(value)>0:
            concadenate = ' '.join(value)
            extrd_dict[key] = [concadenate]
        else:
            value = 'NA'
            extrd_dict[key] = [value]

    return extrd_dict

# Streamlit Part

st.set_page_config(layout= "wide")

st.title("EXTRACTING BUSINESS CARD DATA WITH 'OCR'")
st.write("")


with st.sidebar:
  select= option_menu("Main Menu",["Home", "Upload&Modify", "Cleaned Data","Delete"])

if select == "Home":
  st.markdown("### :blue[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")



  st.write(
            "### :green[**About :**] Bizcard is a Python application designed to extract information from business cards.")
  st.write(
            '### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')

elif select == "Upload&Modify":

  img= st.file_uploader("Upload the Image", type= ["png", "jpg", "jpeg"], label_visibility= "visible")

  if img is not None:
    st.image(img,width= 300)

    text_image,input_img= image_to_text(img)
    text_dict= extracted_text(text_image)

    if text_dict:
      st.success("TEXT IS EXTRACTED SUCCESSFULLY")


    df= pd.DataFrame(text_dict)

    #Converting Image to Bytes
    Image_bytes= io.BytesIO()
    input_img.save(Image_bytes,format= "PNG")

    image_data= Image_bytes.getvalue()

    #Creating dictionary
    data= {"Image":[image_data]}
    df_1= pd.DataFrame(data)

    concat_df= pd.concat([df,df_1],axis=1)

    button3= st.button("Save",use_container_width= True)

    if button3:
        conn = sqlite3.connect('bizcardx.db')

        table_name = 'bizcard_details1'
        columns = concat_df.columns.tolist()
     # Define the table creation query
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS bizcard_details1 (
            NAME varchar(225),
            DESIGNATION varchar(225),
            COMPANY_NAME varchar(225),
            CONTACT varchar(225),
            EMAIL text,
            WEBSITE text,
            ADDRESS text,
            PINCODE varchar(225)
            
        )'''.format(table_name)

        conn.execute(create_table_query)
        conn.commit()

        for index, row in concat_df.iterrows():
            insert_query = '''
                    INSERT INTO bizcard_details1 ("NAME","DESIGNATION","COMPANY_NAME","CONTACT",
                                      "EMAIL","WEBSITE","ADDRESS","PINCODE")
            VALUES (?,?,?,?,?,?,?,?)
            '''
            values= (row['NAME'], row['DESIGNATION'], row['COMPANY_NAME'], row['CONTACT'],
                    row['EMAIL'], row['WEBSITE'], row['ADDRESS'], row['PINCODE'])

            # Execute the insert query
            conn.execute(insert_query,values)

            # Commit the changes
            conn.commit()
  else:
    conn = sqlite3.connect('bizcardx.db')
    cursor = conn.cursor()
    
    query= "select * from bizcard_details1"
    cursor.execute(query)
    
    table = cursor.fetchall()
    conn.commit()

    text_dict= pd.DataFrame(table, columns= ["NAME","DESIGNATION","COMPANY_NAME","CONTACT",
                                      "EMAIL","WEBSITE","ADDRESS","PINCODE"])
     
  method= st.radio("Select the Option",["None","Preview","Modify"])
  if method == "None":
    st.write("")


  if method == "Preview":
    try:
      df= pd.DataFrame(text_dict)
      
      st.image(input_img, width = 350)

      st.dataframe(df)
    except:
       st.markdown("<p style='color:yellow;'>selected the Image after choose the selected image preview</p>", unsafe_allow_html=True)

  elif method == "Modify":

    
    concat_df= pd.DataFrame(text_dict)


    conn = sqlite3.connect('bizcardx.db')
    cursor = conn.cursor()
    
    query= "select * from bizcard_details1"
    cursor.execute(query)
    
    table = cursor.fetchall()
    conn.commit()

    df3= pd.DataFrame(table, columns= ["NAME","DESIGNATION","COMPANY_NAME","CONTACT",
                                      "EMAIL","WEBSITE","ADDRESS","PINCODE"])

    st.dataframe(df3)

    col1,col2= st.columns(2)
    with col1:
      select_name = st.selectbox("Select the Name",df3["NAME"])
    
    df4 = df3[df3["NAME"]==select_name]
    #st.write("")

    col1,col2= st.columns(2)
    with col1:
        modify_name= st.text_input("Name", df4["NAME"].unique()[0])
        modify_desig= st.text_input("Designation", df4["DESIGNATION"].unique()[0])
        modify_company= st.text_input("Company_Name", df4["COMPANY_NAME"].unique()[0])
        modify_contact= st.text_input("Contact", df4["CONTACT"].unique()[0])

        concat_df["NAME"] = modify_name
        concat_df["DESIGNATION"] = modify_desig
        concat_df["COMPANY_NAME"] = modify_company
        concat_df["CONTACT"] = modify_contact

    with col2:
        modify_email= st.text_input("Email", df4["EMAIL"].unique()[0])
        modify_web= st.text_input("Website", df4["WEBSITE"].unique()[0])
        modify_address= st.text_input("Address", df4["ADDRESS"].unique()[0])
        modify_pincode= st.text_input("Pincode", df4["PINCODE"].unique()[0])

        concat_df["EMAIL"] = modify_email
        concat_df["WEBSITE"] = modify_web
        concat_df["ADDRESS"] = modify_address
        concat_df["PINCODE"] = modify_pincode

    col1,col2= st.columns(2)
    with col1:
      button3= st.button("Modify",use_container_width= True)

    if button3:
      conn = sqlite3.connect('bizcardx.db')
      cursor = conn.cursor()


      cursor.execute(f"DELETE FROM bizcard_details1 WHERE NAME ='{select_name}'")
      conn.commit()

      for index, row in concat_df.iterrows():
          insert_query = '''
                  INSERT INTO bizcard_details1 ("NAME","DESIGNATION","COMPANY_NAME","CONTACT",
                                      "EMAIL","WEBSITE","ADDRESS","PINCODE")
          VALUES (?,?,?,?,?,?,?,?)
          '''
          values= (row['NAME'], row['DESIGNATION'], row['COMPANY_NAME'], row['CONTACT'],
                  row['EMAIL'], row['WEBSITE'], row['ADDRESS'], row['PINCODE'])

          # Execute the insert query
          conn.execute(insert_query,values)

          # Commit the changes
          conn.commit()


      conn = sqlite3.connect('bizcardx.db')
      cursor = conn.cursor()
      
      query= "select * from bizcard_details1"
      cursor.execute(query)
      
      table = cursor.fetchall()
      conn.commit()

      df6= pd.DataFrame(table, columns= ["NAME","DESIGNATION","COMPANY_NAME","CONTACT",
                                        "EMAIL","WEBSITE","ADDRESS","PINCODE"])

      st.dataframe(df6)

      st.success("MODIFIED SUCCESSFULLY")



if select == "Cleaned Data":        
  conn = sqlite3.connect('bizcardx.db')
  cursor= conn.cursor()
  query= "select * from bizcard_details1"
  cursor.execute(query)
  table=cursor.fetchall()
  conn.commit()
  Cleaned_data= pd.DataFrame(table, columns= ["NAME","DESIGNATION","COMPANY_NAME","CONTACT",
                                        "EMAIL","WEBSITE","ADDRESS","PINCODE"])

  st.dataframe(Cleaned_data)



if select == "Delete":

  conn = sqlite3.connect('bizcardx.db')
  cursor= conn.cursor()

  col1,col2= st.columns(2)
  with col1:
    cursor.execute("SELECT NAME FROM bizcard_details1")
    conn.commit()
    table1= cursor.fetchall()

    names=[]

    for i in table1:
      names.append(i[0])

    name_select= st.selectbox("Select the Name",options= names)

  with col2:
    cursor.execute(f"SELECT DESIGNATION FROM bizcard_details1 WHERE NAME ='{name_select}'")
    conn.commit()
    table2= cursor.fetchall()

    designations= []

    for j in table2:
      designations.append(j[0])

    designation_select= st.selectbox("Select the Designation", options= designations)

  if name_select and designation_select:
    col1,col2,col3= st.columns(3)

    with col1:
      st.write(f"Selected Name : {name_select}")
      st.write("")
      st.write("")

      st.write(f"Selected Designation : {designation_select}")

    with col2:
      st.write("")
      st.write("")
      st.write("")
      st.write("")
      remove= st.button("Delete",use_container_width= True)

      if remove:
        conn.execute(f"DELETE FROM bizcard_details1 WHERE NAME ='{name_select}' AND DESIGNATION = '{designation_select}'")
        conn.commit()

        st.warning("DELETED")