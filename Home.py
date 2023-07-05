import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🍕'
)

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Namasfood')
st.sidebar.markdown('## An Indian food delivery company')
st.sidebar.markdown("""---""")

st.write('# Namasfood - Company Dashboard')
    
st.header('Namasfood')
