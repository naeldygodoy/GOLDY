import math

def calcular_tudo(comp_ext, larg_ext, alt_ext, comp_int, larg_int, alt_int, isolamento, temp_desejada, espessura_teto, dados_porta):
    """
    Processa toda a engenharia de acessórios, portas e complementos de isolamento.
    """
    # Recuperando dados da porta selecionada
    larg_porta = dados_porta["largura"]
    alt_porta = dados_porta["altura"]
    
    # -------------------------------------------------------------------------
    # 3. ACESSÓRIOS DE ISOLAMENTO E PORTAS (Cálculos de Engenharia)
    # -------------------------------------------------------------------------
    
    # TRILHO INOX: Igual à largura do vão (vistas comerciais em peças de 1m)
    trilho_inox_pcs = math.ceil(larg_porta)
    
    # SUPORTE TRILHO: 6 peças a cada metro de vão da porta
    suporte_trilho_pcs = math.ceil(larg_porta * 6)
    
    # CORTINA PLÁSTICA POLAR:
    # Cada suporte tem uma tira. Comprimento da tira = altura da porta + 10cm (0.10m)
    # Metragem total = quantidade de tiras * comprimento de cada tira. Venda em múltiplos de 10m.
    altura_tira = alt_porta + 0.10
    metragem_total_cortina = suporte_trilho_pcs * altura_tira
    metragem_comercial_cortina = math.ceil(metragem_total_cortina / 10.0) * 10
    
    # Identificação da Espessura em cm para a regra de perfis
    espessura_cm = round(espessura_teto * 100)
    
    # CANTONEIRA EXTERNA & INTERNA 40X40
    # Regra de modelo por espessura
    if espessura_cm in [7, 10]:
        modelo_cantoneira = "40 x 140"
    elif espessura_cm in [12, 15]:
        modelo_cantoneira = "40 x 190"
    else: # 20cm
        modelo_cantoneira = "40 x 240"
        
    # Metragem das Cantoneiras: Perímetro externo + (4 * altura externa)
    perimetro_ext = (comp_ext * 2) + (larg_ext * 2)
    metragem_cantoneira = perimetro_ext + (4 * alt_ext)
    # Barras de 3 metros
    barras_cantoneira_ext = math.ceil(metragem_cantoneira / 3.0)
    barras_cantoneira_int = barras_cantoneira_ext # Segue a mesma regra informada
    
    # PERFIL U: Medida dinâmica (40 x espessura x 40) em barras de 3m
    # Metragem = Perímetro externo + Vão da porta (L + A + L + A)
    vao_porta = (larg_porta * 2) + (alt_porta * 2)
    metragem_perfil_u = perimetro_ext + vao_porta
    barras_perfil_u = math.ceil(metragem_perfil_u / 3.0)
    
    # REBITE REPUXO 312: (Soma de TODAS as barras de cantoneiras e perfis) * 12
    total_barras_perfis = barras_cantoneira_ext + barras_cantoneira_int + barras_perfil_u
    total_rebites_unidades = total_barras_perfis * 12
    centos_rebites = math.ceil(total_rebites_unidades / 100)
    
    # SELANTE PU: Estimativa técnica padrão (1 tubo para cada 3 metros de perfil/cantoneira aplicados)
    total_metragem_perfis = (metragem_cantoneira * 2) + metragem_perfil_u
    tubos_selante = math.ceil(total_metragem_perfis / 3.0)
    
    # PROTEÇÃO E IMPERMEABILIZAÇÃO DO PISO (COM RECORTE/SOBRA TÉCNICA)
    area_externa = comp_ext * larg_ext
    
    # CORREÇÃO: Área da Manta calculada com acréscimo de 0.50m no C e na L para virada de canto
    area_manta = (comp_ext + 0.5) * (larg_ext + 0.5)
    rolos_manta = math.ceil(area_manta / 10.0)
    
    # Hidroasfalto: 1 balde a cada 3 rolos de manta
    baldes_hidroasfalto = math.ceil(rolos_manta / 3.0)
    
    # Lona: Aplicada em 2 vezes a área externa (cada peça tem 20m²)
    pecas_lona = math.ceil((area_externa * 2) / 20.0)
    
    # Poliuretano Spray: Padrão fixo de 10 peças
    spray_pu_pcs = 10

    return {
        "trilho_inox_pcs": trilho_inox_pcs,
        "suporte_trilho_pcs": suporte_trilho_pcs,
        "cortina_polar_metros": metragem_comercial_cortina,
        "modelo_cantoneira": modelo_cantoneira,
        "cantoneira_ext_barras": barras_cantoneira_ext,
        "cantoneira_int_barras": barras_cantoneira_int,
        "modelo_perfil_u": f"40 x {espessura_cm} x 40",
        "perfil_u_barras": barras_perfil_u,
        "rebites_centos": centos_rebites,
        "selante_pu_tubos": tubos_selante,
        "area_manta_calculada": area_manta, # Passando o valor exato para a descrição
        "manta_asfaltica_rolos": rolos_manta,
        "hidroasfalto_baldes": baldes_hidroasfalto,
        "lona_pcs": pecas_lona,
        "spray_pu_pcs": spray_pu_pcs
    }