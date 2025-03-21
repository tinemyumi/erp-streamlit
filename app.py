import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from faker import Faker

# Interface Streamlit
def main():
    st.title("ERP Financeiro com Streamlit")
    
    menu = ["Clientes", "Contas a Pagar", "Contas a Receber", "Lançamentos", "Relatórios", "Comparação Receita vs Despesa", "Fluxo de Caixa por Mês"]
    choice = st.sidebar.selectbox("Selecione uma opção", menu)
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    
    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df)
        
    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df)
        
    elif choice == "Relatórios":
        st.subheader("Relatório de Fluxo de Caixa")
        df = pd.read_sql_query("SELECT tipo, SUM(valor) as total FROM lancamentos GROUP BY tipo", conn)
        st.dataframe(df)

        st.subheader("Status das Contas a Pagar e Receber")
        df_pagar = pd.read_sql_query("SELECT status, SUM(valor) as total FROM contas_pagar GROUP BY status", conn)
        df_receber = pd.read_sql_query("SELECT status, SUM(valor) as total FROM contas_receber GROUP BY status", conn)
        
        df_pagar["tipo"] = "Contas a Pagar"
        df_receber["tipo"] = "Contas a Receber"
        
        df_status = pd.concat([df_pagar, df_receber])
        fig = px.bar(df_status, x="status", y="total", color="tipo", barmode="group", title="Total de Contas Pendentes vs Pagas/Recebidas")
        st.plotly_chart(fig)
    
    elif choice == "Comparação Receita vs Despesa":
        st.subheader("Comparação Receita vs Despesa (Mês Atual)")
        
        df_comparacao = pd.read_sql_query(''' 
            SELECT tipo, SUM(valor) as total
            FROM lancamentos
            WHERE strftime('%Y-%m', data) = strftime('%Y-%m', 'now') 
            GROUP BY tipo
        ''', conn)
        
        st.dataframe(df_comparacao)
        
        fig = px.bar(df_comparacao, x="tipo", y="total", title="Comparação Receita vs Despesa (Mês Atual)", color="tipo")
        st.plotly_chart(fig)
    
    elif choice == "Fluxo de Caixa por Mês":
        st.subheader("Fluxo de Caixa por Mês")
        
        df_fluxo = pd.read_sql_query('''
            SELECT strftime('%Y-%m', data) as mes, tipo, SUM(valor) as total
            FROM lancamentos
            GROUP BY mes, tipo
            ORDER BY mes
        ''', conn)

        st.dataframe(df_fluxo)

        if not df_fluxo.empty:
            tipo_grafico = st.radio("Escolha o tipo de gráfico:", ["Linha", "Barras"])
            
            if tipo_grafico == "Linha":
                fig = px.line(df_fluxo, x="mes", y="total", color="tipo", markers=True, title="Fluxo de Caixa por Mês")
            else:
                fig = px.bar(df_fluxo, x="mes", y="total", color="tipo", barmode="group", title="Fluxo de Caixa por Mês")
            
            st.plotly_chart(fig)
    
    conn.close()
    
if __name__ == "__main__":
    main()
