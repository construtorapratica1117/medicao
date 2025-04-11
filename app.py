
import streamlit as st
st.set_page_config('Sistema de Medição', layout='wide')
import pandas as pd
import os
from datetime import datetime
import glob
import io
from fpdf import FPDF

CAMINHO_USUARIOS = "base_de_dados/usuarios.csv"
SENHA = "240992"

if not os.path.exists(CAMINHO_USUARIOS):
    df_usuarios = pd.DataFrame([{
        "Usuario": "Yuri",
        "Senha": SENHA,
        "Cadastro": True,
        "Medicao": True,
        "Relatorio": True,
        "Historico": True,
        "Exportacoes": True,
        "Admin": True
    }])
    df_usuarios.to_csv(CAMINHO_USUARIOS, index=False)


if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["usuario"] = None
    st.session_state["permissoes"] = {}

if not st.session_state["logado"]:
    st.title("🔐 Login - Sistema de Medição")
    with st.form("login_form"):
        usuario_input = st.text_input("Usuário", max_chars=20)
        senha_input = st.text_input("Senha", type="password", max_chars=20)
        submitted = st.form_submit_button("Entrar")

    if submitted:
        df_usuarios = pd.read_csv(CAMINHO_USUARIOS)
        usuario_input = usuario_input.strip().lower()
        usuario_encontrado = None
        for _, row in df_usuarios.iterrows():
            if row["Usuario"].strip().lower() == usuario_input and str(row["Senha"]).strip() == senha_input:
                usuario_encontrado = row
                break
        if usuario_encontrado is not None:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario_encontrado["Usuario"]
            st.session_state["permissoes"] = dict(usuario_encontrado)
            st.success("Login realizado com sucesso.")
        else:
            st.error("Usuário ou senha inválidos.")

if st.session_state["logado"]:

    import streamlit as st
    import pandas as pd
    import os
    from datetime import datetime

    # Caminhos
    CAMINHO_CASAS = "base_de_dados/casas.csv"
    CAMINHO_TIPOLOGIA = "base_de_dados/tipologia.csv"
    CAMINHO_PRECOS = "base_de_dados/precos.csv"
    CAMINHO_MEDICOES = "base_de_dados/medicoes"
    SENHA = "240992"

    # Carregar dados
    df_casas = pd.read_csv(CAMINHO_CASAS)
    df_tipologia = pd.read_csv(CAMINHO_TIPOLOGIA)
    df_precos = pd.read_csv(CAMINHO_PRECOS)


    menu = []
    permissoes = st.session_state["permissoes"]
    if permissoes.get("Cadastro"): menu.append("📋 Cadastro")
    if permissoes.get("Medicao"): menu.append("🧮 Medição")
    if permissoes.get("Relatorio"): menu.append("📊 Relatório por Casa")
    if permissoes.get("Historico"): menu.append("📚 Histórico")
    if permissoes.get("Exportacoes"): menu.append("📁 Exportações")
    if permissoes.get("Admin"): menu.append("👥 Gerenciar Usuários")
    escolha = st.sidebar.radio("Menu", menu)

    if escolha == "📋 Cadastro":
        st.title("📋 Cadastro Base")
        senha = st.text_input("Digite a senha para editar os dados", type="password")
        if senha == SENHA:
            aba = st.radio("Escolha a tabela:", ["Lotes e Tipologia", "Tipologia - Dimensões", "Preços por Serviço"])
            if aba == "Lotes e Tipologia":
                df = st.data_editor(df_casas, num_rows="dynamic", key="casas")
                if st.button("Salvar Lotes"):
                    df.to_csv(CAMINHO_CASAS, index=False)
                    st.success("Lotes salvos.")
            elif aba == "Tipologia - Dimensões":
                df = st.data_editor(df_tipologia, num_rows="dynamic", key="tipos")
                if st.button("Salvar Tipologia"):
                    df.to_csv(CAMINHO_TIPOLOGIA, index=False)
                    st.success("Tipologia salva.")
            elif aba == "Preços por Serviço":
                df = st.data_editor(df_precos, num_rows="dynamic", key="precos")
                if st.button("Salvar Preços"):
                    df.to_csv(CAMINHO_PRECOS, index=False)
                    st.success("Preços salvos.")
        else:
            st.warning("Digite a senha para liberar a edição.")

    elif escolha == "🧮 Medição":
        st.title("🧮 Medição por Casa")
        modo = st.radio("Tipo de Ação", ["Nova Medição", "Abrir Medição Existente"])
        df_reaberta = None
        edicao_liberada = True

        medicoes_existentes = [f.replace(".xlsx", "") for f in os.listdir(CAMINHO_MEDICOES) if f.endswith(".xlsx")]

        if modo == "Abrir Medição Existente":
            casas_selecionadas = []
            if df_reaberta is not None:
                casas_selecionadas_existentes = df_reaberta['Lote'].dropna().unique().tolist()
                casas_todas = df_casas['Lote'].unique().tolist()
                casas_selecionadas = st.multiselect('Selecionar Casas', options=casas_todas, default=casas_selecionadas_existentes)
            medicao_reaberta = st.selectbox("Selecionar uma medição existente", options=[""] + medicoes_existentes)
            if medicao_reaberta:
                df_reaberta = pd.read_excel(os.path.join(CAMINHO_MEDICOES, f"{medicao_reaberta}.xlsx"))
                senha_edicao = st.text_input("Senha para liberar edição:", type="password")
                edicao_liberada = senha_edicao == SENHA
            nome_medicao = medicao_reaberta
            if df_reaberta is not None:
                casas_selecionadas_existentes = df_reaberta['Lote'].dropna().unique().tolist()
                casas_todas = df_casas['Lote'].unique().tolist()
                casas_selecionadas = st.multiselect('Selecionar Casas', options=casas_todas, default=casas_selecionadas_existentes)
            casas_todas = df_casas['Lote'].unique().tolist()
        else:
            num_medicao = st.text_input("Número da Medição (ex: 01, 02, 10...)", "")
            if num_medicao:
                num_formatado = num_medicao.zfill(2) if num_medicao.isnumeric() else "00"
                nome_medicao = f"Medicao{num_formatado}"
                st.write(f"📌 Nome da Medição: **{nome_medicao}**")
            casas_selecionadas = st.multiselect("Selecionar Casas", options=df_casas["Lote"].unique())

        modo_input = st.radio("Lançar por:", ["% Executada", "QTD Executada (m²)"])
        todas_medicoes = []

        for lote in casas_selecionadas[::-1]:
            if pd.isna(lote) or lote == '':
                continue
            linha_casa = df_casas[df_casas['Lote'] == lote]
            if linha_casa.empty:
                st.warning(f"Lote '{lote}' não encontrado na base de dados.")
                continue
            modelo = linha_casa['Modelo'].values[0]
            st.markdown(f"### Lote: {lote} (Tipo: {modelo})")
            if df_reaberta is not None and lote in df_reaberta["Lote"].values:
                equipe_default = df_reaberta[df_reaberta["Lote"] == lote]["Equipe"].values[0]
            else:
                equipe_default = ""
            equipe = st.text_input(f"Equipe Responsável (Casa {lote})", value=equipe_default, key=f"equipe_{lote}", disabled=not edicao_liberada)

            df_servicos = df_tipologia[df_tipologia["Modelo"] == modelo].copy()
            df_servicos = df_servicos.merge(df_precos, on="Serviço", how="left")

            dados = {"Lote": [], "Serviço": [], "% Exec": [], "QTD Exec": [], "Valor Exec.": [], "Equipe": []}

            for _, row in df_servicos.iterrows():
                servico = row["Serviço"]
                qtd_total = row["QTD (m²)"]
                preco = row["Valor Unitário"]

                valor_salvo = 0.0
                qtd_salva = None
                if df_reaberta is not None:
                    filtro = (df_reaberta["Lote"] == lote) & (df_reaberta["Serviço"] == servico)
                    if filtro.any():
                        linha = df_reaberta.loc[filtro].iloc[0]
                        valor_salvo = linha["% Exec"]
                        qtd_salva = linha["QTD Exec"]

                perc_padrao = float(valor_salvo)
                qtd_padrao = qtd_salva if qtd_salva is not None else (perc_padrao / 100) * qtd_total

                key_perc = f"perc_{lote}_{servico}"
                key_qtd = f"qtd_{lote}_{servico}"

                col1, col2 = st.columns(2)
                if modo_input == "% Executada":
                    with col1:
                        perc = st.number_input(f"{servico} - % Executado", min_value=0.0, max_value=100.0, step=1.0,
                                               value=round(perc_padrao, 2), key=key_perc, disabled=not edicao_liberada)
                    qtd = round((perc / 100) * qtd_total, 2)
                    with col2:
                        st.number_input(f"{servico} - QTD Executada (m²)", value=qtd, disabled=True, key=f"qtd_{lote}_{servico}")
                else:
                    with col1:
                        qtd = st.number_input(f"{servico} - QTD Executada (m²)", min_value=0.0, step=0.01,
                                              value=round(qtd_padrao, 2), key=key_qtd, disabled=not edicao_liberada)
                    perc = round((qtd / qtd_total) * 100, 2) if qtd_total else 0
                    with col2:
                        st.number_input(f"{servico} - % Executado", value=perc, disabled=True, key=f"perc_{lote}_{servico}")

                valor = qtd * preco
                dados["Lote"].append(lote)
                dados["Serviço"].append(servico)
                dados["% Exec"].append(perc)
                dados["QTD Exec"].append(qtd)
                dados["Valor Exec."].append(valor)
                dados["Equipe"].append(equipe)

            df_lote = pd.DataFrame(dados)
            st.markdown(f"**Total Executado - Casa {lote}: R$ {df_lote['Valor Exec.'].sum():,.2f}**")

            df_lote_formatado = df_lote[["Serviço", "% Exec", "QTD Exec", "Valor Exec."]].copy()
            df_lote_formatado["% Exec"] = df_lote_formatado["% Exec"].map(lambda x: f"{x:.2f}%")
            df_lote_formatado["QTD Exec"] = df_lote_formatado["QTD Exec"].map(lambda x: f"{x:.2f}")
            df_lote_formatado["Valor Exec."] = df_lote_formatado["Valor Exec."].map(lambda x: f"R$ {x:,.2f}")
            st.dataframe(df_lote_formatado)

            todas_medicoes.append(df_lote)

        
        st.markdown("### 💾 Salvar Medição")
        if todas_medicoes and edicao_liberada:
            if st.button("Salvar Medição", key=f"salvar_{nome_medicao}"):
                df_final_formatado = []
                for df_lote_raw in todas_medicoes:
                    if df_lote_raw.empty:
                        continue
                    lote = df_lote_raw["Lote"].iloc[0]
                    equipe = df_lote_raw["Equipe"].iloc[0]
                    total_lote = df_lote_raw["Valor Exec."].sum()
                    for i, row in df_lote_raw.iterrows():
                        qtd_total = df_tipologia[
                            (df_tipologia["Modelo"] == modelo)
                            & (df_tipologia["Serviço"] == row["Serviço"])
                        ]["QTD (m²)"].values[0]
                        qtd_executada = round(qtd_total * row["% Exec"] / 100, 2)
                        valor_unit = df_precos[df_precos["Serviço"] == row["Serviço"]]["Valor Unitário"].values[0]
                        valor_exec = round(qtd_executada * valor_unit, 2)
                        df_final_formatado.append({
                            "Medição": nome_medicao,
                            "Lote": lote,
                            "Equipe": equipe,
                            "Tipologia": modelo,
                            "Serviço": row["Serviço"],
                            "QTD Exec": qtd_executada,
                            "% Exec": row["% Exec"],
                            "Valor Unit.": valor_unit,
                            "Valor Exec.": valor_exec,
                            "Valor Total Lote": total_lote
                        })
                    df_final_formatado.append({})  # linha em branco
                df_export = pd.DataFrame(df_final_formatado)
                caminho = os.path.join(CAMINHO_MEDICOES, f"{nome_medicao}.xlsx")
                with pd.ExcelWriter(caminho, engine="openpyxl", mode="w") as writer:
                    df_export.to_excel(writer, index=False, sheet_name="Medição")
                st.success("✅ Medição salva com sucesso no novo formato!")

    elif escolha == "📊 Relatório por Casa":
        st.title("📊 Relatório Consolidado por Casa")
        import glob

        arquivos = glob.glob(os.path.join(CAMINHO_MEDICOES, "*.xlsx"))
        df_todas = pd.concat([pd.read_excel(arq).assign(Medição=os.path.basename(arq).replace(".xlsx", "")) for arq in arquivos])

        df_modelo = df_tipologia.merge(df_precos, on="Serviço")
        df_modelo["Total_Contrato_Serv"] = df_modelo["QTD (m²)"] * df_modelo["Valor Unitário"]

        casas_modelos = df_casas[["Lote", "Modelo"]]
        contratos = casas_modelos.merge(df_modelo, on="Modelo", how="left")

        contratos = contratos[["Lote", "Serviço", "QTD (m²)", "Valor Unitário", "Total_Contrato_Serv"]]

        pivot_medicoes = df_todas.pivot_table(
            index=["Lote", "Serviço"],
            columns="Medição",
            values="QTD Exec",
            aggfunc="sum"
        ).fillna(0)

        pivot_medicoes.columns = [f"Med_{i+1}" for i in range(len(pivot_medicoes.columns))]

        df_merge = contratos.merge(pivot_medicoes, on=["Lote", "Serviço"], how="left").fillna(0)

        col_medicoes = [col for col in df_merge.columns if col.startswith("Med_")]
        df_merge["Total Medido"] = df_merge[col_medicoes].sum(axis=1)
        df_merge["Valor Medido"] = df_merge["Total Medido"] * df_merge["Valor Unitário"]
        df_merge["Falta Medir"] = df_merge["QTD (m²)"] - df_merge["Total Medido"]
        df_merge["Falta Receber"] = df_merge["Total_Contrato_Serv"] - df_merge["Valor Medido"]

        lotes_com_medicao = df_todas["Lote"].unique()
        for lote in sorted(df_merge["Lote"].unique()):
            if lote not in lotes_com_medicao:
                continue
            with st.expander(f"🏠 Lote: {lote}"):
                df_lote = df_merge[df_merge["Lote"] == lote].copy()
                df_lote["QTD (m²)"] = df_lote["QTD (m²)"].map(lambda x: f"{x:.2f}")
                df_lote["Valor Unitário"] = df_lote["Valor Unitário"].map(lambda x: f"R$ {x:,.2f}")
                df_lote["Total_Contrato_Serv"] = df_lote["Total_Contrato_Serv"].map(lambda x: f"R$ {x:,.2f}")
                df_lote["Total Medido"] = df_lote["Total Medido"].map(lambda x: f"{x:.2f}")
                df_lote["Valor Medido"] = df_lote["Valor Medido"].map(lambda x: f"R$ {x:,.2f}")
                df_lote["Falta Medir"] = df_lote["Falta Medir"].map(lambda x: f"{x:.2f}")
                df_lote["Falta Receber"] = df_lote["Falta Receber"].map(lambda x: f"R$ {x:,.2f}")

                colunas_finais = ["Serviço", "QTD (m²)", "Valor Unitário", "Total_Contrato_Serv"] + col_medicoes + ["Total Medido", "Valor Medido", "Falta Medir", "Falta Receber"]
                st.dataframe(df_lote[colunas_finais], use_container_width=True)

    elif escolha == "📚 Histórico":
        st.title("📚 Histórico de Medições por Casa")
        import glob

        arquivos = glob.glob(os.path.join(CAMINHO_MEDICOES, "*.xlsx"))
        historico = []

        for arquivo in arquivos:
            nome_medicao = os.path.basename(arquivo).replace(".xlsx", "")
            df_medicao = pd.read_excel(arquivo)

            for lote in df_medicao["Lote"].unique():
                df_lote = df_medicao[df_medicao["Lote"] == lote]
                total_lote = df_lote["Valor Exec."].sum()
            equipe = df_lote['Equipe'].values[0] if not df_lote.empty and 'Equipe' in df_lote.columns else ''
            historico.append({
                    "Lote": lote,
                    "Medição": nome_medicao,
                    "Equipe": equipe,
                    "Total Executado (R$)": total_lote,
                    "Detalhes": df_lote
                })

        if not historico:
            st.info("Nenhuma medição encontrada.")
        else:
            df_resumo = pd.DataFrame(historico)[["Lote", "Medição", "Equipe", "Total Executado (R$)"]]
            df_resumo = df_resumo.sort_values(by=["Lote", "Medição"])

            st.subheader("Resumo por Casa e Medição")
            st.dataframe(df_resumo, use_container_width=True)

            st.subheader("🔍 Detalhamento por Casa")
            lotes = sorted(df_resumo["Lote"].unique())
            lote_escolhido = st.selectbox("Selecionar um Lote", lotes)

            for item in historico:
                if item["Lote"] == lote_escolhido:
                    with st.expander(f"Medição: {item['Medição']} | Equipe: {item['Equipe']} | Total: R$ {item['Total Executado (R$)']:,.2f}"):
                        df_detalhes = item["Detalhes"].copy()
                        df_detalhes = df_detalhes[["Serviço", "% Exec", "QTD Exec", "Valor Exec."]]
                        df_detalhes["% Exec"] = df_detalhes["% Exec"].map(lambda x: f"{x:.2f}%")
                        df_detalhes["QTD Exec"] = df_detalhes["QTD Exec"].map(lambda x: f"{x:.2f}")
                        df_detalhes["Valor Exec."] = df_detalhes["Valor Exec."].map(lambda x: f"R$ {x:,.2f}")
                        st.dataframe(df_detalhes, use_container_width=True)

                        if st.button(f"Reabrir Medição '{item['Medição']}'", key=f"reabrir_{item['Medição']}"):
                            from shutil import copyfile
                            nova_versao = item["Medição"]
                            contador = 2
                            while os.path.exists(os.path.join(CAMINHO_MEDICOES, f"{nova_versao}.xlsx")):
                                nova_versao = f"{item['Medição']}_v{contador}"
                                contador += 1
                            copyfile(os.path.join(CAMINHO_MEDICOES, f"{item['Medição']}.xlsx"),
                                     os.path.join(CAMINHO_MEDICOES, f"{nova_versao}.xlsx"))
                            st.success(f"Medição reaberta como '{nova_versao}'")


    elif escolha == "📁 Exportações":
        st.title("📁 Exportar Medição Salva")

        medicoes_existentes = [f.replace(".xlsx", "") for f in os.listdir(CAMINHO_MEDICOES) if f.endswith(".xlsx")]
        nome_selecionado = st.selectbox("Selecionar Medição para Exportar", medicoes_existentes)

        if nome_selecionado:
            caminho = os.path.join(CAMINHO_MEDICOES, f"{nome_selecionado}.xlsx")
            df_final = pd.read_excel(caminho, engine="openpyxl")
            st.success(f"Medição '{nome_selecionado}' carregada com sucesso.")

            # ✅ Prévia da Medição: Lote e Valor Total
            st.subheader("🔎 Prévia da Medição")
            df_prev = df_final.groupby("Lote")["Valor Exec."].sum().reset_index()
            df_prev.rename(columns={"Valor Exec.": "Total Executado (R$)"}, inplace=True)
            df_prev["Total Executado (R$)"] = df_prev["Total Executado (R$)"].map(lambda x: f"R$ {x:,.2f}")
            st.dataframe(df_prev, use_container_width=True)

            total_geral = df_final["Valor Exec."].sum()
            st.markdown(f"**💰 Valor Total da Medição: R$ {total_geral:,.2f}**")


            import io
            from fpdf import FPDF

            col1, col2 = st.columns(2)

            with col1:
                output_excel = io.BytesIO()
                df_final.to_excel(output_excel, index=False, engine="openpyxl", sheet_name="Medição")
                output_excel.seek(0)
            st.download_button("⬇️ Exportar para Excel", output_excel, file_name=f"{nome_selecionado}.xlsx")

            with col2:
                pdf = FPDF()
                pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.set_title(f"Medição: {nome_selecionado}")
            pdf.cell(200, 10, txt=f"Medição: {nome_selecionado}", ln=True, align='C')
            pdf.ln(5)

            for lote in df_final["Lote"].unique():
                    df_lote = df_final[df_final["Lote"] == lote]
            equipe = df_lote['Equipe'].values[0] if not df_lote.empty and 'Equipe' in df_lote.columns else ''
            pdf.set_font("Arial", 'B', size=10)
            pdf.cell(200, 8, txt=f"Lote: {lote} - Equipe: {equipe}", ln=True)
            pdf.set_font("Arial", size=9)
            for _, row in df_lote.iterrows():
                        servico = row["Serviço"]
                        perc = f"{row['% Exec']:.2f}%"
                        qtd = f"{row['QTD Exec']:.2f} m²"
                        valor = f"R$ {row['Valor Exec.']:.2f}"
                        pdf.cell(200, 6, txt=f"{servico} | {perc} | {qtd} | {valor}", ln=True)
            total = df_lote["Valor Exec."].sum()
            pdf.set_font("Arial", 'B', size=9)
            pdf.cell(200, 8, txt=f"Total Executado (Lote {lote}): R$ {total:,.2f}", ln=True)
            pdf.ln(4)

            pdf_bytes = pdf.output(dest="S").encode("latin-1")
            st.download_button("⬇️ Exportar para PDF", pdf_bytes, file_name=f"{nome_selecionado}.pdf")


    elif escolha == "👥 Gerenciar Usuários":
        st.title("👥 Gerenciar Usuários")
        df_usuarios = pd.read_csv(CAMINHO_USUARIOS)
        st.dataframe(df_usuarios.drop(columns='Senha'))

        st.subheader("🗑️ Excluir Usuário")
        for i, row in df_usuarios.iterrows():
            if row["Usuario"] != st.session_state["usuario"]:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{row['Usuario']}")
                with col2:
                    if st.button(f"Excluir", key=f"excluir_{i}"):
                        df_usuarios = df_usuarios[df_usuarios["Usuario"] != row["Usuario"]]
                        df_usuarios.to_csv(CAMINHO_USUARIOS, index=False)
                        st.success(f"Usuário '{row['Usuario']}' excluído com sucesso.")
                        st.stop()

        with st.expander("➕ Adicionar Novo Usuário"):
            with st.form("novo_usuario"):
                nome = st.text_input("Nome do Usuário")
                senha = st.text_input("Senha", type="password")
                col1, col2, col3 = st.columns(3)
                with col1:
                    acesso_cadastro = st.checkbox("Cadastro")
                    acesso_medicao = st.checkbox("Medição")
                with col2:
                    acesso_relatorio = st.checkbox("Relatório")
                    acesso_historico = st.checkbox("Histórico")
                with col3:
                    acesso_exportacoes = st.checkbox("Exportações")
                    acesso_admin = st.checkbox("Admin")

                salvar = st.form_submit_button("Salvar Usuário")
                if salvar:
                    novo = pd.DataFrame([{
                        "Usuario": nome,
                        "Senha": senha,
                        "Cadastro": acesso_cadastro,
                        "Medicao": acesso_medicao,
                        "Relatorio": acesso_relatorio,
                        "Historico": acesso_historico,
                        "Exportacoes": acesso_exportacoes,
                        "Admin": acesso_admin
                    }])
                    df_usuarios = pd.concat([df_usuarios, novo], ignore_index=True)
                    df_usuarios.to_csv(CAMINHO_USUARIOS, index=False)
                    st.success("Usuário salvo com sucesso.")


