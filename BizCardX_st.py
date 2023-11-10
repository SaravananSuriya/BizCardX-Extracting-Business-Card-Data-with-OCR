from PIL import Image
import easyocr
import cv2
import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
import sqlite3

# Creating a DataBase, cursor and table in "sqlite3"
try:
  db = sqlite3.connect('Bizcardx.db')
  cursor = db.cursor()
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS Card (
        Card_Holder varchar(50),
        Designation varchar(100),
        Company_Name varchar(100),
        Phone_Number varchar(30),
        E_mail varchar(100),
        Website varchar(100),
        Address text,
        Image_Data BLOB
      )
  ''')
  db.commit()
except:
  pass

# opening the image using "PIL" package to use images in our application
img = Image.open('/content/0x300a0a0.jpeg')
img1 = Image.open('/content/download.jpeg')

# Setting a page Configuration as our wish
st.set_page_config(page_title = 'BizCardX Project', layout = 'wide',page_icon = img1)

selected = option_menu('Extracting Business Card Data with OCR', ["Home", "Upload & Extract", "Modify", 'Delete'], 
    icons=['house', 'cloud-arrow-up-fill', "folder-check", 'trash3'], 
    menu_icon='image-fill', default_index=0, orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#0097FF"},
        "icon": {"color": "black", "font-size": "25px"}, 
        "nav-link": {"font-size": "20px", "text-align": "center", "margin":"0px", "--hover-color": "#800080"},
        "nav-link-selected": {"background-color": "#CCCCFF"},
    }
)

# If selcted a first page 'Home'
if selected == 'Home':

  # Giving Description of Overall Project
  col1,col2 = st.columns([2,3], gap = 'small')
  with col1:
    st.image(img)
  with col2:
    st.markdown('## :blue[Project Title:]')
    st.markdown("### &nbsp; &nbsp; &nbsp; &nbsp; BizCardX: Extracting Business Card Data with OCR.")
    st.markdown("## :blue[Technologies:]")
    st.markdown("### &nbsp; &nbsp; &nbsp; &nbsp;  OCR,streamlit GUI, SQL,Data Extraction.")
  st.markdown("## :blue[About OCR:]")
  st.markdown("### &nbsp; &nbsp; &nbsp; &nbsp;  Optical Character Recognition (OCR) is the process that converts an image of text into a machine-readable text format. It is used to convert the image into a text document with its contents stored as text data.")
  st.markdown("## :blue[Problem Statement:]")
  st.markdown("### &nbsp; &nbsp; &nbsp; &nbsp; You have been tasked with developing a Streamlit application that allows users to upload an image of a business card and extract relevant information from it using easyOCR.")
  st.markdown("## :blue[Results:]")
  st.markdown("### &nbsp; &nbsp; &nbsp; &nbsp; The result of the project would be a Streamlit application that allows users to upload an image of a business card and extract relevant information from it using easyOCR.")

# If selcted a second page 'Upload & Extract' 
elif selected == 'Upload & Extract':
  col1,col2,col3 = st.columns([1,9,1], gap = 'small')
  with col2:
    # Upload file through Streamlit
    st.markdown("### :rainbow[👇🏻 Upload an image to perform easyOCR 👇🏻]")
    img = st.file_uploader(label='', type=['jpg', 'jpeg', 'png'])

    List = [] # this list is used in database function argument
    # this function is used to upload and read the image 
    def upload(img):
      # Check if an image is uploaded
      if img is not None:
        reader = easyocr.Reader(['en'])
      # Read the content of the uploaded file as bytes
        img_bytes = img.read()
        # Convert the bytes to numpy array and decode the image
        np_img = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        #setting a global variable to use this variable in another function
        global img_data
        img_data = img_bytes
        st.markdown('## :rainbow[Your uploaded Image :]')
        st.image(img,width = 700)
        st.markdown('')
        st.markdown('')
        with st.spinner('Please Wait....'):
          global result
          # this is the code to read the image
          result = reader.readtext(img, detail=0)
        st.markdown('')
        st.markdown('## :rainbow[Extracted data from your upload image:]')
        # from the image extracting the data and transpose the shape and push in to the dataframe table
        df = pd.DataFrame(result)
        z=np.array(df).T
        df1 = pd.DataFrame(z)
        st.write(df1)
        List.extend(result)
    upload(img)
    
    # this function is used to save the data to database
    def database(lst):
      st.markdown('')
      st.markdown('')
      st.write(':red[👇🏻 Click below button to Store in SQL]')
      but1 = st.button('Store') # this is the button to store the data in SQL
      if but1:
        with st.spinner('Wait for it...'):
          if len(lst) == 0:
            st.error("Error: Image not uploaded. Upload the image then try again!⛔️")
          else:
            # here we connecting to database and cursor to execute the query
            db = sqlite3.connect('Bizcardx.db')
            cursor = db.cursor()
            cursor.execute('SELECT Card_Holder FROM Card')
            name = []
            for i in cursor:
              name.append(i[0])
            if result[0] not in name:
              # in below line creating a dictionary to store the data from the image
              dic = {'Card_holder':[],'Designation':[],'Phone_Number':[],'E_mail':[],'Website':[],'Address':[],'Company_Name':[]}
              for i in result: # this 'result' variable contains a image extracted data
                # in this if statement trying to get 'Card Holder' name and 'Designation' and append it to the 'dic' dictionary
                if len(dic['Card_holder']) <1 and len(dic['Designation']) <1 :
                  dic['Card_holder'].append(result[0])
                  dic['Designation'].append(result[1])
                # in this if statement trying to get 'Phone number' and append it to the 'dic' dictionary
                if '-' in i or '+' in i:
                  dic['Phone_Number'].append(i)
                # in this if statement trying to get 'Address' and append it to the 'dic' dictionary
                if '123 ' in i or 'Tamil' in i or 'Er' in i:
                  dic['Address'].append(i)
                # in this if statement trying to get 'mail-id' and append it to the 'dic' dictionary
                if '@' in i and 'www' not in i.lower():
                  dic['E_mail'].append(i)
                # in this if statement trying to get 'Website' and append it to the 'dic' dictionary
                if 'www' in i.lower() or '@' not in i and '.com' in i:
                  dic['Website'].append(i)
                # in this if statement trying to get 'Address' and append it to the 'dic' dictionary
                if i.isnumeric():
                  dic['Address'].append(i)
                # in this if statement trying to get 'Company Name' and append it to the 'dic' dictionary
                end = result[-1]
                if i == end:
                  if len(i.split(' ')) == 2 and len(i) > 4:
                    dic['Company_Name'].append(i)
                  elif 'St' in i:
                    res = result[-4] + ' ' + result[-2]
                    dic['Company_Name'].append(res)
                  elif 'Ta' in result[-2] or 'www' in result[-2].lower():
                    res = result[-3] + ' ' + result[-1]
                    dic['Company_Name'].append(res)
                  else:
                    res = result[-2] + ' ' + result[-1]
                    dic['Company_Name'].append(res)

              # in below line combinig all the splitted address
              combined_address = ', '.join(dic['Address'])
              dic['Address'] = [combined_address]

              # in below if statement combinig all the splitted Websites
              if len(dic['Website']) == 2:
                combined_site = ', '.join(dic['Website'])
                dic['Website'] = [combined_site]
              
              # in below if statement combinig all the splitted Phone number
              if len(dic['Phone_Number']) == 2:
                combined_no = ', '.join(dic['Phone_Number'])
                dic['Phone_Number'] = [combined_no]

              # here we connecting to database and cursor to insert the values from 'dic' dictionary
              db = sqlite3.connect('Bizcardx.db')
              cursor = db.cursor()
              cursor.execute("INSERT INTO Card (Card_Holder,Designation,Company_Name,Phone_Number,E_mail,Website,Address,Image_Data) VALUES (?,?,?,?,?,?,?,?)", (dic['Card_holder'][0],dic['Designation'][0],dic['Company_Name'][0],dic['Phone_Number'][0],dic['E_mail'][0],dic['Website'][0],dic['Address'][0],sqlite3.Binary(img_data)))
              db.commit()
              st.success('✅Sucessfully Uploaded in DataBase!')
              st.markdown('## :rainbow[Saved data in SQL:]')
              db = sqlite3.connect('Bizcardx.db')
              # in below code executing the query to show all saved datas
              qry ="SELECT * FROM Card"
              df = pd.read_sql_query(qry,db)
              st.dataframe(df)
              cursor.close()
              db.close()
            else:
              st.warning("⚠️ Already exists in DataBase")
    database(List)

# If selcted a third page 'Modify' 
elif selected == 'Modify':
  st.subheader(':red[👇🏻Select any Card Holder Name to Modify their Data👇🏻]')
  # in below code connecting to database and cursor to excute query and getting card holder name and append to the 'name' list
  db = sqlite3.connect('Bizcardx.db')
  cursor = db.cursor()
  cursor.execute('SELECT Card_Holder FROM Card')
  name = []
  for i in cursor:
    name.append(i[0])
  # in below code creating selectbox to select card holder name from 'name' list and executing the query and showing in dataframe
  option = st.selectbox(label = "",options = name,index = None,placeholder='Select any name')
  qry =f"SELECT * FROM Card WHERE Card_Holder = '{option}'"
  df = pd.read_sql_query(qry,db)
  st.dataframe(df,use_container_width=True)
  st.markdown('')
  st.markdown('')
  # in below code creating multiselect option to modify the data in SQL
  choice = ['Card_Holder','Designation','Company_Name','Phone_Number','E_mail','Website','Address']
  st.markdown('### :red[👇🏻Choose a Field to Modify]')
  st.info("NOTE: If you want to change **Card Holder Name**, Please select at last option. Don't choose at first or middle.")
  val = st.multiselect('',options=choice)

  # this if-elif-else statement is used to alter the data by using multiselect option
  if len(val) == 0:
    pass
  elif len(val) == 1:
    # getting a data where user select by their wish
    cursor.execute(f"SELECT {val[0]} FROM Card WHERE Card_Holder = '{option}'")
    result = cursor.fetchone()
    try:
      a = st.text_input(label=f'{val[0]}',value=result[0])
    except:
      pass
    button = st.button("Submit") # creating a button to update the values in SQl
    if button:
      try:
        update_query = f"UPDATE Card SET '{val[0]}' = '{a}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query)
        db.commit()
        st.success('Successfully Updated✅')
        st.markdown('')
        st.markdown('### :red[Here is your Modified Data]')
        qry = f"SELECT * FROM Card WHERE {val[0]} = '{a}'"
        df = pd.read_sql_query(qry,db)
        st.dataframe(df)
      except:
        st.error("Error: Card Holder Name not selected⛔️")

  elif len(val) == 2:
    cursor.execute(f"SELECT {val[0]},{val[1]} FROM Card WHERE Card_Holder = '{option}'")
    result = cursor.fetchmany()
    try:
      a1 = st.text_input(label=f'{val[0]}',value=result[0][0])
      b1 = st.text_input(label=f'{val[1]}',value=result[0][1])
    except:
      pass
    button = st.button("Submit")
    if button:
      try:
        update_query = f"UPDATE Card SET '{val[0]}' = '{a1}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query)
        update_query1 = f"UPDATE Card SET '{val[1]}' = '{b1}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query1)
        db.commit()
        st.success('Successfully Updated✅')
        st.markdown('')
        st.markdown('### :red[Here is your Modified Data]')
        qry = f"SELECT * FROM Card WHERE {val[0]} = '{a1}'"
        df = pd.read_sql_query(qry,db)
        st.dataframe(df)
      except:
        st.error("Error: Card Holder Name not selected⛔️")

  elif len(val) == 3:
    cursor.execute(f"SELECT {val[0]},{val[1]},{val[2]} FROM Card WHERE Card_Holder = '{option}'")
    result = cursor.fetchmany()
    try:
      a2 = st.text_input(label=f'{val[0]}',value=result[0][0])
      b2 = st.text_input(label=f'{val[1]}',value=result[0][1])
      c2 = st.text_input(label=f'{val[2]}',value=result[0][2])
    except:
      pass
    button = st.button("Submit")
    if button:
      try:
        update_query = f"UPDATE Card SET '{val[0]}' = '{a2}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query)
        update_query1 = f"UPDATE Card SET '{val[1]}' = '{b2}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query1)
        update_query2 = f"UPDATE Card SET '{val[2]}' = '{c2}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query2)
        db.commit()
        st.success('Successfully Updated✅')
        st.markdown('')
        st.markdown('### :red[Here is your Modified Data]')
        qry = f"SELECT * FROM Card WHERE {val[0]} = '{a2}'"
        df = pd.read_sql_query(qry,db)
        st.dataframe(df)
      except:
        st.error("Error: Card Holder Name not selected⛔️")


  elif len(val) == 4:
    cursor.execute(f"SELECT {val[0]},{val[1]},{val[2]},{val[3]} FROM Card WHERE Card_Holder = '{option}'")
    result = cursor.fetchmany()
    try:
      a3 = st.text_input(label=f'{val[0]}',value=result[0][0])
      b3 = st.text_input(label=f'{val[1]}',value=result[0][1])
      c3 = st.text_input(label=f'{val[2]}',value=result[0][2])
      d3 = st.text_input(label=f'{val[3]}',value=result[0][3])
    except:
      pass
    button = st.button("Submit")
    if button:
      try:
        update_query = f"UPDATE Card SET '{val[0]}' = '{a3}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query)
        update_query1 = f"UPDATE Card SET '{val[1]}' = '{b3}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query1)
        update_query2 = f"UPDATE Card SET '{val[2]}' = '{c3}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query2)
        update_query3 = f"UPDATE Card SET '{val[3]}' = '{d3}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query3)
        db.commit()
        st.success('Successfully Updated✅')
        st.markdown('')
        st.markdown('### :red[Here is your Modified Data]')
        qry = f"SELECT * FROM Card WHERE {val[0]} = '{a3}'"
        df = pd.read_sql_query(qry,db)
        st.dataframe(df)
      except:
        st.error("Error: Card Holder Name not selected⛔️")
  
  elif len(val) == 5:
    cursor.execute(f"SELECT {val[0]},{val[1]},{val[2]},{val[3]},{val[4]} FROM Card WHERE Card_Holder = '{option}'")
    result = cursor.fetchmany()
    try:
      a4 = st.text_input(label=f'{val[0]}',value=result[0][0])
      b4 = st.text_input(label=f'{val[1]}',value=result[0][1])
      c4 = st.text_input(label=f'{val[2]}',value=result[0][2])
      d4 = st.text_input(label=f'{val[3]}',value=result[0][3])
      e4 = st.text_input(label=f'{val[4]}',value=result[0][4])
    except:
      pass
    button = st.button("Submit")
    if button:
      try:
        update_query = f"UPDATE Card SET '{val[0]}' = '{a4}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query)
        update_query1 = f"UPDATE Card SET '{val[1]}' = '{b4}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query1)
        update_query2 = f"UPDATE Card SET '{val[2]}' = '{c4}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query2)
        update_query3 = f"UPDATE Card SET '{val[3]}' = '{d4}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query3)
        update_query4 = f"UPDATE Card SET '{val[4]}' = '{e4}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query4)
        db.commit()
        st.success('Successfully Updated✅')
        st.markdown('')
        st.markdown('### :red[Here is your Modified Data]')
        qry = f"SELECT * FROM Card WHERE {val[0]} = '{a4}'"
        df = pd.read_sql_query(qry,db)
        st.dataframe(df)
      except:
        st.error("Error: Card Holder Name not selected⛔️")
  
  elif len(val) == 6:
    cursor.execute(f"SELECT {val[0]},{val[1]},{val[2]},{val[3]},{val[4]},{val[5]} FROM Card WHERE Card_Holder = '{option}'")
    result = cursor.fetchmany()
    try:
      a5 = st.text_input(label=f'{val[0]}',value=result[0][0])
      b5 = st.text_input(label=f'{val[1]}',value=result[0][1])
      c5 = st.text_input(label=f'{val[2]}',value=result[0][2])
      d5 = st.text_input(label=f'{val[3]}',value=result[0][3])
      e5 = st.text_input(label=f'{val[4]}',value=result[0][4])
      f5 = st.text_input(label=f'{val[5]}',value=result[0][5])
    except:
      pass
    button = st.button("Submit")
    if button:
      try:
        update_query = f"UPDATE Card SET '{val[0]}' = '{a5}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query)
        update_query1 = f"UPDATE Card SET '{val[1]}' = '{b5}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query1)
        update_query2 = f"UPDATE Card SET '{val[2]}' = '{c5}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query2)
        update_query3 = f"UPDATE Card SET '{val[3]}' = '{d5}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query3)
        update_query4 = f"UPDATE Card SET '{val[4]}' = '{e5}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query4)
        update_query5 = f"UPDATE Card SET '{val[5]}' = '{f5}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query5)
        db.commit()
        st.success('Successfully Updated✅')
        st.markdown('')
        st.markdown('### :red[Here is your Modified Data]')
        qry = f"SELECT * FROM Card WHERE {val[0]} = '{a5}'"
        df = pd.read_sql_query(qry,db)
        st.dataframe(df)
      except:
        st.error("Error: Card Holder Name not selected⛔️")

  elif len(val) == 7:
    cursor.execute(f"SELECT {val[0]},{val[1]},{val[2]},{val[3]},{val[4]},{val[5]},{val[6]} FROM Card WHERE Card_Holder = '{option}'")
    result = cursor.fetchmany()
    try:
      a6 = st.text_input(label=f'{val[0]}',value=result[0][0])
      b6 = st.text_input(label=f'{val[1]}',value=result[0][1])
      c6 = st.text_input(label=f'{val[2]}',value=result[0][2])
      d6 = st.text_input(label=f'{val[3]}',value=result[0][3])
      e6 = st.text_input(label=f'{val[4]}',value=result[0][4])
      f6 = st.text_input(label=f'{val[5]}',value=result[0][5])
      g6 = st.text_input(label=f'{val[6]}',value=result[0][6])
    except:
      pass
    button = st.button("Submit")
    if button:
      try:
        update_query = f"UPDATE Card SET '{val[0]}' = '{a6}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query)
        update_query1 = f"UPDATE Card SET '{val[1]}' = '{b6}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query1)
        update_query2 = f"UPDATE Card SET '{val[2]}' = '{c6}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query2)
        update_query3 = f"UPDATE Card SET '{val[3]}' = '{d6}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query3)
        update_query4 = f"UPDATE Card SET '{val[4]}' = '{e6}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query4)
        update_query5 = f"UPDATE Card SET '{val[5]}' = '{f6}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query5)
        update_query6 = f"UPDATE Card SET '{val[6]}' = '{g6}' WHERE Card_Holder = '{option}'"
        cursor.execute(update_query6)
        db.commit()
        st.success('Successfully Updated✅')
        st.markdown('')
        st.markdown('### :red[Here is your Modified Data]')
        qry = f"SELECT * FROM Card WHERE {val[0]} = '{a6}'"
        df = pd.read_sql_query(qry,db)
        st.dataframe(df)
      except:
        st.error("Error: Card Holder Name not selected⛔️")

# If selcted a third page 'Delete' 
elif selected == 'Delete':
  st.subheader(':violet[👇🏻Select any Card to delete their Data👇🏻]')
  # below code connecting the database and cursor for executing the query and get the card holder name and company name
  db = sqlite3.connect('Bizcardx.db')
  cursor = db.cursor()
  cursor.execute('SELECT Card_Holder,Company_Name FROM Card')
  name = [] # crating a list to store the card holder name and company name and shown in selectbox to user select a option to delete
  for i in cursor:
    value = i[0],i[1]
    Join = ' & '.join(value) # two values joining by '&' to append the data
    name.append(Join)
  option = st.selectbox(label = "",options = name,index = None,placeholder='Select any Card')
  try:
    name = option.split(' &')[0] # here splitting the data by '&' and getting the first value by slicing the data
    com_name = option.split(' & ')[1] # here splitting the data by '&' and getting the second value by slicing the data
    st.info(f'you selected card is **{name}** and their company  name is **{com_name}**  for more details see below table. Make sure to delete this card, because there is no backup.')
    qry = f"SELECT * FROM Card WHERE Card_Holder = '{name}'"
    df = pd.read_sql_query(qry,db)
    st.dataframe(df)
    button = st.button('Delete this Card') # creating the button to delete the data in SQL
    if button:
      delete_query = f"DELETE FROM Card WHERE Card_Holder = '{name}'"
      cursor.execute(delete_query)
      db.commit()
      st.success('Successfully Deleted✅')
      st.markdown('')
      st.subheader(':violet[👇🏻Here is your Updated Data👇🏻]')
      db = sqlite3.connect('/content/Bizcardx.db')
      qury = "SELECT * FROM Card"
      df1 = pd.read_sql_query(qury, db)
      if df1.empty:
        st.markdown("#### &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; No data available in DataBase")
      else:
        st.dataframe(df1)
        cursor.close()
        db.close()
  except:
    pass

# this code is use for removing the "made with streamlit" in bottom of the app and also it removes the menu option
hide = """
    <style>
    footer {visibility: hidden;}
    #header {visibility: hidden;}
    </style>
    """
st.markdown(hide,unsafe_allow_html = True)


