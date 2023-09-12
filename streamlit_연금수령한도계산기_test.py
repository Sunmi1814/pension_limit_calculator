#!/usr/bin/env python
# coding: utf-8

# In[2]:


import streamlit as st


# In[38]:


st.set_page_config(layout="wide")


# # 

# In[3]:


st.title("연금 수령 한도 계산기")


# ## 사이드바 화면

# In[4]:


st.sidebar.title("연금 수령 한도 계산기")


# In[5]:


st.subheader("연금계좌 Cash Flow")


# In[43]:


import pandas as pd
import numpy as np
import streamlit as st
from babel.numbers import format_percent

# Define Streamlit inputs
연금계좌평가액 = st.sidebar.number_input("연금계좌평가액 (원)", step=1, format="%d")
연간인출금액 = st.sidebar.number_input("연간인출금액 (원)", step=1, format="%d")
연평균수익률 = st.sidebar.number_input("연평균수익률 (%)", step=0.01, format="%.2f") / 100
이전가입여부_option = ["2013년 3월 이전 가입", "2013년 3월 이후 가입"]
이전가입여부 = st.sidebar.selectbox("2013년 3월 이전 가입 여부", 이전가입여부_option)
나이_option = ["만55세 이상", "만55세 미만"]
나이 = st.sidebar.selectbox("만55세 이상 여부", 나이_option)
퇴직소득세율 = st.sidebar.number_input("퇴직소득세율 (%)", step=0.01, format="%.2f") 

# 첫 번째 데이터프레임 생성
df = pd.DataFrame(np.nan, index=range(30), columns=['수령연차', '연초 계좌평가액', '인출 후 계좌 잔액', '연말 계좌평가액'])

# '수령연차' 값 설정
df['수령연차'] = range(1, 31)

# '수령연차'를 정수형으로 변환
df['수령연차'] = df['수령연차'].astype(int)

# 각 연도별 계좌 평가액 및 인출 계산
for i in range(30):
    if i == 0:
        df.loc[i, '연초 계좌평가액'] = 연금계좌평가액
    else:
        df.loc[i, '연초 계좌평가액'] = df.loc[i-1, '연말 계좌평가액']
    
    df.loc[i, '인출 후 계좌 잔액'] = df.loc[i, '연초 계좌평가액'] - 연간인출금액
    df.loc[i, '연말 계좌평가액'] = df.loc[i, '인출 후 계좌 잔액'] * (1 + 연평균수익률)

# 두 번째 데이터프레임 생성
df1 = pd.DataFrame(np.nan, index=range(30), columns=['연금 수령연차', '연금 계좌 평가액', '연간 연금수령한도', '퇴직소득세 감면 연차', '퇴직소득세율'])

# '연금 계좌 평가액' 초기값 설정
df1['연금 계좌 평가액'] = df['연초 계좌평가액']

# '연금 수령연차' 초기값 설정
if 이전가입여부 == "2013년 3월 이전 가입" and 나이 == "만55세 이상":
    df1.loc[0, '연금 수령연차'] = 6
elif 이전가입여부 == "2013년 3월 이후 가입" and 나이 == "만55세 이상":
    df1.loc[0, '연금 수령연차'] = 1
else:
    df1.loc[0, '연금 수령연차'] = np.nan

# '퇴직소득세율' 값을 형식화하기 위한 함수 정의
def format_percentage(value):
    if pd.notna(value):
        return format_percent(value, format='#.##%', locale='ko_KR')
    else:
        return ''

# '연금 수령연차' 및 '퇴직소득세율' 계산
for i in range(30):
    if i == 0:
        if df1.loc[i, '연금 수령연차'] < 11:
            df1.loc[i, '연간 연금수령한도'] = df1.loc[i, '연금 계좌 평가액'] / (11 - df1.loc[i, '연금 수령연차']) * 1.2
        df1.loc[i, '퇴직소득세 감면 연차'] = df.loc[i, '수령연차']
        if df1.loc[i, '퇴직소득세 감면 연차'] >= 11:
            df1.loc[i, '퇴직소득세율'] = 0.6 * 퇴직소득세율 / 100
        else:
            df1.loc[i, '퇴직소득세율'] = 0.7 * 퇴직소득세율 / 100
    else:
        df1.loc[i, '연금 수령연차'] = df1.loc[i-1, '연금 수령연차'] + 1
    
        if df1.loc[i, '연금 수령연차'] < 11:
            df1.loc[i, '연간 연금수령한도'] = df1.loc[i, '연금 계좌 평가액'] / (11 - df1.loc[i, '연금 수령연차']) * 1.2
        df1.loc[i, '퇴직소득세 감면 연차'] = df.loc[i, '수령연차']
        if df1.loc[i, '퇴직소득세 감면 연차'] >= 11:
            df1.loc[i, '퇴직소득세율'] = 0.6 * 퇴직소득세율 / 100
        else:
            df1.loc[i, '퇴직소득세율'] = 0.7 * 퇴직소득세율 / 100

# '퇴직소득세율' 값을 포맷하여 표시
df1['퇴직소득세율'] = df1['퇴직소득세율'].apply(format_percentage)

# '연말 계좌평가액' 컬럼 포맷 조정
pd.options.display.float_format = '{:,.0f}'.format

# 스트림릿 표시 포맷 조정
st.markdown("""
<style>
table {
    width: 100%;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# 스트림릿 화면을 두 개의 열로 나누어 표시
col1, col2 = st.columns(2)

# 데이터프레임을 HTML 문자열로 변환 (인덱스는 표시하지 않음)
df_html = df.to_html(index=False)
df1_html = df1.to_html(index=False)

# 스트림릿에 HTML 테이블 표시
with col1:
    st.markdown("### 연금 수령 계좌 현황")
    st.markdown(df_html, unsafe_allow_html=True)

with col2:
    st.markdown("### 연금 수령연차 및 세금 관련 정보")
    st.markdown(df1_html, unsafe_allow_html=True)


# In[ ]:




