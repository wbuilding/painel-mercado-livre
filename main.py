import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Painel de Vendas Mercado Livre", layout="wide", initial_sidebar_state="collapsed")

# Estilo customizado para texto claro nos cards/títulos/tabelas
st.markdown("""
    <style>
        .main {
            background-color: #181b1e;
        }
        div[data-testid="stMetric"] > label {
            color: #fff !important;
        }
        .css-1offfwp {
            color: #fff !important;
        }
        .stTextInput>div>div>input {
            color: #fff !important;
            background-color: #222 !important;
        }
        .stSelectbox>div>div>div>div {
            color: #fff !important;
            background-color: #222 !important;
        }
        th, td {
            color: #fff !important;
            background-color: #23262b !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Painel de Vendas Mercado Livre")

# Simulação de dados
# No seu código, troque por dados reais via API!
dados = {
    "Data": pd.date_range("2024-01-01", periods=12, freq="M"),
    "ID Venda": np.arange(1000, 1012),
    "Status": ["Pago", "Pago", "Cancelado", "Pago", "Pago", "Pago", "Pago", "Pago", "Cancelado", "Pago", "Pago", "Pago"],
    "Comprador": ["Cliente A", "Cliente B", "Cliente C", "Cliente D", "Cliente E", "Cliente F", "Cliente G", "Cliente H", "Cliente I", "Cliente J", "Cliente K", "Cliente L"],
    "Valor Total": np.random.randint(100, 1000, 12),
    "Status Pagamento": ["Aprovado", "Aprovado", "Cancelado", "Aprovado", "Aprovado", "Aprovado", "Aprovado", "Aprovado", "Cancelado", "Aprovado", "Aprovado", "Aprovado"],
    "Item": ["Produto A", "Produto B", "Produto C", "Produto B", "Produto D", "Produto A", "Produto C", "Produto B", "Produto D", "Produto B", "Produto C", "Produto A"],
}
df = pd.DataFrame(dados)

# Filtro por mês
df["Mês"] = df["Data"].dt.strftime('%Y-%m')
meses = df["Mês"].unique().tolist()
mes_selecionado = st.selectbox("Filtrar por mês:", ["Todos"] + meses, key="mes_filtro")
if mes_selecionado != "Todos":
    df = df[df["Mês"] == mes_selecionado]

# Cards com informações principais (claro)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Vendas totais", f"{df.shape[0]}")
with col2:
    st.metric("Receita Total", f"R$ {df['Valor Total'].sum():,.2f}")
with col3:
    st.metric("Ticket Médio 3 meses", f"R$ {df['Valor Total'].mean():,.2f}")
with col4:
    st.metric("Crescimento do mês", "-93.09%")

st.markdown("---")

# Gráfico de linhas Receita por mês (valor)
df_linhas = df.groupby("Mês")["Valor Total"].sum().reset_index()
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_linhas["Mês"],
    y=df_linhas["Valor Total"],
    mode="lines+markers+text",
    text=[f"R$ {v:,.0f}" for v in df_linhas["Valor Total"]],
    textposition="top center",
    line=dict(color="#27e1c1")
))
fig.update_layout(
    title=dict(text="Receita por mês (todas as vendas)", font=dict(color="#fff")),
    xaxis=dict(title="", color="#fff", gridcolor="#444"),
    yaxis=dict(title="Valor Total", color="#fff", gridcolor="#444"),
    plot_bgcolor="#222",
    paper_bgcolor="#222"
)
st.plotly_chart(fig, use_container_width=True)

# Donut status pagamento
status_counts = df["Status"].value_counts()
fig2 = go.Figure(data=[go.Pie(labels=status_counts.index, values=status_counts.values, hole=0.6)])
fig2.update_traces(textinfo="percent+label", marker=dict(colors=["#27e1c1", "#e14b4b"]))
fig2.update_layout(
    title=dict(text="Status dos Pagamentos", font=dict(color="#fff")),
    legend=dict(font=dict(color="#fff")),
    plot_bgcolor="#222",
    paper_bgcolor="#222"
)
st.plotly_chart(fig2, use_container_width=True)

# Tabela: Top 5 produtos mais vendidos
st.subheader("Top 5 produtos mais vendidos")
top5 = df["Item"].value_counts().head(5).reset_index()
top5.columns = ["Produto", "Quantidade vendida"]
st.dataframe(top5, use_container_width=True, hide_index=True)

# Tabela de vendas
st.subheader("Minhas vendas mais recentes:")
st.dataframe(df[["Data", "ID Venda", "Status", "Comprador", "Valor Total", "Status Pagamento", "Item"]], use_container_width=True)

