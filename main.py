import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide", page_title="Painel Mercado Livre", initial_sidebar_state="collapsed")

# ====================
# ESTILO GLOBAL DARK
# ====================
st.markdown("""
    <style>
    body, .stApp {
        background-color: #17191c !important;
        color: #fff !important;
    }
    .st-cg, .st-cg .st-cp {
        color: #fff !important;
    }
    .st-dp, .st-dr, .st-dd, .st-dk, .st-fn, .st-bo, .st-ag {
        background-color: #222 !important;
        color: #fff !important;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div>div {
        background-color: #222 !important;
        color: #fff !important;
    }
    th, td {
        background-color: #232323 !important;
        color: #fff !important;
    }
    .st-bx {
        color: #fff !important;
    }
    .css-1wivap2, .st-bx, .st-bv, .st-cz {
        color: #fff !important;
    }
    .st-bw {
        background-color: #242424 !important;
        color: #fff !important;
    }
    .stDataFrame th, .stDataFrame td {
        background-color: #232323 !important;
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ====================
# FUNÇÕES EXEMPLO: SUBSTITUA PELO SEU LOAD
# ====================
@st.cache_data
def carregar_dados():
    # Aqui você coloca o seu código para buscar dados do Mercado Livre
    # --- EXEMPLO FAKE DATA ---
    dados = {
        "Data": pd.date_range("2025-01-01", periods=100, freq="15D"),
        "ID Venda": [f"00{x:04d}" for x in range(100)],
        "Status": ["paid"] * 80 + ["cancelled"] * 10 + ["refunded"] * 10,
        "Comprador": ["cliente_"+str(x%20) for x in range(100)],
        "Valor Total": [round(100+1000*(x%4)+x,2) for x in range(100)],
        "Status Pagamento": ["approved"] * 100,
        "Item": [f"Produto {chr(65+(x%5))}" for x in range(100)]
    }
    df = pd.DataFrame(dados)
    return df

df = carregar_dados()

# ===========================
# FILTRO POR MÊS
# ===========================
df["AnoMes"] = df["Data"].dt.strftime('%Y-%m')
meses = sorted(df["AnoMes"].unique())
mes_selecionado = st.selectbox(
    "Filtrar por mês:",
    options=["Todos"] + meses,
    index=0,
    key="filtro_mes"
)
if mes_selecionado != "Todos":
    df_mes = df[df["AnoMes"] == mes_selecionado].copy()
else:
    df_mes = df.copy()

# ===========================
# CARDS
# ===========================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div style="background-color:#242424;padding:24px;border-radius:16px;box-shadow:0 2px 8px #0003;">
        <div style="font-size:16px;">Vendas totais</div>
        <div style="font-size:38px;font-weight:bold;">{}</div>
        </div>
    """.format(len(df)), unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style="background-color:#242424;padding:24px;border-radius:16px;box-shadow:0 2px 8px #0003;">
        <div style="font-size:16px;">Receita Total</div>
        <div style="font-size:38px;font-weight:bold;">R$ {:,.2f}</div>
        </div>
    """.format(df["Valor Total"].sum()), unsafe_allow_html=True)

with col3:
    tm3 = df.tail(90)["Valor Total"].mean() if not df.tail(90).empty else 0
    st.markdown("""
        <div style="background-color:#242424;padding:24px;border-radius:16px;box-shadow:0 2px 8px #0003;">
        <div style="font-size:16px;">Ticket Médio 3 meses</div>
        <div style="font-size:38px;font-weight:bold;">R$ {:,.2f}</div>
        </div>
    """.format(tm3), unsafe_allow_html=True)

with col4:
    if len(meses) > 1:
        rec_atual = df[df["AnoMes"] == meses[-1]]["Valor Total"].sum()
        rec_ant = df[df["AnoMes"] == meses[-2]]["Valor Total"].sum()
        perc = 0 if rec_ant == 0 else 100*(rec_atual - rec_ant)/rec_ant
    else:
        perc = 0
    color = "#4cf554" if perc >= 0 else "#ff4c4c"
    seta = "↑" if perc >= 0 else "↓"
    st.markdown("""
        <div style="background-color:#242424;padding:24px;border-radius:16px;box-shadow:0 2px 8px #0003;">
        <div style="font-size:16px;">Crescimento do mês</div>
        <div style="font-size:38px;font-weight:bold;color:{};">{:.2f}% <span style="font-size:18px">{}</span></div>
        </div>
    """.format(color, perc, seta), unsafe_allow_html=True)

# ===========================
# GRÁFICO LINHA (RECEITA MENSAL)
# ===========================
st.markdown("### Receita por mês (todas as vendas)")

df_graf = df_mes.groupby("AnoMes")["Valor Total"].sum().reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_graf["AnoMes"], y=df_graf["Valor Total"],
    mode="lines+markers+text",
    text=["R$ {:,.0f}".format(v) for v in df_graf["Valor Total"]],
    textposition="top center",
    line=dict(color="#21e5b6", width=3),
    marker=dict(size=8, color="#21e5b6"),
    name="Receita"
))
fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="#232323",
    paper_bgcolor="#232323",
    font_color="#fff",
    margin=dict(t=40, l=20, r=20, b=40),
    xaxis_title="Mês",
    yaxis_title="Valor Total",
)
st.plotly_chart(fig, use_container_width=True)

# ===========================
# GRÁFICO ROSCA STATUS PAGAMENTO
# ===========================
st.markdown("<span style='color:#fff;font-size:22px;'>Status dos Pagamentos</span>", unsafe_allow_html=True)
st.write("")
status = df_mes["Status"].value_counts()
fig2 = go.Figure(data=[go.Pie(
    labels=status.index,
    values=status.values,
    hole=.6,
    marker_colors=["#27db98", "#ff7676", "#00b3ff", "#999"],
    textinfo="label+percent"
)])
fig2.update_layout(
    showlegend=True,
    plot_bgcolor="#232323",
    paper_bgcolor="#232323",
    font_color="#fff",
    margin=dict(t=20, l=0, r=0, b=0)
)
st.plotly_chart(fig2, use_container_width=True)

# ===========================
# TOP 5 PRODUTOS MAIS VENDIDOS (TABELA)
# ===========================
st.markdown("### Top 5 produtos mais vendidos")
top5 = df_mes["Item"].value_counts().head(5).reset_index()
top5.columns = ["Produto", "Qtd. Vendas"]
st.dataframe(top5, hide_index=True, use_container_width=True)

# ===========================
# TABELA VENDAS RECENTES
# ===========================
st.markdown("### Minhas vendas mais recentes:")
st.dataframe(
    df_mes[["Data", "ID Venda", "Status", "Comprador", "Valor Total", "Status Pagamento", "Item"]].sort_values("Data", ascending=False).head(10),
    use_container_width=True
)
