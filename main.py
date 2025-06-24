import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Painel de Vendas Mercado Livre", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main {
        background-color: #15181b;
    }
    .stApp {
        background-color: #15181b;
        color: #fff;
    }
    .st-bd, .st-cd, .st-ce {
        background-color: #222 !important;
        color: #fff !important;
        border-radius: 12px;
        padding: 10px 16px;
        font-size: 19px !important;
    }
    .stDataFrame thead tr {
        background-color: #222 !important;
    }
    .stDataFrame {
        background-color: #1a1d20 !important;
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#fff;'>Painel de Vendas Mercado Livre</h1>", unsafe_allow_html=True)
st.markdown(f"""<a style='color:#3ABFEF;font-size:18px;' href="https://auth.mercadolivre.com.br/authorization?response_type=code&client_id=1084489159343219&redirect_uri=https://www.google.com/">Clique aqui para conectar com o Mercado Livre</a>""", unsafe_allow_html=True)

codigo = st.text_input("Cole aqui o código de autorização que apareceu na URL após o login:")
access_token = None

if codigo:
    url_token = "https://api.mercadolibre.com/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": "1084489159343219",
        "client_secret": "6S0WD8QztvDOcDvjrrWIOogLMMWGXbJg",
        "code": codigo,
        "redirect_uri": "https://www.google.com/"
    }
    headers = {"accept": "application/json", "content-type": "application/x-www-form-urlencoded"}
    try:
        response = requests.post(url_token, data=payload, headers=headers)
        token_data = response.json()
        if "access_token" in token_data:
            access_token = token_data["access_token"]
            st.success("Token de acesso gerado com sucesso!")
        else:
            st.error("Erro ao trocar o código pelo token de acesso.")
    except Exception as e:
        st.error(f"Erro: {str(e)}")

if access_token:
    # Buscar vendas (puxa várias páginas!)
    vendas = []
    offset = 0
    while True:
        url = f"https://api.mercadolibre.com/orders/search?seller=1773673043&access_token={access_token}&offset={offset}&limit=50"
        res = requests.get(url).json()
        if "results" in res:
            vendas += res["results"]
            if len(res["results"]) < 50:
                break
            offset += 50
        else:
            break

    if len(vendas) == 0:
        st.warning("Nenhuma venda encontrada.")
    else:
        # Normaliza e prepara os dados
        df = pd.DataFrame([{
            "Data": pd.to_datetime(order["date_created"]).date(),
            "ID Venda": order["id"],
            "Status": order["status"],
            "Comprador": order["buyer"]["nickname"] if order.get("buyer") else "",
            "Valor Total": float(order["total_amount"]),
            "Status Pagamento": order.get("payments", [{}])[0].get("status", ""),
            "Item": order["order_items"][0]["item"]["title"] if order.get("order_items") else "",
        } for order in vendas])

        df["Data"] = pd.to_datetime(df["Data"])
        df["Ano-Mês"] = df["Data"].dt.strftime('%Y-%m')

        # FILTRO DE MÊS (sempre funciona)
        meses = ["Todos"] + sorted(df["Ano-Mês"].unique().tolist())
        mes_sel = st.selectbox("Filtrar por mês:", meses)
        if mes_sel != "Todos":
            df_mes = df[df["Ano-Mês"] == mes_sel]
        else:
            df_mes = df.copy()

        # CARDS PRINCIPAIS
        col1, col2, col3, col4 = st.columns(4)
        vendas_totais = len(df_mes)
        receita_total = df_mes["Valor Total"].sum()
        ticket_medio = df_mes["Valor Total"].mean() if vendas_totais > 0 else 0

        # Ticket médio últimos 3 meses
        ultimos3 = df[df["Ano-Mês"].isin(sorted(df["Ano-Mês"].unique())[-3:])]
        ticket_3m = ultimos3["Valor Total"].mean() if len(ultimos3) else 0

        # Crescimento do mês (vs mês anterior)
        meses_sorted = sorted(df["Ano-Mês"].unique())
        if mes_sel == "Todos":
            mes_atual = meses_sorted[-1]
            mes_ant = meses_sorted[-2] if len(meses_sorted) > 1 else meses_sorted[-1]
        else:
            mes_atual = mes_sel
            idx = meses_sorted.index(mes_sel)
            mes_ant = meses_sorted[idx-1] if idx > 0 else meses_sorted[0]
        vendas_atual = df[df["Ano-Mês"] == mes_atual]["Valor Total"].sum()
        vendas_ant = df[df["Ano-Mês"] == mes_ant]["Valor Total"].sum()
        crescimento = ((vendas_atual - vendas_ant) / vendas_ant * 100) if vendas_ant > 0 else 0

        with col1:
            st.metric("Vendas totais", vendas_totais)
        with col2:
            st.metric("Receita Total", f"R$ {receita_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with col3:
            st.metric("Ticket Médio 3 meses", f"R$ {ticket_3m:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        with col4:
            st.metric("Crescimento do mês", f"{crescimento:.2f} %", delta=f"{crescimento:.1f}%" if crescimento > 0 else f"{crescimento:.1f}%", delta_color="normal")

        # GRÁFICO DE LINHAS: Receita mensal
        receita_mes = df.groupby("Ano-Mês")["Valor Total"].sum().reset_index()
        fig_linha = px.line(
            receita_mes,
            x="Ano-Mês",
            y="Valor Total",
            title="Receita por mês (todas as vendas)",
            markers=True,
            text="Valor Total",
        )
        fig_linha.update_traces(line_color="#36d399", marker_color="#36d399", texttemplate="R$ %{y:,.0f}", textposition="top center")
        fig_linha.update_layout(
            plot_bgcolor='#222',
            paper_bgcolor='#222',
            font_color="#fff",
            xaxis=dict(showgrid=False, color="#fff"),
            yaxis=dict(showgrid=True, gridcolor="#444", color="#fff"),
        )
        st.plotly_chart(fig_linha, use_container_width=True)

        # GRÁFICO DE ROSCA: Status Pagamento
        status_count = df_mes["Status Pagamento"].replace({"approved": "Pago", "cancelled": "Cancelado"}).value_counts().reset_index()
        status_count.columns = ["Status", "Contagem"]
        fig_pie = px.pie(
            status_count,
            values="Contagem",
            names="Status",
            title="Status dos Pagamentos",
            hole=0.55,
            color_discrete_sequence=["#36d399", "#f87171"]
        )
        fig_pie.update_traces(
            textinfo="percent+label",
            marker=dict(line=dict(color="#222", width=2)),
            pull=[0.03, 0.03],
        )
        fig_pie.update_layout(
            height=290,
            margin=dict(t=40, b=10, l=0, r=0),
            paper_bgcolor="#222",
            plot_bgcolor="#222",
            font_color="#fff",
            showlegend=True,
        )
        st.plotly_chart(fig_pie, use_container_width=False)

        # TOP 5 PRODUTOS MAIS VENDIDOS
        st.subheader("Top 5 produtos mais vendidos")
        top5 = df_mes["Item"].value_counts().head(5)
        fig_top5 = px.bar(
            top5,
            x=top5.index,
            y=top5.values,
            text=top5.values,
            labels={"x": "Produto", "y": "Qtd. Vendas"},
            title="Top 5 Produtos"
        )
        fig_top5.update_traces(marker_color="#3ABFEF", textposition="outside")
        fig_top5.update_layout(
            plot_bgcolor="#222",
            paper_bgcolor="#222",
            font_color="#fff",
            xaxis=dict(color="#fff"),
            yaxis=dict(color="#fff"),
            margin=dict(t=40, b=40, l=20, r=20),
        )
        st.dataframe(fig_top5, use_container_width=True)

        # TABELA DE VENDAS
        st.subheader("Minhas vendas mais recentes:")
        st.dataframe(df_mes[["Data", "ID Venda", "Status", "Comprador", "Valor Total", "Status Pagamento", "Item"]].sort_values("Data", ascending=False), use_container_width=True)

else:
    st.info("Cole o código de autorização para acesso às suas vendas.")

