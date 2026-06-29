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
    texto_estocagem = f"**{estocagem_ton:.2f} Toneladas**"
elif "Congelados" in temp_desejada:
    estocagem_ton = (volume_interno * 400 * 0.8) / 1000
    texto_estocagem = f"**{estocagem_ton:.2f} Toneladas**"
else:
    texto_estocagem = "⚠️ **Definir conforme movimentação**"

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

# ENGENHARIA DE CÁLCULO DE SPRAY PU (GEOMÉTRICO)
perimetro_piso_int = (comp_int * 2) + (larg_int * 2)
juncoes_paineis_parede = total_paineis_parede * alt_painel
juncoes_paineis_teto = (total_paineis_teto - 1) * larg_ext if total_paineis_teto > 1 else 0
quinas_verticais_camara = 4 * alt_painel

metragem_total_frestas = perimetro_piso_int + juncoes_paineis_parede + juncoes_paineis_teto + quinas_verticais_camara
latas_frestas_geometrico = metragem_total_frestas / 25.0
latas_operacionais_obra = 1.0 + 1.0 + 1.0

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
# Estimativa de Carga Térmica considerando o ambiente severo de 43ºC externo
area_superficial = 2 * (comp_ext * larg_ext + comp_ext * alt_ext + larg_ext * alt_ext)
delta_t_ambiente = 43 - temp_interna_alvo 
carga_termica_estimada = (area_superficial * (coef_condutividade / espessura_teto) * delta_t_ambiente * 24 / 16) * 1.45

# Inicialização de variáveis de controle de equipamentos
qtd_maquinas = 1
modelo_condensadora = "Não localizado"
modelo_evaporador = "Não localizado"
kcal_unitario_cond = 0
kcal_unitario_evap = 0

# Determinação do perfil técnico pela altura (Até 4 metros de altura externa utiliza a linha GSMI)
usa_gsmi = alt_ext <= 4.0 and "Sorvetes" not in temp_desejada

if "Resfriados" in temp_desejada:
    # ------------------ REGIME DE RESFRIADOS (-10°C, R22, Amb 43°C) ------------------
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
    # ------------------ REGIME DE CONGELADOS (-25°C, R404A, Amb 43°C) ------------------
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

# ================= ENGENHERIA DE DIÂMETRO DE TUBULAÇÕES (MECÂNICA) =================
# Carga por conjunto individual para fins de dimensionamento de tubulação
carga_por_conjunto = carga_termica_estimada / qtd_maquinas

# Inicialização padrão de segurança
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
# PORCA 3/8: 1pç por válvula + 2pç adicionais se descarga for 3/8
qtd_porca_38 = 1 * qtd_maquinas
if bitola_descarga == "3/8":
    qtd_porca_38 += 2 * qtd_maquinas

# PORCA 1/2: 1pç por válvula + 2pç adicionais se descarga for 1/2
qtd_porca_12 = 1 * qtd_maquinas
if bitola_descarga == "1/2":
    qtd_porca_12 += 2 * qtd_maquinas

# PORCA 5/8: Regulamento fixo de 2pç por máquina + 1pç se válvula for TE2 (Sempre é TE2 por padrão atual)
qtd_porca_58 = (2 * qtd_maquinas) + (1 * qtd_maquinas)

# ================= EXIBIÇÃO DOS RESULTADOS =================
with col_direita:
    # ------------------ 2. RELATÓRIO TÉCNICO DE MATERIAIS ------------------
    st.header("2. Relatório Técnico de Materiais")
    
    st.info(f"""
    📐 **Dimensões Internas Úteis:** {comp_int:.2f}m (C) x {larg_int:.2f}m (L) x {alt_int:.2f}m (A)  
    📦 **Volume Interno Útil:** {volume_interno:.2f} m³  
    ⚡ **Carga Térmica de Projeto (Ambiente Ext: 43°C):** {carga_termica_estimada:.0f} Kcal/h  
    ⚖️ **Previsão de Estocagem:** {texto_estocagem}
    """)
    
    st.markdown("---")
    
    # ------------------ 3. LISTA DE MATERIAIS (ISOLAMENTO) ------------------
    st.markdown("### 📋 3. Lista de Materiais (Isolamento)")
    
    dados_tabela = [
        {"Item": "Total de painéis de parede", "Quantidade": f"{total_paineis_parede} pçs", "Descrição": f"Painéis de {alt_painel:.2f}m x {larg_modulo:.2f}m x {espessura_teto:.2f}m"},
        {"Item": "Total de painéis de teto", "Quantidade": f"{total_paineis_teto} pçs", "Descrição": f"Painéis de {comprimento_painel_teto:.2f}m x {larg_modulo:.2f}m x {espessura_teto:.2f}m"}
    ]
    
    if chapas_5cm > 0:
        dados_tabela.append({"Item": "Total de chapas de piso (EPS 5cm)", "Quantidade": f"{chapas_5cm} pçs", "Descrição": "Chapas de 1,15m x 1,00m x 0,05m"})
    if chapas_10cm > 0:
        dados_tabela.append({"Item": "Total de chapas de piso (EPS 10cm)", "Quantidade": f"{chapas_10cm} pçs", "Descrição": "Chapas de 1,15m x 1,00m x 0,10m"})
        
    dados_tabela.append({"Item": f"Porta Frigorífica {tamanho_porta}", "Quantidade": "1 pç", "Descrição": f"Modelo {detalhe_porta} | {resistencia_porta}"})
    
    st.table(dados_tabela)
    
    st.markdown("#### Acessórios de Isolamento e Portas")
    
    tabela_acessorios = [
        {"Item": "Trilho Inox", "Quantidade": f"{trilho_inox_pcs} pç"},
        {"Item": "Suporte de Trilho", "Quantidade": f"{suporte_trilho_pcs} pçs"},
        {"Item": "Cortina Plástica Polar", "Quantidade": f"{metragem_comercial_cortina} metros"},
        {"Item": f"Cantoneira Externa {modelo_cantoneira}", "Quantidade": f"{barras_cantoneira_ext} barras"},
        {"Item": "Cantoneira Interna 40 x 40", "Quantidade": f"{barras_cantoneira_int} barras"},
        {"Item": f"Perfil U 40 x {espessura_mm} x 40", "Quantidade": f"{barras_perfil_u} barras"},
        {"Item": "Rebite pacote 1000pç", "Quantidade": f"{pacotes_rebites} pacote(s)"},
        {"Item": "Selante PU", "Quantidade": f"{tubos_selante} tubos"},
        {"Item": "Manta Asfáltica", "Quantidade": f"{rolos_manta} rolos"},
        {"Item": "Hydroasfalto", "Quantidade": f"{baldes_hidroasfalto} balde(s)"},
        {"Item": "Lona Plástica", "Quantidade": f"{pecas_lona} pçs"},
        {"Item": "Poliuretano Spray", "Quantidade": f"{spray_pu_pcs} pçs"},
        {"Item": "Luminária tartaruga", "Quantidade": f"{luminarias_pcs} pçs"},
    ]
    
    if barras_de_6m > 0:
        tabela_acessorios.append({"Item": "Kit sustentação de teto 6m", "Quantidade": f"{barras_de_6m} barras"})
    if barras_de_3m > 0:
        tabela_acessorios.append({"Item": "Kit sustentação de teto 3m", "Quantidade": f"{barras_de_3m} barras"})
        
    if qtd_valvulas > 0:
        tabela_acessorios.append({"Item": "Válvula de compensação", "Quantidade": f"{qtd_valvulas} pçs"})
        
    st.table(tabela_acessorios)
    
    # ------------------ 4. DIMENSIONAMENTO DE EQUIPAMENTOS ------------------
    st.markdown("### ⚙️ 4. Dimensionamento de Equipamentos")
    
    if qtd_maquinas > 1:
        st.warning(f"⚠️ O projeto foi dividido em **{qtd_maquinas} circuitos mecânicos independentes** de **{carga_por_conjunto:.0f} Kcal/h** cada para garantir maior segurança operacional.")
    
    tabela_equipamentos = [
        {
            "Componente": "Unidade Condensadora Danfoss",
            "Modelo Sugerido": f"{qtd_maquinas}x {modelo_condensadora}",
            "Rendimento Individual": f"{kcal_unitario_cond} Kcal/h",
            "Capacidade Total do Kit": f"{(kcal_unitario_cond * qtd_maquinas)} Kcal/h",
            "Detalhe de Operação": f"Evaporação: {evap_alvo} | Fluido: {tipo_gas}"
        },
        {
            "Componente": f"Evaporador Mipal ({'Linha GSMI' if usa_gsmi else 'Linha HDL'})",
            "Modelo Sugerido": f"{qtd_maquinas}x {modelo_evaporador}",
            "Rendimento Individual": f"{kcal_unitario_evap} Kcal/h",
            "Capacidade Total do Kit": f"{(kcal_unitario_evap * qtd_maquinas)} Kcal/h",
            "Detalhe de Operação": f"Ideal para pé-direito {'até 4.0m (Baixo Perfil)' if usa_gsmi else 'acima de 4.0m (Médio Perfil)'} | Motores AC"
        }
    ]
    
    st.table(tabela_equipamentos)
    
    # ------------------ 5. ACESSÓRIOS DOS EQUIPAMENTOS ------------------
    st.markdown("### 🔧 5. Acessórios dos Equipamentos (Instalação Mecânica)")
    
    valv_exp_modelo = "TEX2 (Danfoss)" if tipo_gas == "R22" else "TES2 (Danfoss)"
    tubo_elastom_espessura = "19mm" if "Resfriados" in temp_desejada else "25mm"
    oleo_sugerido = "160P (Mineral)" if tipo_gas == "R22" else "160PZ (POE)"
    
    tabela_acessorios_mecanicos = [
        {"Componente / Insumo": "Resistências de Degelo", "Quantidade": f"{qtd_maquinas} Kit(s)", "Especificação": "Kit original para o evaporador Mipal selecionado"},
        {"Componente / Insumo": "Válvula de Expansão Termostática", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação": f"Modelo {valv_exp_modelo} com equalização externa"},
        {"Componente / Insumo": "Orifício de Expansão", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação": f"Orifício técnico calibrado (Linha 0 a 6) conforme capacidade"},
        {"Componente / Insumo": "Porca Flare 1/4\"", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação": "Para conexão de equalização da válvula de expansão"},
        {"Componente / Insumo": "Porca Flare 3/8\"", "Quantidade": f"{qtd_porca_38} pç(s)", "Especificação": "Entrada da válvula / Linha de líquido conforme bitola"},
        {"Componente / Insumo": "Porca Flare 1/2\"", "Quantidade": f"{qtd_porca_12} pç(s)", "Especificação": "Saída da válvula / Linha de descarga conforme bitola"},
        {"Componente / Insumo": "Porca Flare 5/8\"", "Quantidade": f"{qtd_porca_58} pç(s)", "Especificação": "2 por máquina + 1 por válvula TE2 unificada"},
        {"Componente / Insumo": "Cobre Tubo Sucção (Isolado)", "Quantidade": f"{(15 * qtd_maquinas)} metros", "Especificação": f"Tubulação rígida/panqueca na bitola de **{bitola_succao}\"**"},
        {"Componente / Insumo": "Cobre Tubo Descarga / Líquido", "Quantidade": f"{(15 * qtd_maquinas)} metros", "Especificação": f"Tubulação frigorífica na bitola de **{bitola_descarga}\"**"},
        {"Componente / Insumo": "Tubo Isolante Elastomérico", "Quantidade": f"{(8 * qtd_maquinas * 2)} metros", "Especificação": f"Parede de {tubo_elastom_espessura} | Múltiplos de 2m na bitola da sucção ({bitola_succao}\")"},
        {"Componente / Insumo": "Visor de Líquido", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação": "⚠️ Integrado de fábrica na Unidade Condensadora Danfoss"},
        {"Componente / Insumo": "Filtro Secador", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação": "⚠️ Integrado de fábrica na Unidade Condensadora Danfoss"},
        {"Componente / Insumo": "Válvula Solenoide de Líquido", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação": f"Conexão de rosca na bitola da descarga (**{bitola_descarga}\"**)"},
        {"Componente / Insumo": "Bobina para Válvula Solenoide", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação": "Compatível com a tensão do quadro de comando"},
        {"Componente / Insumo": "Curva de Cobre 90° - Sucção", "Quantidade": f"{(5 * qtd_maquinas)} pçs", "Especificação": f"Bitola de **{bitola_succao}\"** para raio longo"},
        {"Componente / Insumo": "Curva de Cobre 90° - Descarga", "Quantidade": f"{(5 * qtd_maquinas)} pçs", "Especificação": f"Bitola de **{bitola_descarga}\"**"},
        {"Componente / Insumo": "Luva de Cobre - Sucção", "Quantidade": f"{(3 * qtd_maquinas)} pçs", "Especificação": f"Bitola de **{bitola_succao}\"**"},
        {"Componente / Insumo": "Luva de Cobre - Descarga", "Quantidade": f"{(3 * qtd_maquinas)} pçs", "Especificação": f"Bitola de **{bitola_descarga}\"**"},
        {"Componente / Insumo": "Sifão de Cobre", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação": f"Instalado na saída do evaporador - Bitola **{bitola_succao}\"**"},
        {"Componente / Insumo": "Fita Plástica PVC (Branca)", "Quantidade": f"{(10 * qtd_maquinas)} rolos", "Especificação": "Para proteção do isolamento elastomérico externo"},
        {"Componente / Insumo": "Quadro de Comando Elétrico", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação": "Completo com controlador digital e chaves de proteção"},
        {"Componente / Insumo": "Calço Amortecedor de Borracha", "Quantidade": f"{(4 * qtd_maquinas)} pçs", "Especificação": "Para pés da Unidade Condensadora (Eliminação de vibração)"},
        {"Componente / Insumo": "Suporte Metálico Condensadora", "Quantidade": f"{qtd_maquinas} pç(s)", "Especificação": "Suporte reforçado em perfil U para fixação robusta"},
        {"Componente / Insumo": "Canaleta de Acabamento", "Quantidade": f"{(2 * qtd_maquinas)} pçs", "Especificação": "Para passagem e proteção física de cabos e fiações"},
        {"Componente / Insumo": "Cabo Elétrico PP - Ventiladores", "Quantidade": f"{(25 * qtd_maquinas)} metros", "Especificação": "Cabo PP 4 x 1.5 mm²"},
        {"Componente / Insumo": "Cabo Elétrico PP - Resistências", "Quantidade": f"{(25 * qtd_maquinas)} metros", "Especificação": "Cabo PP 4 x 2.5 mm² (Dimensionado para corrente de degelo)"},
        {"Componente / Insumo": "Cabo Elétrico PP - Força Geral", "Quantidade": f"{(25 * qtd_maquinas)} metros", "Especificação": "Cabo PP 4 x 4.0 mm²"},
        {"Componente / Insumo": "Cabo Elétrico PP - Iluminação", "Quantidade": f"{(25 * qtd_maquinas)} metros", "Especificação": "Cabo PP 2 x 1.5 mm²"},
        {"Componente / Insumo": "Gás / Fluido Refrigerante", "Quantidade": f"{qtd_maquinas} cilindro(s)", "Especificação": f"Cilindro de carga original compatível ({tipo_gas})"},
        {"Componente / Insumo": "Óleo Lubrificante Frigorífico", "Quantidade": f"{qtd_maquinas} litro(s)", "Especificação": f"Tipo {oleo_sugerido} Danfoss"},
        {"Componente / Insumo": "Solda Foscoper / Prata", "Quantidade": f"{(0.5 * qtd_maquinas):.1f} Kg", "Especificação": "Varetas de alta qualidade para brasagem"},
        {"Componente / Insumo": "Fluxo para Solda", "Quantidade": "1 pote", "Especificação": "Decapante químico para limpeza de tubos de cobre"},
        {"Componente / Insumo": "Carga de Gás MAP", "Quantidade": f"{(3 * qtd_maquinas)} pçs", "Especificação": "Cilindros descartáveis para maçarico portátil de brasagem"}
    ]
    
    st.table(tabela_acessorios_mecanicos)
    
    st.info("""
    💡 **INFORMAÇÃO IMPORTANTE:** Os dados e quantitativos apresentados neste relatório foram consolidados com base na análise técnica dos parâmetros fornecidos pelo cliente, o qual é inteiramente responsável pela exatidão das dimensões e especificações de entrada do projeto.
    """)