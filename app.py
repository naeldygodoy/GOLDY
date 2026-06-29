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
metragem_total_cortina = suporte_trilho_pcs * altura_tira
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
    
    # ------------------ CONSOLIDAÇÃO DOS DADOS (TABELA COMERCIAL) ------------------
    lista_consolidada_relatorio = []
    
    lista_consolidada_relatorio.append({"Quantidade": f"{total_paineis_parede} pçs", "Descrição do Item": f"Painéis de Parede - Espessura {espessura_teto:.2f}m | Altura {alt_painel:.2f}m"})
    lista_consolidada_relatorio.append({"Quantidade": f"{total_paineis_teto} pçs", "Descrição do Item": f"Painéis de Teto - Comprimento {comprimento_painel_teto:.2f}m"})
    
    if chapas_5cm > 0:
        lista_consolidada_relatorio.append({"Quantidade": f"{chapas_5cm} pçs", "Descrição do Item": "Chapas de piso (EPS 5cm) - Isolamento de Piso"})
    if chapas_10cm > 0:
        lista_consolidada_relatorio.append({"Quantidade": f"{chapas_10cm} pçs", "Descrição do Item": "Chapas de piso (EPS 10cm) - Isolamento de Piso"})
        
    lista_consolidada_relatorio.append({"Quantidade": "1 pç", "Descrição do Item": f"Porta Frigorífica {tamanho_porta} - Modelo {detalhe_porta} | {resistencia_porta}"})
    lista_consolidada_relatorio.append({"Quantidade": f"{trilho_inox_pcs} pç", "Descrição do Item": "Trilho Inox - Acessório Porta"})
    lista_consolidada_relatorio.append({"Quantidade": f"{suporte_trilho_pcs} pçs", "Descrição do Item": "Suporte de Trilho - Acessório Porta"})
    lista_consolidada_relatorio.append({"Quantidade": f"{metragem_comercial_cortina} m", "Descrição do Item": "Cortina Plástica Polar - Proteção Térmica"})
    lista_consolidada_relatorio.append({"Quantidade": f"{barras_cantoneira_ext} barras", "Descrição do Item": f"Cantoneira Externa {modelo_cantoneira} - Acabamento Externo"})
    lista_consolidada_relatorio.append({"Quantidade": f"{barras_cantoneira_int} barras", "Descrição do Item": "Cantoneira Interna 40 x 40 - Acabamento Interno"})
    lista_consolidada_relatorio.append({"Quantidade": f"{barras_perfil_u} barras", "Descrição do Item": f"Perfil U 40 x {espessura_mm} x 40 - Perfil de Piso/Painel"})
    lista_consolidada_relatorio.append({"Quantidade": f"{pacotes_rebites} pac(s)", "Descrição do Item": "Rebite pacote 1000pç - Fixação de Perfis"})
    lista_consolidada_relatorio.append({"Quantidade": f"{tubos_selante} tubos", "Descrição do Item": "Selante PU - Vedação de Juntas"})
    lista_consolidada_relatorio.append({"Quantidade": f"{rolos_manta} rolos", "Descrição do Item": "Manta Asfáltica - Proteção Mecânica Piso"})
    lista_consolidada_relatorio.append({"Quantidade": f"{baldes_hidroasfalto} balde(s)", "Descrição do Item": "Hydroasfalto - Impermeallização"})
    lista_consolidada_relatorio.append({"Quantidade": f"{pecas_lona} pçs", "Descrição do Item": "Lona Plástica - Barreira de Vapor"})
    lista_consolidada_relatorio.append({"Quantidade": f"{spray_pu_pcs} pçs", "Descrição do Item": "Poliuretano Spray - Isolamento de Frestas"})
    lista_consolidada_relatorio.append({"Quantidade": f"{luminarias_pcs} pçs", "Descrição do Item": "Luminária tartaruga - Iluminação Interna"})
    
    if barras_de_6m > 0:
        lista_consolidada_relatorio.append({"Quantidade": f"{barras_de_6m} barras", "Descrição do Item": "Kit sustentação de teto 6m - Perfil T Sustentação"})
    if barras_de_3m > 0:
        lista_consolidada_relatorio.append({"Quantidade": f"{barras_de_3m} barras", "Descrição do Item": "Kit sustentação de teto 3m - Perfil T Sustentação"})
    if qtd_valvulas > 0:
        lista_consolidada_relatorio.append({"Quantidade": f"{qtd_valvulas} pçs", "Descrição do Item": "Válvula de compensação - Alívio de Pressão"})
        
    lista_consolidada_relatorio.append({"Quantidade": f"{qtd_maquinas} x {modelo_condensadora}", "Descrição do Item": f"Unidade Condensadora Danfoss - Rendimento Ind: {kcal_unitario_cond} Kcal/h | Fluido: {tipo_gas}"})
    lista_consolidada_relatorio.append({"Quantidade": f"{qtd_maquinas} x {modelo_evaporador}", "Descrição do Item": f"Evaporador Mipal - Rendimento Ind: {kcal_unitario_evap} Kcal/h"})

    valv_exp_modelo = "TEX2 (Danfoss)" if tipo_gas == "R22" else "TES2 (Danfoss)"
    tubo_elastom_espessura = "19mm" if "Resfriados" in temp_desejada else "25mm"
    oleo_sugerido = "160P (Mineral)" if tipo_gas == "R22" else "160PZ (POE)"

    lista_consolidada_relatorio.extend([
        {"Quantidade": f"{qtd_maquinas} Kit(s)", "Descrição do Item": "Resistências de Degelo - Kit original p/ evaporador"},
        {"Quantidade": f"{qtd_maquinas} pç(s)", "Descrição do Item": f"Válvula de Expansão Termostática - Modelo {valv_exp_modelo}"},
        {"Quantidade": f"{qtd_maquinas} pç(s)", "Descrição do Item": "Orifício de Expansão - Orifício técnico calibrado (0 a 6)"},
        {"Quantidade": f"{qtd_maquinas} pç(s)", "Descrição do Item": "Porca Flare 1/4\" - Conexão de equalização"},
        {"Quantidade": f"{qtd_porca_38} pç(s)", "Descrição do Item": "Porca Flare 3/8\" - Linha de líquido / Válvula"},
        {"Quantidade": f"{qtd_porca_12} pç(s)", "Descrição do Item": "Porca Flare 1/2\" - Linha de descarga / Válvula"},
        {"Quantidade": f"{qtd_porca_58} pç(s)", "Descrição do Item": "Porca Flare 5/8\" - Conexões unificadas"},
        {"Quantidade": f"{(15 * qtd_maquinas)} m", "Descrição do Item": f"Cobre Tubo Sucção (Isolado) - Bitola de {bitola_succao}\""},
        {"Quantidade": f"{(15 * qtd_maquinas)} m", "Descrição do Item": f"Cobre Tubo Descarga / Líquido - Bitola de {bitola_descarga}\""},
        {"Quantidade": f"{(8 * qtd_maquinas * 2)} m", "Descrição do Item": f"Tubo Isolante Elastomérico - Parede {tubo_elastom_espessura} | Bitola {bitola_succao}\""},
        {"Quantidade": f"{qtd_maquinas} pç(s)", "Descrição do Item": "Visor de Líquido - Integrado de fábrica na UC Danfoss"},
        {"Quantidade": f"{qtd_maquinas} pç(s)", "Descrição do Item": "Filtro Secador - Integrado de fábrica na UC Danfoss"},
        {"Quantidade": f"{qtd_maquinas} pç(s)", "Descrição do Item": f"Válvula Solenoide de Líquido - Rosca na bitola {bitola_descarga}\""},
        {"Quantidade": f"{qtd_maquinas} pç(s)", "Descrição do Item": "Bobina para Válvula Solenoide - Compartível com quadro"},
        {"Quantidade": f"{(5 * qtd_maquinas)} pçs", "Descrição do Item": f"Curva de Cobre 90° - Sucção - Bitola {bitola_succao}\""},
        {"Quantidade": f"{(5 * qtd_maquinas)} pçs", "Descrição do Item": f"Curva de Cobre 90° - Descarga - Bitola {bitola_descarga}\""},
        {"Quantidade": f"{(3 * qtd_maquinas)} pçs", "Descrição do Item": "Luva de Cobre - Sucção - Bitola " + bitola_succao + "\""},
        {"Quantidade": f"{(3 * qtd_maquinas)} pçs", "Descrição do Item": "Luva de Cobre - Descarga - Bitola " + bitola_descarga + "\""},
        {"Quantidade": f"{qtd_maquinas} pç(s)", "Descrição do Item": f"Sifão de Cobre - Saída do Evaporador | Bitola {bitola_succao}\""},
        {"Quantidade": f"{(10 * qtd_maquinas)} rolos", "Descrição do Item": "Fita Plástica PVC (Branca) - Proteção do isolamento"},
        {"Quantidade": f"{qtd_maquinas} pç(s)", "Descrição do Item": "Quadro de Comando Elétrico - Controlador digital integrado"},
        {"Quantidade": f"{(4 * qtd_maquinas)} pçs", "Descrição do Item": "Calço Amortecedor de Borracha - Pés da condensadora"},
        {"Quantidade": f"{qtd_maquinas} pç(s)", "Descrição do Item": "Suporte Metálico Condensadora - Fixação robusta em perfil U"},
        {"Quantidade": f"{(2 * qtd_maquinas)} pçs", "Descrição do Item": "Canaleta de Acabamento - Proteção física de fiação"},
        {"Quantidade": f"{(25 * qtd_maquinas)} m", "Descrição do Item": "Cabo Elétrico PP - Ventiladores - Cabo PP 4 x 1.5 mm²"},
        {"Quantidade": f"{(25 * qtd_maquinas)} m", "Descrição do Item": "Cabo Elétrico PP - Resistências - Cabo PP 4 x 2.5 mm²"},
        {"Quantidade": f"{(25 * qtd_maquinas)} m", "Descrição do Item": "Cabo Elétrico PP - Força Geral - Cabo PP 4 x 4.0 mm²"},
        {"Quantidade": f"{(25 * qtd_maquinas)} m", "Descrição do Item": "Cabo Elétrico PP - Iluminação - Cabo PP 2 x 1.5 mm²"},
        {"Quantidade": f"{qtd_maquinas} cil", "Descrição do Item": f"Gás / Fluido Refrigerante - Carga original {tipo_gas}"},
        {"Quantidade": f"{qtd_maquinas} L", "Descrição do Item": f"Óleo Lubrificante Frigorífico - Tipo {oleo_sugerido}"},
        {"Quantidade": f"{(0.5 * qtd_maquinas):.1f} Kg", "Descrição do Item": "Solda Foscoper / Prata - Varetas para brasagem"},
        {"Quantidade": "1 pote", "Descrição do Item": "Fluxo para Solda - Decapante químico"},
        {"Quantidade": f"{(3 * qtd_maquinas)} pçs", "Descrição do Item": "Carga de Gás MAP - Cilindro descartável p/ maçarico"}
    ])

    # ------------------ SISTEMA DE IMPRESSÃO VIA VISIBILITY (CORREÇÃO DE PÁGINA EM BRANCO) ------------------
    st.markdown("""
        <style>
        /* Estilos normais da aplicação */
        .print-only-title {
            display: none;
            font-family: sans-serif;
            text-align: center;
            margin-bottom: 20px;
        }
        
        /* Regras de Impressão via Visibility */
        @media print {
            /* 1. Esconde visualmente toda a árvore da aplicação mas mantém os espaços e containers ativos */
            html, body, .stApp, [data-testid="stAppViewContainer"], 
            [data-testid="stMain"], [data-testid="stMainSpaceBlockContainer"],
            [data-testid="column"], [data-testid="stVerticalBlock"] {
                visibility: hidden !important;
                background: white !important;
            }
            
            /* 2. Força apenas a div de conteúdo comercial a ficar visível e flutuar para o topo da folha */
            .printable-content, .printable-content * {
                visibility: visible !important;
            }
            
            .printable-content {
                position: absolute !important;
                left: 0 !important;
                top: 0 !important;
                width: 100% !important;
            }
            
            /* 3. Ativa e estiliza o título exclusivo de impressão */
            .print-only-title {
                display: block !important;
                font-family: sans-serif !important;
                font-size: 20px !important;
                font-weight: bold !important;
                text-align: center !important;
                color: #000 !important;
                margin-top: 0px !important;
                margin-bottom: 25px !important;
            }

            /* 4. Formatação e compactação fina da tabela para folha A4 */
            .printable-content table {
                width: 100% !important;
                font-size: 11px !important;
                border-collapse: collapse !important;
            }
            
            .printable-content th, .printable-content td {
                padding: 5px 8px !important;
                border: 1px solid #333 !important;
                color: #000 !important;
            }
            
            .printable-content th {
                background-color: #f2f2f2 !important;
                font-weight: bold !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🖨️ Exportar Orçamento")
    st.markdown("<div class='print-instruction'><p>Utilize o botão verde abaixo. A nova lógica de isolamento impede telas brancas na pré-visualização e imprime apenas os materiais:</p></div>", unsafe_allow_html=True)
    
    # Botão de gatilho de impressão atualizado
    st.components.v1.html("""
        <style>
        .print-btn {
            background-color: #28a745;
            color: white !important;
            padding: 14px 28px;
            text-align: center;
            font-size: 16px;
            cursor: pointer;
            border-radius: 6px;
            border: none;
            font-weight: bold;
            width: 100%;
            font-family: sans-serif;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        }
        .print-btn:hover { background-color: #218838; }
        </style>
        <button class="print-btn" onclick="window.parent.print()">🖨️ Imprimir Listagem Unificada</button>
    """, height=60)

    # Encapsulamento da área comercial
    st.markdown("<div class='printable-content'>", unsafe_allow_html=True)
    st.markdown("<div class='print-only-title'>Listagem Unificada de Materiais e Insumos</div>", unsafe_allow_html=True)
    
    # Renderização da tabela de dados comercial
    st.table(lista_consolidada_relatorio)
    st.markdown("</div>", unsafe_allow_html=True)

    st.info("💡 **Configuração de Layout:** Certifique-se de manter as margens como **'Padrão'** nas configurações da sua impressora para o perfeito ajuste das colunas.")