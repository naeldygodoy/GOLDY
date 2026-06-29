import streamlit as st
import math

# Configuração da página web
st.set_page_config(page_title="Calculadora Frigelar - Câmaras Frias", layout="wide")

st.title("❄️ Calculadora de Câmaras Frias (Módulo Completo)")
st.subheader("Gerador de Orçamentos Rápido e Técnico")
st.markdown("---")

# Layout em duas colunas: Entrada de dados na esquerda, Resultado na direita
col_esquerda, col_direita = st.columns([1, 1.3])

with col_esquerda:
    st.header("1. Dados da Câmara")
    
    comp_ext = st.number_input("Comprimento Externo (metros):", min_value=1.0, value=10.0, step=0.1)
    larg_ext = st.number_input("Largura Externa (metros):", min_value=1.0, value=7.0, step=0.1)
    alt_ext = st.number_input("Altura Externa (metros):", min_value=1.0, value=3.0, step=0.1)
    
    st.markdown("---")
    
    isolamento = st.selectbox("Tipo de Isolamento (Paredes/Teto):", ["EPS", "PIR"])
    temp_desejada = st.selectbox("Temperatura da Câmara:", [
        "0ºC a 15ºC (Resfriados)", 
        "-20ºC (Congelados)", 
        "Abaixo de -20ºC (Sorvetes/Túneis)"
    ])
    
    st.markdown("---")
    st.header("🚪 2. Configuração da Porta")
    
    # Seleção do Tipo de Movimento da Porta
    tipo_movimento = st.radio("Tipo de Porta:", ["Girar", "Correr"], horizontal=True)
    
    # Seleção de tamanho da porta
    tamanho_porta = st.selectbox("Tamanho da Porta (L x A):", ["0,80 x 1,80", "1,00 x 2,00"])
    larg_p, alt_p = (0.80, 1.80) if tamanho_porta == "0,80 x 1,80" else (1.00, 2.00)
    
    # Seleção de Batente (Válido para Girar e Correr)
    tipo_batente = st.radio("Modelo de Batente:", ["3B", "4B"], horizontal=True)
    
    # Regra de Reversibilidade e Lados
    if tipo_movimento == "Girar" and tipo_batente == "4B":
        detalhe_porta = "De Girar 4B (Reversível)"
        st.caption("ℹ️ O modelo 4B de girar é nativamente reversível na montagem.")
    else:
        texto_lado = "Lado de Abertura" if tipo_movimento == "Girar" else "Sentido de Correr"
        lado_selecionado = st.radio(f"{texto_lado} (Olhando por Fora):", ["Direita", "Esquerda"], horizontal=True)
        detalhe_porta = f"De {tipo_movimento} {tipo_batente} (Lado: {lado_selecionado})"
        
    # Regra de resistência baseada na temperatura
    if "Resfriados" in temp_desejada:
        resistencia_porta = "Sem resistência"
    else:
        resistencia_porta = "Com Resistência (Aquecimento de Batente)"

# ================= REGRAS DE NEGÓCIO E ESPESSURAS =================
if isolamento == "EPS":
    larg_modulo = 1.14
    coef_condutividade = 0.041  # W/mK
    if "Resfriados" in temp_desejada:    espessura_teto = 0.10
    elif "Congelados" in temp_desejada:  espessura_teto = 0.15
    else:                                espessura_teto = 0.20
else: # PIR
    larg_modulo = 1.12
    coef_condutividade = 0.022  # W/mK
    if "Resfriados" in temp_desejada:    espessura_teto = 0.07
    elif "Congelados" in temp_desejada:  espessura_teto = 0.12
    else:                                espessura_teto = 0.15

if "Resfriados" in temp_desejada:
    espessura_piso_eps = 0.10
    camadas_piso = "2 camadas de 5cm (5+5)"
    temp_interna_alvo = 5
    evap_alvo = "-10°C"
    tipo_gas = "R22"
elif "Congelados" in temp_desejada:
    espessura_piso_eps = 0.15
    camadas_piso = "1 camada de 5cm + 1 camada de 10cm (5+10)"
    temp_interna_alvo = -20
    evap_alvo = "-25°C"
    tipo_gas = "R404A"
else:
    espessura_piso_eps = 0.20
    camadas_piso = "2 camadas de 10cm (10+10)"
    temp_interna_alvo = -25
    evap_alvo = "-25°C"
    tipo_gas = "R404A"

# ================= CÁLCULO VOLUMÉTRICO E GEOMÉTRICO =================
comp_int = comp_ext - (2 * espessura_teto)
larg_int = larg_ext - (2 * espessura_teto)
alt_int = alt_ext - espessura_teto - espessura_piso_eps - 0.10 
volume_interno = comp_int * larg_int * alt_int

if "Resfriados" in temp_desejada:
    estocagem_ton = (volume_interno * 250 * 0.8) / 1000
    texto_estocagem = f"{estocagem_ton:.2f} Toneladas"
elif "Congelados" in temp_desejada:
    estocagem_ton = (volume_interno * 400 * 0.8) / 1000
    texto_estocagem = f"{estocagem_ton:.2f} Toneladas"
else:
    texto_estocagem = "Definir conforme movimentação"

# ================= QUANTITATIVOS DE PAINÉIS E PISO =================
alt_painel = alt_ext - espessura_teto
total_paineis_parede = math.ceil(math.ceil((comp_ext / larg_modulo) * 2) / 2 * 2) + math.ceil(math.ceil((larg_int / larg_modulo) * 2) / 2 * 2)

total_paineis_teto = math.ceil(comp_ext / larg_modulo)
comprimento_painel_teto = larg_ext

area_externa = comp_ext * larg_ext
placas_piso_por_camada = math.ceil(area_externa / 1.15)

if "Resfriados" in temp_desejada:
    chapas_5cm, chapas_10cm = placas_piso_por_camada * 2, 0
elif "Congelados" in temp_desejada:
    chapas_5cm, chapas_10cm = placas_piso_por_camada, placas_piso_por_camada
else:
    chapas_5cm, chapas_10cm = 0, placas_piso_por_camada * 2

# ================= DINÂMICA DO KIT SUSTENTAÇÃO DE TETO (PERFIL T) =================
espessura_cm = round(espessura_teto * 100)

if espessura_cm in [7, 10]:
    limite_vau = 5.0
elif espessura_cm == 12 or (espessura_cm == 15 and isolamento == "EPS"):
    limite_vau = 6.0
else:
    limite_vau = 7.0

comprimento_vao_teto = larg_ext 
maior_sentido_camara = comp_ext

barras_de_6m = 0
barras_de_3m = 0

if comprimento_vao_teto > limite_vau:
    linhas_sustentacao = math.floor(comprimento_vao_teto / limite_vau)
    metragem_por_linha = maior_sentido_camara
    
    for _ in range(linhas_sustentacao):
        resto = metragem_por_linha
        while resto > 0:
            if resto > 3.0:
                barras_de_6m += 1
                resto -= 6.0
            elif resto > 0 and resto <= 3.0:
                barras_de_3m += 1
                resto -= 3.0

# ================= CÁLCULO DA VÁLVULA DE COMPENSAÇÃO =================
qtd_valvulas = math.floor(volume_interno / 150.0)

# ================= LOGICA DOS ACESSÓRIOS E PERFIS =================
trilho_inox_pcs = math.ceil(larg_p)
suporte_trilho_pcs = trilho_inox_pcs * 6

altura_tira = alt_p + 0.10
metragem_total_cortina = suporte_trilho_pcs * altura_tira  #  Muda para 'suporte'
metragem_comercial_cortina = math.ceil(metragem_total_cortina / 10.0) * 10

if espessura_cm in [7, 10]:
    modelo_cantoneira = "40 x 140"
elif espessura_cm in [12, 15]:
    modelo_cantoneira = "40 x 190"
else:
    modelo_cantoneira = "40 x 240"

perimetro_ext = (comp_ext * 2) + (larg_ext * 2)
metragem_cantoneira = perimetro_ext + (4 * alt_ext)
barras_cantoneira_ext = math.ceil(metragem_cantoneira / 3.0)
barras_cantoneira_int = barras_cantoneira_ext

vao_porta = (larg_p * 2) + (alt_p * 2)
metragem_perfil_u = perimetro_ext + vao_porta
barras_perfil_u = math.ceil(metragem_perfil_u / 3.0)

# REBRITES (12cm EM LINHA - PACOTES DE 1000 UN)
rebites_cantoneiras = metragem_cantoneira * 2 * (1.0 / 0.12 * 2)  
rebites_perfil_u = metragem_perfil_u * (1.0 / 0.12)  
total_rebites_unidades = (rebites_cantoneiras + rebites_perfil_u) * 1.15
pacotes_rebites = math.ceil(total_rebites_unidades / 1000.0)

total_metragem_perfis = (metragem_cantoneira * 2) + metragem_perfil_u
tubos_selante = math.ceil(total_metragem_perfis / 3.0)

# ENGENHARIA DE CÁLCULO DE SPRAY PU
perimetro_piso_int = (comp_int * 2) + (larg_int * 2)
juncoes_paineis_parede = total_paineis_parede * alt_painel
juncoes_paineis_teto = (total_paineis_teto - 1) * larg_ext if total_paineis_teto > 1 else 0
quinas_verticais_camara = 4 * alt_painel

metragem_total_frestas = perimetro_piso_int + juncoes_paineis_parede + juncoes_paineis_teto + quinas_verticais_camara
latas_frestas_geometrico = metragem_total_frestas / 25.0
latas_operacionais_obra = 3.0

spray_pu_pcs = math.ceil(latas_frestas_geometrico + latas_operacionais_obra)
if spray_pu_pcs < 3:
    spray_pu_pcs = 3

# QUANTIDADE DE ILUMINAÇÃO
luminarias_pcs = math.ceil(area_externa / 6.0)
if luminarias_pcs < 4:
    luminarias_pcs = 4

area_manta = (comp_ext + 0.5) * (larg_ext + 0.5)
rolos_manta = math.ceil(area_manta / 10.0)
baldes_hidroasfalto = math.ceil(rolos_manta / 3.0)
pecas_lona = math.ceil((area_externa * 2) / 20.0)

espessura_mm = espessura_cm * 10

# ================= ENGENHARIA DE ENERGIA E SELEÇÃO MATRIZADA =================
area_superficial = 2 * (comp_ext * larg_ext + comp_ext * alt_ext + larg_ext * alt_ext)
delta_t_ambiente = 43 - temp_interna_alvo 
carga_termica_estimada = (area_superficial * (coef_condutividade / espessura_teto) * delta_t_ambiente * 24 / 16) * 1.45

qtd_maquinas = 1
modelo_condensadora = "Não localizado"
modelo_evaporador = "Não localizado"
kcal_unitario_cond = 0
kcal_unitario_evap = 0

usa_gsmi = alt_ext <= 4.0 and "Sorvetes" not in temp_desejada

if "Resfriados" in temp_desejada:
    catalogo_danfoss_resf = [
        {"modelo": "OP-HJM019", "kcal": 1631}, {"modelo": "OP-HJM022", "kcal": 2263},
        {"modelo": "OP-HJM028", "kcal": 3581}, {"modelo": "OP-HJM032", "kcal": 3748},
        {"modelo": "OP-HJM036", "kcal": 4438}, {"modelo": "OP-HJM040", "kcal": 5096},
        {"modelo": "OP-HJM044", "kcal": 4965}, {"modelo": "OP-HJM050", "kcal": 5781},
        {"modelo": "OP-HJM056", "kcal": 6441}, {"modelo": "OP-HJM064", "kcal": 7303},
        {"modelo": "OP-HGM072", "kcal": 8581}, {"modelo": "OP-HGM080", "kcal": 9767},
        {"modelo": "OP-HGM100", "kcal": 10250}, {"modelo": "OP-HGM125", "kcal": 14430},
        {"modelo": "OP-HGM144", "kcal": 15980}, {"modelo": "OP-HGM160", "kcal": 17500}
    ]
    if usa_gsmi:
        catalogo_mipal_resf = [
            {"modelo": "GSMI13", "kcal": 1107}, {"modelo": "GSMI15", "kcal": 1387},
            {"modelo": "GSMI18", "kcal": 1579}, {"modelo": "GSMI25", "kcal": 2213},
            {"modelo": "GSMI31", "kcal": 2710}, {"modelo": "GSMI38", "kcal": 3318},
            {"modelo": "GSMI46", "kcal": 4051}, {"modelo": "GSMI51", "kcal": 4424},
            {"modelo": "GSMI62", "kcal": 5416}, {"modelo": "GSMI78", "kcal": 6781},
            {"modelo": "GSMI94", "kcal": 8106}, {"modelo": "GSMI110", "kcal": 9478},
            {"modelo": "GSMI125", "kcal": 10860}
        ]
    else:
        catalogo_mipal_resf = [
            {"modelo": "HDL31", "kcal": 2977}, {"modelo": "HDL38", "kcal": 3572},
            {"modelo": "HDL48", "kcal": 4584}, {"modelo": "HDL58", "kcal": 5501},
            {"modelo": "HDL64", "kcal": 6132}, {"modelo": "HDL77", "kcal": 7358},
            {"modelo": "HDL86", "kcal": 8156}, {"modelo": "HDL103", "kcal": 9787},
            {"modelo": "HDL129", "kcal": 12323}, {"modelo": "HDL155", "kcal": 14788},
            {"modelo": "HDL198", "kcal": 18871}, {"modelo": "HDL238", "kcal": 22646}
        ]

    for cond in catalogo_danfoss_resf:
        if cond["kcal"] >= carga_termica_estimada:
            modelo_condensadora = cond["modelo"]
            kcal_unitario_cond = cond["kcal"]
            break
            
    if kcal_unitario_cond == 0:
        qtd_maquinas = 2
        carga_fracionada = carga_termica_estimada / 2
        for cond in catalogo_danfoss_resf:
            if cond["kcal"] >= carga_fracionada:
                modelo_condensadora = cond["modelo"]
                kcal_unitario_cond = cond["kcal"]
                break

    carga_por_evap = carga_termica_estimada / qtd_maquinas
    for evap in catalogo_mipal_resf:
        if evap["kcal"] >= carga_por_evap:
            modelo_evaporador = evap["modelo"]
            kcal_unitario_evap = evap["kcal"]
            break
else:
    catalogo_danfoss_cong = [
        {"modelo": "OP-HJZ019", "kcal": 1141}, {"modelo": "OP-HJZ022", "kcal": 1333},
        {"modelo": "OP-HJZ028", "kcal": 2113}, {"modelo": "OP-HJZ032", "kcal": 2569},
        {"modelo": "OP-HJZ044", "kcal": 2659}, {"modelo": "OP-HJZ048", "kcal": 3317},
        {"modelo": "OP-HJZ068", "kcal": 3678}, {"modelo": "OP-HJZ086", "kcal": 4455},
        {"modelo": "OP-HJZ096", "kcal": 5090}, {"modelo": "OP-HJZ108", "kcal": 5812},
        {"modelo": "OP-HJZ121", "kcal": 5869}, {"modelo": "OP-HJZ136", "kcal": 8603},
        {"modelo": "OP-HJZ144", "kcal": 9648}, {"modelo": "OP-HJZ171", "kcal": 10660}
    ]
    if usa_gsmi:
        catalogo_mipal_cong = [
            {"modelo": "GSMI13", "kcal": 1015}, {"modelo": "GSMI15", "kcal": 1272},
            {"modelo": "GSMI18", "kcal": 1448}, {"modelo": "GSMI25", "kcal": 2029},
            {"modelo": "GSMI31", "kcal": 2485}, {"modelo": "GSMI38", "kcal": 3042},
            {"modelo": "GSMI46", "kcal": 3714}, {"modelo": "GSMI51", "kcal": 4057},
            {"modelo": "GSMI62", "kcal": 4966}, {"modelo": "GSMI78", "kcal": 6217},
            {"modelo": "GSMI94", "kcal": 7433}, {"modelo": "GSMI110", "kcal": 8691},
            {"modelo": "GSMI125", "kcal": 9958}
        ]
    else:
        catalogo_mipal_cong = [
            {"modelo": "HDL31", "kcal": 2375}, {"modelo": "HDL38", "kcal": 2849},
            {"modelo": "HDL48", "kcal": 3657}, {"modelo": "HDL58", "kcal": 4388},
            {"modelo": "HDL64", "kcal": 4892}, {"modelo": "HDL77", "kcal": 5870},
            {"modelo": "HDL86", "kcal": 6506}, {"modelo": "HDL103", "kcal": 7807},
            {"modelo": "HDL129", "kcal": 9830}, {"modelo": "HDL155", "kcal": 11797},
            {"modelo": "HDL198", "kcal": 15054}, {"modelo": "HDL238", "kcal": 18065}
        ]

    for cond in catalogo_danfoss_cong:
        if cond["kcal"] >= carga_termica_estimada:
            modelo_condensadora = cond["modelo"]
            kcal_unitario_cond = cond["kcal"]
            break
            
    if kcal_unitario_cond == 0:
        qtd_maquinas = 2
        carga_fracionada = carga_termica_estimada / 2
        for cond in catalogo_danfoss_cong:
            if cond["kcal"] >= carga_fracionada:
                modelo_condensadora = cond["modelo"]
                kcal_unitario_cond = cond["kcal"]
                break

    carga_por_evap = carga_termica_estimada / qtd_maquinas
    for evap in catalogo_mipal_cong:
        if evap["kcal"] >= carga_por_evap:
            modelo_evaporador = evap["modelo"]
            kcal_unitario_evap = evap["kcal"]
            break

# ================= ENGENHARIA DE DIÂMETRO DE TUBULAÇÕES =================
carga_por_conjunto = carga_termica_estimada / qtd_maquinas
bitola_succao = "1 1/8"
bitola_descarga = "1/2"

if "Resfriados" in temp_desejada:
    matriz_tubos = [
        (252, "3/8", "3/8"), (756, "1/2", "3/8"), (1008, "1/2", "3/8"), (1512, "5/8", "3/8"),
        (2268, "5/8", "3/8"), (3024, "7/8", "3/8"), (3780, "7/8", "3/8"), (4536, "7/8", "3/8"),
        (6048, "7/8", "3/8"), (7560, "1 1/8", "3/8"), (9072, "1 1/8", "1/2"), (10584, "1 1/8", "1/2"),
        (12096, "1 1/8", "1/2"), (13608, "1 3/8", "1/2"), (15120, "1 3/8", "1/2"), (16632, "1 3/8", "1/2"),
        (18144, "1 3/8", "1/2"), (19656, "1 3/8", "5/8"), (21168, "1 3/8", "5/8"), (22680, "1 3/8", "5/8"),
        (30240, "1 5/8", "7/8"), (37800, "1 5/8", "7/8"), (45360, "2 1/8", "7/8"), (52920, "2 1/8", "7/8"),
        (60480, "2 1/8", "7/8"), (75600, "2 1/8", "7/8"), (90720, "2 5/8", "7/8"), (120960, "2 5/8", "1 1/8"),
        (161200, "2 5/8", "1 1/8")
    ]
else:
    matriz_tubos = [
        (250, "3/8", "3/8"), (750, "1/2", "3/8"), (1000, "5/8", "3/8"), (1500, "5/8", "3/8"),
        (2250, "7/8", "3/8"), (3000, "7/8", "3/8"), (3750, "7/8", "3/8"), (4500, "7/8", "3/8"),
        (6000, "1 1/8", "3/8"), (7500, "1 1/8", "1/2"), (9000, "1 1/8", "1/2"), (10500, "1 3/8", "1/2"),
        (12000, "1 3/8", "1/2"), (13500, "1 3/8", "1/2"), (15000, "1 3/8", "1/2"), (16500, "1 5/8", "1/2"),
        (18000, "1 5/8", "1/2"), (19500, "1 5/8", "5/8"), (21000, "1 5/8", "5/8"), (22500, "1 5/8", "5/8"),
        (30000, "2 1/8", "5/8"), (37500, "2 1/8", "5/8"), (45000, "2 1/8", "7/8"), (52500, "2 1/8", "7/8"),
        (60000, "2 5/8", "7/8"), (75000, "2 5/8", "7/8"), (90000, "2 5/8", "7/8"), (120000, "3 1/8", "1 1/8"),
        (150000, "3 1/8", "1 1/8")
    ]

for limite_cap, suc, desc in matriz_tubos:
    if carga_por_conjunto <= limite_cap:
        bitola_succao = suc
        bitola_descarga = desc
        break

# ================= REGRAS DE CÁLCULO DE PORCAS =================
qtd_porca_38 = 1 * qtd_maquinas
if bitola_descarga == "3/8":
    qtd_porca_38 += 2 * qtd_maquinas

qtd_porca_12 = 1 * qtd_maquinas
if bitola_descarga == "1/2":
    qtd_porca_12 += 2 * qtd_maquinas

qtd_porca_58 = (2 * qtd_maquinas) + (1 * qtd_maquinas)

# ================= EXIBIÇÃO DOS RESULTADOS =================
with col_direita:
    st.header("2. Relatório Técnico de Materiais")
    
    st.info(f"""
    📐 **Dimensões Internas Úteis:** {comp_int:.2f}m (C) x {larg_int:.2f}m (L) x {alt_int:.2f}m (A)  
    📦 **Volume Interno Útil:** {volume_interno:.2f} m³  
    ⚡ **Carga Térmica de Projeto (Ambiente Ext: 43°C):** {carga_termica_estimada:.0f} Kcal/h  
    ⚖️ **Previsão de Estocagem:** {texto_estocagem}
    """)
    
    st.markdown("---")
    
    # ------------------ CONSOLIDAÇÃO DOS DADOS (TABELA ÚNICA) ------------------
    lista_consolidada_relatorio = []
    
    lista_consolidada_relatorio.append({"Item / Componente": "Painéis de Parede", "Quantidade": f"{total_paineis_parede} pçs", "Especificação / Detalhe": f"Espessura {espessura_teto:.2f}m | Altura {alt_painel:.2f}m"})
    lista_consolidada_relatorio.append({"Item / Componente": "Painéis de Teto", "Quantidade": f"{total_paineis_teto} pçs", "Especificação / Detalhe": f"Comprimento {comprimento_painel_teto:.2f}m"})
    if chapas_5cm > 0:
        lista_consolidada_relatorio.append({"Item / Componente": "Chapas de piso (EPS 5cm)", "Quantidade": f"{chapas_5cm} pçs", "Especificação / Detalhe": "Isolamento de Piso"})
    if chapas_10cm > 0:
        lista_consolidada_relatorio.append({"Item / Componente": "Chapas de piso (EPS 10cm)", "Quantidade": f"{chapas_10cm} pçs", "Especificação / Detalhe": "Isolamento de Piso"})
    lista_consolidada_relatorio.append({"Item / Componente": f"Porta Frigorífica {tamanho_porta}", "Quantidade": "1 pç", "Especificação / Detalhe": f"Modelo {detalhe_porta} | {resistencia_porta}"})
    
    lista_consolidada_relatorio.append({"Item / Componente": "Trilho Inox", "Quantidade": f"{trilho_inox_pcs} pç", "Especificação / Detalhe": "Acessório Porta"})
    lista_consolidada_relatorio.append({"Item / Componente": "Suporte de Trilho", "Quantidade": f"{suporte_trilho_pcs} pçs", "Especificação / Detalhe": "Acessório Porta"})
    lista_consolidada_relatorio.append({"Item / Componente": "Cortina Plástica Polar", "Quantidade": f"{metragem_comercial_cortina} m", "Especificação / Detalhe": "Proteção Térmica"})
    lista_consolidada_relatorio.append({"Item / Componente": f"Cantoneira Externa {modelo_cantoneira}", "Quantidade": f"{barras_cantoneira_ext} barras", "Especificação / Detalhe": "Acabamento Externo"})
    lista_consolidada_relatorio.append({"Item / Componente": "Cantoneira Interna 40 x 40", "Quantidade": f"{barras_cantoneira_int} barras", "Especificação / Detalhe": "Acabamento Interno"})
    lista_consolidada_relatorio.append({"Item / Componente": f"Perfil U 40 x {espessura_mm} x 40", "Quantidade": f"{barras_perfil_u} barras", "Especificação / Detalhe": "Perfil de Piso/Painel"})
    lista_consolidada_relatorio.append({"Item / Componente": "Rebite pacote 1000pç", "Quantidade": f"{pacotes_rebites} pac(s)", "Especificação / Detalhe": "Fixação de Perfis"})
    lista_consolidada_relatorio.append({"Item / Componente": "Selante PU", "Quantidade": f"{tubos_selante} tubos", "Especificação / Detalhe": "Vedação de Juntas"})
    lista_consolidada_relatorio.append({"Item / Componente": "Manta Asfáltica", "Quantidade": f"{rolos_manta} rolos", "Especificação / Detalhe": "Proteção Mecânica Piso"})
    lista_consolidada_relatorio.append({"Item / Componente": "Hydroasfalto", "Quantidade": f"{baldes_hidroasfalto} balde(s)", "Especificação / Detalhe": "Impermeabilização"})
    lista_consolidada_relatorio.append({"Item / Componente": "Lona Plástica", "Quantidade": f"{pecas_lona} pçs", "Especificação / Detalhe": "Barreira de Vapor"})
    lista_consolidada_relatorio.append({"Item / Componente": "Poliuretano Spray", "Quantidade": f"{spray_pu_pcs} pçs", "Especificação / Detalhe": "Isolamento de Frestas"})
    lista_consolidada_relatorio.append({"Item / Componente": "Luminária tartaruga", "Quantidade": f"{luminarias_pcs} pçs", "Especificação / Detalhe": "Iluminação Interna"})
    if barras_de_6m > 0:
        lista_consolidada_relatorio.append({"Item / Componente": "Kit sustentação de teto 6m", "Quantidade": f"{barras_de_6m} barras", "Especificação / Detalhe": "Perfil T Sustentação"})
    if barras_de_3m > 0:
        lista_consolidada_relatorio.append({"Item / Componente": "Kit sustentação de teto 3m", "Quantidade": f"{barras_de_3m} barras", "Especificação / Detalhe": "Perfil T Sustentação"})
    if qtd_valvulas > 0:
        lista_consolidada_relatorio.append({"Item / Componente": "Válvula de compensação", "Quantidade": f"{qtd_valvulas} pçs", "Especificação / Detalhe": "Alívio de Pressão"})
        
    lista_consolidada_relatorio.append({"Item / Componente": "Unidade Condensadora Danfoss", "Quantidade": f"{qtd_maquinas} x {modelo_condensadora}", "Especificação / Detalhe": f"Rendimento Ind: {kcal_unitario_cond} Kcal/h | Fluido: {tipo_gas}"})
    lista_consolidada_relatorio.append({"Item / Componente": f"Evaporador Mipal", "Quantidade": f"{qtd_maquinas} x {modelo_evaporador}", "Especificação / Detalhe": f"Rendimento Ind: {kcal_unitario_evap} Kcal/h"})

    valv_exp_modelo = "TEX2 (Danfoss)" if tipo_gas == "R22" else "TES2 (Danfoss)"
    tubo_elastom_espessura = "19mm" if "Resfriados" in temp_desejada else "25mm"
    oleo_sugerido = "160P (Mineral)" if tipo_gas == "R22" else "160PZ (POE)"

    lista_consolidada_relatorio.extend([
        {"Item / Componente": "Resistências de Degelo", "Quantidade": f"{qtd_maquinas} Kit(s)", "Especificação / Detalhe": "Kit original p/ evaporador"},
        {"Item / Componente": "Válvula de Expansão Termostática", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação / Detalhe": f"Modelo {valv_exp_modelo}"},
        {"Item / Componente": "Orifício de Expansão", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação / Detalhe": "Orifício técnico calibrado (0 a 6)"},
        {"Item / Componente": "Porca Flare 1/4\"", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação / Detalhe": "Conexão de equalização"},
        {"Item / Componente": "Porca Flare 3/8\"", "Quantidade": f"{qtd_porca_38} pç(s)", "Especificação / Detalhe": "Linha de líquido / Válvula"},
        {"Item / Componente": "Porca Flare 1/2\"", "Quantidade": f"{qtd_porca_12} pç(s)", "Especificação / Detalhe": "Linha de descarga / Válvula"},
        {"Item / Componente": "Porca Flare 5/8\"", "Quantidade": f"{qtd_porca_58} pç(s)", "Especificação / Detalhe": "Conexões unificadas"},
        {"Item / Componente": "Cobre Tubo Sucção (Isolado)", "Quantidade": f"{(15 * qtd_maquinas)} m", "Especificação / Detalhe": f"Bitola de {bitola_succao}\""},
        {"Item / Componente": "Cobre Tubo Descarga / Líquido", "Quantidade": f"{(15 * qtd_maquinas)} m", "Especificação / Detalhe": f"Bitola de {bitola_descarga}\""},
        {"Item / Componente": "Tubo Isolante Elastomérico", "Quantidade": f"{(8 * qtd_maquinas * 2)} m", "Especificação / Detalhe": f"Parede {tubo_elastom_espessura} | Bitola {bitola_succao}\""},
        {"Item / Componente": "Visor de Líquido", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação / Detalhe": "Integrado de fábrica na UC Danfoss"},
        {"Item / Componente": "Filtro Secador", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação / Detalhe": "Integrado de fábrica na UC Danfoss"},
        {"Item / Componente": "Válvula Solenoide de Líquido", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação / Detalhe": f"Rosca na bitola {bitola_descarga}\""},
        {"Item / Componente": "Bobina para Válvula Solenoide", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação / Detalhe": "Compatível com quadro"},
        {"Item / Componente": "Curva de Cobre 90° - Sucção", "Quantidade": f"{(5 * qtd_maquinas)} pçs", "Especificação / Detalhe": f"Bitola {bitola_succao}\""},
        {"Item / Componente": "Curva de Cobre 90° - Descarga", "Quantidade": f"{(5 * qtd_maquinas)} pçs", "Especificação / Detalhe": f"Bitola {bitola_descarga}\""},
        {"Item / Componente": "Luva de Cobre - Sucção", "Quantidade": f"{(3 * qtd_maquinas)} pçs", "Especificação / Detalhe": f"Bitola {bitola_succao}\""},
        {"Item / Componente": "Luva de Cobre - Descarga", "Quantidade": f"{(3 * qtd_maquinas)} pçs", "Especificação / Detalhe": f"Bitola {bitola_descarga}\""},
        {"Item / Componente": "Sifão de Cobre", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação / Detalhe": f"Saída do Evaporador | Bitola {bitola_succao}\""},
        {"Item / Componente": "Fita Plástica PVC (Branca)", "Quantidade": f"{(10 * qtd_maquinas)} rolos", "Especificação / Detalhe": "Proteção do isolamento"},
        {"Item / Componente": "Quadro de Comando Elétrico", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação / Detalhe": "Controlador digital integrado"},
        {"Item / Componente": "Calço Amortecedor de Borracha", "Quantidade": f"{(4 * qtd_maquinas)} pçs", "Especificação / Detalhe": "Pés da condensadora"},
        {"Item / Componente": "Suporte Metálico Condensadora", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação / Detalhe": "Fixação robusta em perfil U"},
        {"Item / Componente": "Canaleta de Acabamento", "Quantidade": f"{(2 * qtd_maquinas)} pçs", "Especificação / Detalhe": "Proteção física de fiação"},
        {"Item / Componente": "Cabo Elétrico PP - Ventiladores", "Quantidade": f"{(25 * qtd_maquinas)} m", "Especificação / Detalhe": "Cabo PP 4 x 1.5 mm²"},
        {"Item / Componente": "Cabo Elétrico PP - Resistências", "Quantidade": f"{(25 * qtd_maquinas)} m", "Especificação / Detalhe": "Cabo PP 4 x 2.5 mm²"},
        {"Item / Componente": "Cabo Elétrico PP - Força Geral", "Quantidade": f"{(25 * qtd_maquinas)} m", "Especificação / Detalhe": "Cabo PP 4 x 4.0 mm²"},
        {"Item / Componente": "Cabo Elétrico PP - Iluminação", "Quantidade": f"{(25 * qtd_maquinas)} m", "Especificação / Detalhe": "Cabo PP 2 x 1.5 mm²"},
        {"Item / Componente": "Gás / Fluido Refrigerante", "Quantidade": f"{qtd_maquinas} cil", "Especificação / Detalhe": f"Carga original {tipo_gas}"},
        {"Item / Componente": "Óleo Lubrificante Frigorífico", "Quantidade": f"{qtd_maquinas} L", "Especificação / Detalhe": f"Tipo {oleo_sugerido}"},
        {"Item / Componente": "Solda Foscoper / Prata", "Quantidade": f"{(0.5 * qtd_maquinas):.1f} Kg", "Especificação / Detalhe": "Varetas para brasagem"},
        {"Item / Componente": "Fluxo para Solda", "Quantidade": "1 pote", "Especificação / Detalhe": "Decapante químico"},
        {"Item / Componente": "Carga de Gás MAP", "Quantidade": f"{(3 * qtd_maquinas)} pçs", "Especificação / Detalhe": "Cilindro descartável p/ maçarico"}
    ])

    st.markdown("### 📊 Listagem Unificada de Materiais e Insumos")
    st.table(lista_consolidada_relatorio)

    st.markdown("---")

    # ------------------ SISTEMA DE IMPRESSÃO CROSS-ORIGIN (CORRIGIDO) ------------------
    st.markdown("### 🖨️ Exportar Orçamento")

    # Injeção de estilo CSS avançado focado em omitir barras laterais, botões e cabeçalhos na folha de papel
    st.markdown("""
        <style>
        @media print {
            div[data-testid="stSidebar"] { display: none !important; }
            div[data-testid="stHeader"] { display: none !important; }
            footer { display: none !important; }
            .main .block-container { padding-top: 0rem !important; max-width: 100% !important; }
            iframe { display: none !important; } /* Esconde o próprio frame do botão no papel */
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<p style='margin-bottom: 15px;'>Clique abaixo para acionar a impressão completa ou salvar em PDF:</p>", unsafe_allow_html=True)
    
    # Executa um componente de script isolado que contorna o bloqueio do iframe do Streamlit Cloud chamando a janela "mãe" (parent)
    st.components.v1.html("""
        <style>
        .print-btn {
            background-color: #ff4b4b;
            color: white !important;
            padding: 12px 24px;
            text-align: center;
            font-size: 16px;
            cursor: pointer;
            border-radius: 8px;
            border: none;
            font-weight: bold;
            width: 100%;
            font-family: sans-serif;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        }
        .print-btn:hover { background-color: #ff3333; }
        </style>
        <button class="print-btn" onclick="window.parent.print()">🖨️ Imprimir / Salvar Relatório Completo como PDF</button>
    """, height=60)

    st.info("💡 **Dica da Frigelar:** Escolha a opção **'Salvar como PDF'** nas configurações da sua impressora para gerar o arquivo digital comercial.")