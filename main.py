import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Título do painel
st.title("Painel de Vendas Mercado Livre")

# Campo para token (coloque aqui o campo igual antes!)
code = st.text_input(
    "Cole aqui o código de autorização que apareceu na URL após o login:"
)

# Simulação dos dados (troque pelo seu dataframe!)
# df = pd.read_csv('sua_base.csv')  # Exemplo

# --- Exemplo de DataFrame para ilustrar (substitua pelo seu) ---
df = pd.DataFrame({
    "Data": [
        "2024-03-31", "2024-04-30", "2024-05-31", "2024-06-30",
        "2024-07-31", "2024-08-31", "2024-09-30", "2024-10-31"
    ],
    "ID Venda": [1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009],
    "Status": ["Cancelado", "Pago", "Pago", "Pago", "Pago", "Pago", "Cancelado", "Pago"],
    "Comprador": ["Cliente C", "Cliente D", "Cliente E", "Cliente F", "Cliente G", "Cliente H", "Cliente I", "Cliente J"],
    "Valor Total": [424, 273, 608, 850, 901, 124, 265, 596],
    "Status Pagamento": ["Cancelado", "Aprovado", "Aprovado", "Aprovado", "Aprovado", "Aprovado", "Cancelado", "Aprovado"],
    "Item": ["Produto C", "Produto B", "Produto D", "Produto A", "Produto C", "Produto B", "Produto D", "Produto B"],
})

# Filtro de mês
df["Data"] = pd.to_datetime(df["Data"])
df["Mês/Ano"] = df["Data"].dt.strftime("%m/%Y")
meses = ["Todos"] + list(df["Mês/Ano"].unique())
mes_selecionado = st.selectbox("Filtrar por mês:", meses)

if mes_selecionado != "Todos":
    df_mes = df[df["Mês/Ano"] == mes_selecionado]
else:
    df_mes = df.copy()

# --- Cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Vendas totais", f"{df_mes.shape[0]}")
col2.metric("Receita total", f"R$ {df_mes['Valor Total'].sum():,.2f}")
col3.metric("Ticket Médio 3 meses", f"R$ {df_mes['Valor Total'].mean():,.2f}")
# Exemplo de crescimento do mês (você pode trocar pela sua lógica)
col4.metric("Crescimento do mês", "-93.09%")

# --- Gráfico de linha ---
st.subheader("Receita por mês (todas as vendas)")
receita_mes = df.groupby(df["Data"].dt.strftime("%m/%Y"))["Valor Total"].sum().reset_index()
fig = px.line(receita_mes, x="Data", y="Valor Total", markers=True, text="Valor Total")
fig.update_traces(line_color='#3182CE', textposition="top center")
fig.update_layout(
    plot_bgcolor='#181a1b', paper_bgcolor='#181a1b',
    font_color='#222', title_font_color='#222',
)
st.plotly_chart(fig, use_container_width=True)

# --- Top 5 produtos mais vendidos (em tabela) ---
st.subheader("Top 5 produtos mais vendidos")
top5 = df_mes["Item"].value_counts().head(5).reset_index()
top5.columns = ["Produto", "Quantidade vendida"]
st.dataframe(top5, use_container_width=True)

# --- Tabela de vendas ---
st.subheader("Minhas vendas mais recentes:")
st.dataframe(
    df_mes[["Data", "ID Venda", "Status", "Comprador", "Valor Total", "Status Pagamento", "Item"]],
    use_container_width=True,
)

