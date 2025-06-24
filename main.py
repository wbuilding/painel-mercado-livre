import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# TEMA CLARO PARA OS GRÁFICOS E TABELAS
st.set_page_config(page_title="Painel de Vendas Mercado Livre", layout="wide")

# TÍTULO
st.title("Painel de Vendas Mercado Livre")

# SIMULAÇÃO DE DADOS (troque pelo seu dataframe)
# Remova esta simulação no seu código, e use seu df_mes
# ===================
dados = {
    "Data": pd.date_range("2024-01-01", periods=12, freq="M"),
    "ID Venda": [1001 + i for i in range(12)],
    "Status": ["Pago", "Pago", "Cancelado", "Pago", "Pago", "Pago", "Pago", "Cancelado", "Pago", "Pago", "Pago", "Pago"],
    "Comprador": [f"Cliente {chr(65+i)}" for i in range(12)],
    "Valor Total": np.random.randint(200, 1200, 12),
    "Status Pagamento": ["Aprovado", "Aprovado", "Cancelado", "Aprovado", "Aprovado", "Aprovado", "Aprovado", "Cancelado", "Aprovado", "Aprovado", "Aprovado", "Aprovado"],
    "Item": ["Produto A", "Produto B", "Produto C", "Produto D", "Produto B", "Produto A", "Produto C", "Produto D", "Produto C", "Produto B", "Produto A", "Produto D"],
}
df_mes = pd.DataFrame(dados)
df_mes["Data"] = pd.to_datetime(df_mes["Data"])
df_mes["Mês/Ano"] = df_mes["Data"].dt.strftime("%m/%Y")
# ===================

# FILTRO POR MÊS
meses = ["Todos"] + sorted(df_mes["Mês/Ano"].unique())
filtro_mes = st.selectbox("Filtrar por mês:", meses)
if filtro_mes != "Todos":
    df_mes_filtrado = df_mes[df_mes["Mês/Ano"] == filtro_mes]
else:
    df_mes_filtrado = df_mes.copy()

# CARDS: NOME + VALOR
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("**Vendas totais**")
    st.markdown(f"<h2 style='color:#222'>{df_mes_filtrado.shape[0]}</h2>", unsafe_allow_html=True)
with col2:
    st.markdown("**Receita total**")
    st.markdown(f"<h2 style='color:#222'>R$ {df_mes_filtrado['Valor Total'].sum():,.2f}</h2>", unsafe_allow_html=True)
with col3:
    st.markdown("**Ticket Médio 3 meses**")
    ticket_medio = df_mes_filtrado["Valor Total"].mean() if not df_mes_filtrado.empty else 0
    st.markdown(f"<h2 style='color:#222'>R$ {ticket_medio:,.2f}</h2>", unsafe_allow_html=True)
with col4:
    st.markdown("**Crescimento do mês**")
    # Exemplo fictício, troque por sua lógica real
    crescimento = -93.09
    cor = "#222"
    st.markdown(f"<h2 style='color:{cor}'>{crescimento:.2f}%</h2>", unsafe_allow_html=True)

# GRÁFICO DE LINHAS (RECEITA POR MÊS)
st.markdown("### Receita por mês (todas as vendas)")
receita_mes = (
    df_mes.groupby("Mês/Ano")["Valor Total"].sum().reset_index().sort_values("Mês/Ano")
)
fig_receita = px.line(receita_mes, x="Mês/Ano", y="Valor Total", markers=True, text="Valor Total")
fig_receita.update_traces(texttemplate="R$ %{y:,.0f}", textposition="top center")
fig_receita.update_layout(
    xaxis_title="Mês/Ano",
    yaxis_title="Valor Total",
    plot_bgcolor="#181b1f",
    paper_bgcolor="#181b1f",
    font_color="#222",
)
st.plotly_chart(fig_receita, use_container_width=True)

# GRÁFICO DE ROSCA - STATUS DOS PAGAMENTOS
st.markdown("### Status dos Pagamentos")
status_pagamentos = df_mes_filtrado["Status Pagamento"].value_counts().reset_index()
status_pagamentos.columns = ["Status Pagamento", "Quantidade"]
fig_status = px.pie(status_pagamentos, values="Quantidade", names="Status Pagamento", hole=0.6)
fig_status.update_traces(textinfo="percent+label")
fig_status.update_layout(
    showlegend=True,
    plot_bgcolor="#181b1f",
    paper_bgcolor="#181b1f",
    font_color="#222"
)
st.plotly_chart(fig_status, use_container_width=True)

# TOP 5 PRODUTOS MAIS VENDIDOS - TABELA
st.markdown("### Top 5 produtos mais vendidos")
top5_produtos = df_mes_filtrado["Item"].value_counts().head(5).reset_index()
top5_produtos.columns = ["Produto", "Quantidade vendida"]
st.dataframe(top5_produtos, hide_index=True)

# TABELA DE VENDAS (COMPLETA)
st.markdown("### Minhas vendas mais recentes:")
st.dataframe(
    df_mes_filtrado[
        ["Data", "ID Venda", "Status", "Comprador", "Valor Total", "Status Pagamento", "Item"]
    ],
    use_container_width=True
)
