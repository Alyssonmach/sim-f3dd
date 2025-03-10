import streamlit as st
from main_page import page1
from experimental_page import page2

st.set_page_config(page_title = 'Simulador Vibra-torre', page_icon = '⚡')

pg = st.navigation([
    st.Page(page1, title = 'Simulador Vibra-Torre', icon = '🚀'),
    st.Page(page2, title = 'Testes Experimentais', icon = '🧪')
])

pg.run()