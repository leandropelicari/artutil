import flet as ft
import os
import unicodedata
import base64

def main(page: ft.Page):
    page.title = "Calculadora - Art Útil"
    page.theme_mode = "light"
    page.bgcolor = "#F9F6F0"
    page.padding = 0
    
    # --- PALETA DE CORES DA ART ÚTIL ---
    COR_PRETA = "#171717"
    COR_PINUS = "#EADDCE"
    COR_BORDA = "#D4C4B7"
    COR_TEXTO = "#44403C"
    
    # --- FUNÇÕES DE INTERFACE SEGURAS ---
    def criar_campo_texto(label, valor="", on_change=None):
        return ft.TextField(
            label=label,
            value=valor,
            on_change=on_change,
            border_radius=12,
            border_color=COR_BORDA,
            focused_border_color=COR_PRETA,
            content_padding=15,
            label_style=ft.TextStyle(color=COR_TEXTO)
        )

    def criar_campo_numero(label, prefixo="", sufixo="", valor="", on_change=None):
        return ft.TextField(
            label=label, 
            prefix=ft.Text(prefixo, color="#A8A29E") if prefixo else None, 
            suffix=ft.Text(sufixo, color="#A8A29E") if sufixo else None, 
            value=valor, 
            on_change=on_change,
            keyboard_type="number",
            text_align="right",
            border_radius=12,
            border_color=COR_BORDA,
            focused_border_color=COR_PRETA,
            content_padding=15,
            label_style=ft.TextStyle(color=COR_TEXTO)
        )

    def extrair_numero(campo):
        if not campo.value or campo.value.strip() == "": return 0.0
        try:
            return float(campo.value.replace(",", "."))
        except ValueError:
            return 0.0

    def remover_acentos(texto):
        return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn')

    # --- HEADER (LOGOTIPO ART ÚTIL) ---
    header = ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text("/\\", size=28, weight="bold", color=COR_PRETA),
                ft.Text("ART ÚTIL", size=32, weight="w900", color=COR_PRETA),
                ft.Text("MÓVEIS DE PINUS", size=12, weight="bold", color=COR_PRETA)
            ], spacing=0, horizontal_alignment="center")
        ], alignment="center"),
        bgcolor=COR_PINUS,
        padding=20
    )

    # ==========================================
    # LÓGICA DE CÁLCULO E RESULTADOS (AO VIVO)
    # ==========================================
    resultado_texto = ft.Text("Preencha os dados para ver o resultado.", size=14, color=COR_TEXTO, text_align="center")
    card_resultado = ft.Container(content=resultado_texto, bgcolor="white", border_radius=12, padding=20)

    def calcular_tudo(e=None):
        salvar_padrao(None)
        bruto = extrair_numero(txt_preco_bruto)
        tx_comissao = extrair_numero(txt_comissao) / 100
        tx_promocao = extrair_numero(txt_promocao) / 100
        tx_imposto = extrair_numero(txt_imposto) / 100
        impulsionamento = extrair_numero(txt_impulsionamento)

        descontos = (bruto * (tx_comissao + tx_promocao + tx_imposto)) + impulsionamento
        custo_mp = sum(extrair_numero(item["ctrl_qtd"]) * extrair_numero(item["ctrl_valor"]) for item in campos_mp)
        custo_mo = extrair_numero(txt_tempo) * extrair_numero(txt_valor_hora)

        volume = extrair_numero(txt_volume_mensal)
        if volume == 0: volume = 1 
        custo_fixo_unitario = sum(extrair_numero(item["ctrl_valor"]) for item in campos_fixos) / volume

        custo_total = custo_mp + custo_mo + custo_fixo_unitario + descontos
        lucro_unitario = bruto - custo_total
        margem_real = (lucro_unitario / bruto * 100) if bruto > 0 else 0

        cor_lucro = "#16A34A" if lucro_unitario >= 0 else "#DC2626"

        card_resultado.content = ft.Column([
            ft.Text(f"PRODUTO: {txt_produto.value.upper() if txt_produto.value else 'NÃO INFORMADO'}", weight="bold", size=16, color=COR_PRETA),
            ft.Divider(color=COR_BORDA),
            ft.Row([ft.Text("Preço de Venda:", color=COR_TEXTO), ft.Text(f"R$ {bruto:.2f}", weight="bold")], alignment="spaceBetween"),
            ft.Row([ft.Text("Taxas/Descontos:", color=COR_TEXTO), ft.Text(f"- R$ {descontos:.2f}", color="#DC2626")], alignment="spaceBetween"),
            ft.Row([ft.Text("Matéria Prima:", color=COR_TEXTO), ft.Text(f"- R$ {custo_mp:.2f}", color="#DC2626")], alignment="spaceBetween"),
            ft.Row([ft.Text("Mão de Obra:", color=COR_TEXTO), ft.Text(f"- R$ {custo_mo:.2f}", color="#DC2626")], alignment="spaceBetween"),
            ft.Row([ft.Text("Custo Fixo (Un.):", color=COR_TEXTO), ft.Text(f"- R$ {custo_fixo_unitario:.2f}", color="#DC2626")], alignment="spaceBetween"),
            ft.Divider(color=COR_BORDA),
            ft.Row([ft.Text("CUSTO TOTAL:", weight="bold", color=COR_PRETA), ft.Text(f"R$ {custo_total:.2f}", weight="bold", color=COR_PRETA)], alignment="spaceBetween"),
            ft.Container(height=10),
            ft.Row([ft.Text("LUCRO LÍQUIDO", size=18, weight="bold", color=cor_lucro), ft.Text(f"R$ {lucro_unitario:.2f}", size=18, weight="bold", color=cor_lucro)], alignment="spaceBetween"),
            ft.Row([ft.Text("MARGEM", size=14, color=cor_lucro), ft.Text(f"{margem_real:.1f}%", size=14, weight="bold", color=cor_lucro)], alignment="spaceBetween"),
        ])
        
        try:
            card_resultado.update()
        except Exception:
            pass

    # ==========================================
    # CAMPOS DE ENTRADA
    # ==========================================
    txt_cliente = criar_campo_texto("Nome do cliente", on_change=calcular_tudo)
    txt_produto = criar_campo_texto("Nome do produto", on_change=calcular_tudo)
    
    txt_preco_bruto = criar_campo_numero("Preço produto (Bruto)", prefixo="R$ ", on_change=calcular_tudo)
    txt_comissao = criar_campo_numero("Comissão plataforma", sufixo=" %", on_change=calcular_tudo)
    txt_impulsionamento = criar_campo_numero("Impulsionamento", prefixo="R$ ", on_change=calcular_tudo)
    txt_promocao = criar_campo_numero("Promoção de campanha", sufixo=" %", on_change=calcular_tudo)
    txt_imposto = criar_campo_numero("Imposto", sufixo=" %", on_change=calcular_tudo)

    bloco_plataforma = ft.Column([
        txt_cliente, txt_produto,
        ft.Container(height=5),
        txt_preco_bruto, txt_comissao, txt_impulsionamento, txt_promocao, txt_imposto
    ], spacing=15)

    # --- MATÉRIA PRIMA ---
    lista_materiais_padrao = [
        "Tábua 25x300x2", "Tábua 30x300x2", "Parafuso 1/4\"x2\"",
        "Parafuso 3,5 x 30", "Parafuso 3,5 x 40", "Pino tipo F",
        "Cola", "Porca 1/4\" Parlock", "Arruela 1/4\"",
        "Cavilha", "Lixa 4\"", "Compensado", "Painel Pinus"
    ]

    campos_mp = []
    coluna_mp_itens = ft.Column(spacing=15)

    def adicionar_item_mp(nome="", qtd="", valor=""):
        txt_qtd = criar_campo_numero("Qtd", valor=qtd, on_change=calcular_tudo)
        txt_qtd.expand = True
        txt_valor = criar_campo_numero("R$ Un.", valor=valor, on_change=calcular_tudo)
        txt_valor.expand = True
        
        opcoes_dd = [ft.dropdown.Option(m) for m in lista_materiais_padrao]
        
        dd_nome = ft.Dropdown(
            label="Selecione o Material",
            options=opcoes_dd,
            value=nome if nome in lista_materiais_padrao else None,
            on_change=calcular_tudo,
            border_radius=12,
            border_color=COR_BORDA,
            focused_border_color=COR_PRETA,
            content_padding=15,
            label_style=ft.TextStyle(color=COR_TEXTO)
        )

        def remover_item(e_rem):
            coluna_mp_itens.controls.remove(cartao)
            campos_mp.remove(ref_dict)
            calcular_tudo()
            page.update()

        btn_remover = ft.Container(
            content=ft.Row([ft.Text("Excluir Item", color="#DC2626", weight="bold", size=13)], alignment="center"),
            on_click=remover_item,
            padding=10,
            bgcolor="#FEE2E2",
            border_radius=8
        )
        
        cartao = ft.Container(
            content=ft.Column([
                dd_nome,
                ft.Row([txt_qtd, txt_valor]),
                btn_remover
            ]),
            bgcolor="white",
            padding=15,
            border_radius=12
        )
        
        ref_dict = {"get_nome": lambda: dd_nome.value or "", "ctrl_qtd": txt_qtd, "ctrl_valor": txt_valor}
        campos_mp.append(ref_dict)
        coluna_mp_itens.controls.append(cartao)
        calcular_tudo()
        try:
            page.update()
        except Exception:
            pass

    btn_add_mp = ft.Container(
        content=ft.Row([ft.Text("+ Adicionar Material", color=COR_PRETA, weight="bold")], alignment="center"),
        padding=12,
        bgcolor=COR_PINUS,
        border_radius=8,
        on_click=lambda e: adicionar_item_mp() 
    )
    
    bloco_materia_prima = ft.Column([
        coluna_mp_itens,
        ft.Container(height=5),
        btn_add_mp
    ], spacing=15)

    # --- MÃO DE OBRA E FIXOS ---
    txt_tempo = criar_campo_numero("Tempo Estimado (Horas)", valor="", on_change=calcular_tudo)
    txt_valor_hora = criar_campo_numero("Valor por Hora", prefixo="R$ ", valor="", on_change=calcular_tudo)
    txt_margem_lucro_desejada = criar_campo_numero("Margem Lucro Desejada", sufixo=" %", valor="", on_change=calcular_tudo)
    txt_volume_mensal = criar_campo_numero("Qtd Estimada de Clientes/Mês", valor="1", on_change=calcular_tudo)

    lista_custos_padrao = [
        "Contador", "Aluguel", "Luz", "Água", "IPTU", 
        "Combustível", "Alimentação", "Manutenção Carro", "Manutenção Máquina"
    ]

    campos_fixos = []
    coluna_fixos_itens = ft.Column(spacing=15)

    def adicionar_item_fixo(nome="", valor=""):
        txt_valor = criar_campo_numero("Valor Mensal R$", valor=valor, on_change=calcular_tudo)
        opcoes_dd_custo = [ft.dropdown.Option(c) for c in lista_custos_padrao]
        
        dd_nome = ft.Dropdown(
            label="Selecione o Custo",
            options=opcoes_dd_custo,
            value=nome if nome in lista_custos_padrao else None,
            on_change=calcular_tudo,
            border_radius=12,
            border_color=COR_BORDA,
            focused_border_color=COR_PRETA,
            content_padding=15,
            label_style=ft.TextStyle(color=COR_TEXTO)
        )

        def remover_item(e_rem):
            coluna_fixos_itens.controls.remove(cartao)
            campos_fixos.remove(ref_dict)
            calcular_tudo()
            page.update()

        btn_remover = ft.Container(
            content=ft.Row([ft.Text("Excluir Custo", color="#DC2626", weight="bold", size=13)], alignment="center"),
            on_click=remover_item,
            padding=10,
            bgcolor="#FEE2E2",
            border_radius=8
        )
        
        cartao = ft.Container(
            content=ft.Column([
                dd_nome,
                txt_valor,
                btn_remover
            ]),
            bgcolor="white",
            padding=15,
            border_radius=12
        )
        
        ref_dict = {"get_nome": lambda: dd_nome.value or "", "ctrl_valor": txt_valor}
        campos_fixos.append(ref_dict)
        coluna_fixos_itens.controls.append(cartao)
        calcular_tudo()
        try:
            page.update()
        except Exception:
            pass

    btn_add_fixo = ft.Container(
        content=ft.Row([ft.Text("+ Adicionar Custo", color=COR_PRETA, weight="bold")], alignment="center"),
        padding=12,
        bgcolor=COR_PINUS,
        border_radius=8,
        on_click=lambda e: adicionar_item_fixo()
    )

    bloco_mo_fixos = ft.Column([
        txt_tempo, txt_valor_hora, txt_margem_lucro_desejada,
        ft.Divider(color=COR_BORDA),
        ft.Text("Custos Fixos (Rateio)", size=16, weight="bold", color=COR_PRETA),
        txt_volume_mensal,
        coluna_fixos_itens,
        ft.Container(height=5),
        btn_add_fixo
    ], spacing=15)

    # ==========================================
    # SALVAMENTO CLIENT_STORAGE
    # ==========================================
    def salvar_padrao(e):
        dados_salvar = {
            "plataforma": {
                "comissao": txt_comissao.value,
                "promocao": txt_promocao.value,
                "imposto": txt_imposto.value
            },
            "mo": {
                "valor_hora": txt_valor_hora.value,
                "margem": txt_margem_lucro_desejada.value,
                "volume": txt_volume_mensal.value
            },
            "materiais": [{"nome": m["get_nome"](), "qtd": m["ctrl_qtd"].value, "valor": m["ctrl_valor"].value} for m in campos_mp],
            "fixos": [{"nome": f["get_nome"](), "valor": f["ctrl_valor"].value} for f in campos_fixos]
        }
        try:
            page.client_storage.set("padrao_art_util", dados_salvar)
        except Exception:
            pass

    def carregar_padrao():
        try:
            dados = page.client_storage.get("padrao_art_util")
            if dados:
                txt_comissao.value = dados["plataforma"].get("comissao", "")
                txt_promocao.value = dados["plataforma"].get("promocao", "")
                txt_imposto.value = dados["plataforma"].get("imposto", "")
                txt_valor_hora.value = dados["mo"].get("valor_hora", "")
                txt_margem_lucro_desejada.value = dados["mo"].get("margem", "")
                txt_volume_mensal.value = dados["mo"].get("volume", "1")
                
                for m in dados["materiais"]:
                    adicionar_item_mp(m["nome"], m["qtd"], m["valor"])
                    
                for f in dados["fixos"]:
                    adicionar_item_fixo(f["nome"], f["valor"])
                return
        except Exception:
            pass
            
        txt_volume_mensal.value = "1"
        adicionar_item_mp("", "", "")
        adicionar_item_fixo("", "")

    # ==========================================
    # EXPORTAÇÃO PDF
    # ==========================================
    def exportar_pdf(e):
        try:
            from fpdf import FPDF
        except ImportError:
            return

        bruto = extrair_numero(txt_preco_bruto)
        descontos = (bruto * ((extrair_numero(txt_comissao) / 100) + (extrair_numero(txt_promocao) / 100) + (extrair_numero(txt_imposto) / 100))) + extrair_numero(txt_impulsionamento)
        custo_mp = sum(extrair_numero(item["ctrl_qtd"]) * extrair_numero(item["ctrl_valor"]) for item in campos_mp)
        custo_mo = extrair_numero(txt_tempo) * extrair_numero(txt_valor_hora)
        volume = extrair_numero(txt_volume_mensal) if extrair_numero(txt_volume_mensal) > 0 else 1
        custo_fixo_unitario = sum(extrair_numero(item["ctrl_valor"]) for item in campos_fixos) / volume
        custo_total = custo_mp + custo_mo + custo_fixo_unitario + descontos
        lucro_unitario = bruto - custo_total

        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(190, 10, txt="ART UTIL - RELATORIO DE CUSTOS", ln=True, align='C')
        
        pdf.set_font("Arial", 'B', 12)
        nome_prod = remover_acentos(txt_produto.value.upper() if txt_produto.value else "PRODUTO_NAO_INFORMADO")
        pdf.cell(190, 10, txt=f"PRODUTO: {nome_prod}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", '', 12)
        pdf.cell(100, 10, txt="Preco de Venda (Bruto):", border=0)
        pdf.cell(90, 10, txt=f"R$ {bruto:.2f}", border=0, ln=True, align='R')
        pdf.cell(100, 10, txt="Taxas e Descontos:", border=0)
        pdf.cell(90, 10, txt=f"- R$ {descontos:.2f}", border=0, ln=True, align='R')
        pdf.cell(100, 10, txt="Materia Prima:", border=0)
        pdf.cell(90, 10, txt=f"- R$ {custo_mp:.2f}", border=0, ln=True, align='R')
        pdf.cell(100, 10, txt="Mao de Obra:", border=0)
        pdf.cell(90, 10, txt=f"- R$ {custo_mo:.2f}", border=0, ln=True, align='R')
        pdf.cell(100, 10, txt="Custo Fixo (Rateio Un.):", border=0)
        pdf.cell(90, 10, txt=f"- R$ {custo_fixo_unitario:.2f}", border=0, ln=True, align='R')
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 10, txt="CUSTO TOTAL:", border=0)
        pdf.cell(90, 10, txt=f"R$ {custo_total:.2f}", border=0, ln=True, align='R')
        pdf.ln(5)
        pdf.set_font("Arial", 'L', 12) # ajustado para B caso prefira negrito
        pdf.cell(100, 10, txt="LUCRO LIQUIDO:", border=0)
        pdf.cell(90, 10, txt=f"R$ {lucro_unitario:.2f}", border=0, ln=True, align='R')

        try:
            pdf_output = pdf.output(dest='S')
            if isinstance(pdf_output, str):
                pdf_bytes = pdf_output.encode('latin1')
            else:
                pdf_bytes = pdf_output
                
            b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            data_uri = f"data:application/pdf;base64,{b64_pdf}"
            page.launch_url(data_uri)
        except Exception:
            pass

    btn_pdf = ft.Container(
        content=ft.Row([ft.Text("EXPORTAR EM PDF", color="white", weight="bold")], alignment="center"),
        padding=15, bgcolor="#DC2626", border_radius=30, on_click=exportar_pdf
    )

    carregar_padrao()
    calcular_tudo(None)

    # ==========================================
    # LAYOUT RESPONSIVO INTELIGENTE (COM SCROLL)
    # ==========================================
    ultimo_modo = None

    def construir_ui(e=None):
        nonlocal ultimo_modo
        largura = page.width if page.width and page.width > 0 else 1200
        novo_modo = "desktop" if largura >= 850 else "celular"
        
        if novo_modo == ultimo_modo and len(page.controls) > 0:
            return
            
        ultimo_modo = novo_modo
        page.clean()

        if novo_modo == "desktop":
            # Coluna esquerda com scroll independente
            coluna_esquerda = ft.Column([
                ft.Text("1. Dados da Venda e Plataforma", size=16, weight="bold", color=COR_PRETA),
                bloco_plataforma,
                ft.Divider(color=COR_BORDA, height=30),
                ft.Text("2. Itens do Produto (Matéria Prima)", size=16, weight="bold", color=COR_PRETA),
                bloco_materia_prima,
                ft.Divider(color=COR_BORDA, height=30),
                ft.Text("3. Mão de Obra e Custos Fixos", size=16, weight="bold", color=COR_PRETA),
                bloco_mo_fixos,
                ft.Container(height=30)
            ], scroll="auto", spacing=15, expand=True)

            container_esquerda = ft.Container(content=coluna_esquerda, expand=6, padding=25)

            # Coluna direita com scroll independente
            coluna_direita = ft.Column([
                ft.Text("Painel de Resultados (Ao Vivo)", size=18, weight="bold", color=COR_PRETA),
                card_resultado,
                ft.Container(height=10),
                btn_pdf
            ], scroll="auto", spacing=15, expand=True)

            container_direita = ft.Container(content=coluna_direita, expand=4, padding=25)

            corpo_principal = ft.Row([
                container_esquerda,
                ft.VerticalDivider(width=1, color=COR_BORDA),
                container_direita
            ], expand=True, spacing=0, alignment="start")

            page.add(header, ft.Divider(height=1, color=COR_BORDA), corpo_principal)

        else:
            aba_plataforma_cel = ft.Column([ft.Text("Dados da Venda", size=16, weight="bold", color=COR_PRETA), bloco_plataforma], scroll="auto", spacing=15)
            aba_materia_prima_cel = ft.Column([ft.Text("Matéria Prima", size=16, weight="bold", color=COR_PRETA), bloco_materia_prima], scroll="auto", spacing=15)
            aba_mo_fixos_cel = ft.Column([ft.Text("Mão de Obra e Custos", size=16, weight="bold", color=COR_PRETA), bloco_mo_fixos], scroll="auto", spacing=15)
            aba_resultados_cel = ft.Column([btn_pdf, ft.Container(height=10), card_resultado], scroll="auto")

            conteudos_cel = [aba_plataforma_cel, aba_materia_prima_cel, aba_mo_fixos_cel, aba_resultados_cel]
            nomes_abas_cel = ["Venda", "Materiais", "Custos", "Relatório"]
            botoes_cel = []
            area_conteudo_cel = ft.Container(content=aba_plataforma_cel, expand=True, padding=20)

            def mudar_aba_cel(index_alvo):
                calcular_tudo(None)
                for i, btn in enumerate(botoes_cel):
                    if i == index_alvo:
                        btn.bgcolor, btn.content.color = COR_PRETA, "white"
                    else:
                        btn.bgcolor, btn.content.color = "transparent", COR_TEXTO
                area_conteudo_cel.content = conteudos_cel[index_alvo]
                page.update()

            def criar_botao_aba_cel(nome, index):
                bg = COR_PRETA if index == 0 else "transparent"
                texto_cor = "white" if index == 0 else COR_TEXTO
                btn = ft.Container(
                    content=ft.Text(nome, color=texto_cor, weight="bold", size=13),
                    padding=10, bgcolor=bg, border_radius=20,
                    on_click=lambda e: mudar_aba_cel(index)
                )
                botoes_cel.append(btn)
                return btn

            menu_navegacao_cel = ft.Container(
                content=ft.Row([criar_botao_aba_cel(nome, i) for i, nome in enumerate(nomes_abas_cel)], alignment="spaceBetween"),
                padding=15, bgcolor="white"
            )

            page.add(header, menu_navegacao_cel, ft.Divider(height=1, color=COR_BORDA), area_conteudo_cel)

        page.update()

    page.on_resize = construir_ui
    construir_ui()

porta = int(os.environ.get("PORT", 8080))
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=porta, host="0.0.0.0", assets_dir="assets")
