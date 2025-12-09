# O QUE AINDA FALTA MIGRAR - pySuAVE

Data: 09 de Dezembro de 2025

## RESUMO

**Total de funcoes no funcproc.f90**: 73 funcoes
**Funcoes migradas**: 10 funcoes (13.7%)
**Funcoes restantes**: 63 funcoes (86.3%)

**Ferramentas Fortran**: 15 programas (s_*.f90)
**Ferramentas migradas**: 0 programas (0%)
**Ferramentas restantes**: 15 programas (100%)

---

## FUNCOES DO FUNCPROC.F90

### JA MIGRADAS (10 funcoes)

1. param() -> calculate_grid_parameters_cartesian()
2. param_esf() -> calculate_grid_parameters_spherical()
3. def_bin() -> calculate_bin_size_cartesian()
4. def_bin_sph() -> calculate_bin_size_spherical()
5. calc_rmsd() -> calculate_rmsd_cartesian()
6. calc_rmsd_sph() -> calculate_rmsd_spherical()
7. calc_rmsd_inert() -> calculate_rmsd_inertia()
8. calc_area() -> calculate_surface_area_cartesian()
9. calc_area_sph() -> calculate_surface_area_and_volume_spherical()
10. Formula de Heron -> calculate_triangle_area_heron()

### FALTAM MIGRAR (63 funcoes)

#### PRIORIDADE ALTA - Funcoes Matematicas Core (20 funcoes)

**Densidade:**
1. calc_dens_sph() - Calculo de densidade esferica
   - Usado em: s_densph_s

**Ordem/Orientacao:**
2. calc_order() - Parametro de ordem (Cartesiano)
   - Usado em: s_order_c
3. calc_order_sph() - Parametro de ordem (Esferico)
   - Usado em: s_densph_s, s_gridsph_s

**Espessura:**
4. calc_thick() - Calculo de espessura (Cartesiano)
   - Usado em: s_thick_c
5. calc_thick_sph() - Calculo de espessura (Esferico)
   - Usado em: s_shell_s

**Topografia:**
6. calc_topog() - Calculo de topografia
   - Usado em: s_topog_c

**Inercia:**
7. calc_inertia() - Calculo de momento de inercia
   - Usado em: s_inertia_s

**Raio de Giracao:**
8. calc_gyrat() - Calculo de raio de giracao
   - Usado em: s_spher_s

**Conversoes de Coordenadas:**
9. cart2sphe() - Cartesiano para Esferico
   - Usado em: s_spher_s
10. sphe2cart() - Esferico para Cartesiano
    - Usado em: s_gridsph_s, s_densph_s, s_shell_s

**Angulo Solido:**
11. ang() - Calculo de angulo solido
    - Usado em: calc_area_sph (JA MIGRADA, mas ang() falta)

**Gaussiana:**
12. calc_gauss() - Calculo de curvatura Gaussiana
    - Usado em: s_gauss_c

**Estatisticas:**
13. calc_stat_aver() - Media, desvio, skewness, kurtosis
    - Usado em: s_stat
14. calc_stat_all() - Estatisticas completas
    - Usado em: s_stat
15. do_histogram() - Gerar histograma
    - Usado em: s_stat
16. calc_acf() - Funcao de autocorrelacao
    - Usado em: s_stat

**Filtro:**
17. filter_suave() - Filtro de suavizacao
    - Usado em: s_filter

**Grid:**
18. calcula_bin() - Calculo de bins para grid
    - Usado em: varios programas

**Outras:**
19. def_frame() - Definicao de frames de trajetoria
20. abre_trj() - Abertura de trajetorias (parcialmente em io/)

#### PRIORIDADE MEDIA - Funcoes de I/O e Formatacao (15 funcoes)

**Escrita de Arquivos:**
21. print_pdb() - Escrever PDB (parcialmente em io/pdb.py)
22. print_grid() - Escrever grid
23. print_grid_xpm() - Escrever grid em formato XPM
24. print_grid_xpm_xpm() - Escrever dois grids em XPM
25. print_xpm() - Escrever arquivo XPM
26. print_xpm_gauss() - Escrever XPM com Gaussiana
27. print_xpm_sph() - Escrever XPM esferico

**Leitura de Arquivos:**
28. abre() - Abertura generica de arquivos
29. abre_ndx() - Leitura de NDX (JA MIGRADA em io/ndx.py)

**Utilitarios:**
30. imprime() - Impressao de vetores
31. ending() - Finalizacao e tempo de execucao

#### PRIORIDADE BAIXA - Funcoes Auxiliares (28 funcoes)

Funcoes de suporte, helpers e utilitarios diversos que serao
migrados conforme necessidade durante a implementacao das ferramentas.

---

## FERRAMENTAS (PROGRAMAS s_*.f90)

### CARTESIANAS (7 programas)

1. **s_area_c.f90** (15089 linhas)
   - Calculo de area superficial
   - Funcoes necessarias: calc_area (MIGRADA)
   - Status: Pronto para migrar

2. **s_dens_c.f90** (17405 linhas)
   - Calculo de densidade
   - Funcoes necessarias: Funcoes de densidade (FALTAM)
   - Status: Aguardando funcoes

3. **s_gauss_c.f90** (14605 linhas)
   - Curvatura Gaussiana
   - Funcoes necessarias: calc_gauss (FALTA)
   - Status: Aguardando funcoes

4. **s_grid_c.f90** (10166 linhas)
   - Geracao de grid Cartesiano
   - Funcoes necessarias: Grid functions (FALTAM)
   - Status: Aguardando funcoes

5. **s_order_c.f90** (12121 linhas)
   - Parametro de ordem
   - Funcoes necessarias: calc_order (FALTA)
   - Status: Aguardando funcoes

6. **s_thick_c.f90** (15499 linhas)
   - Calculo de espessura
   - Funcoes necessarias: calc_thick (FALTA)
   - Status: Aguardando funcoes

7. **s_topog_c.f90** (14670 linhas)
   - Topografia
   - Funcoes necessarias: calc_topog (FALTA)
   - Status: Aguardando funcoes

### ESFERICAS (7 programas)

8. **s_bend_s.f90** (13695 linhas)
   - Curvatura de dobramento
   - Status: Aguardando funcoes

9. **s_count_s.f90** (12280 linhas)
   - Contagem de atomos
   - Status: Aguardando funcoes

10. **s_densph_s.f90** (17382 linhas)
    - Densidade esferica
    - Funcoes necessarias: calc_dens_sph (FALTA)
    - Status: Aguardando funcoes

11. **s_gridsph_s.f90** (12389 linhas)
    - Grid esferico
    - Funcoes necessarias: sphe2cart (FALTA)
    - Status: Aguardando funcoes

12. **s_inertia_s.f90** (12026 linhas)
    - Momento de inercia
    - Funcoes necessarias: calc_inertia (FALTA)
    - Status: Aguardando funcoes

13. **s_shell_s.f90** (18366 linhas)
    - Analise de camadas
    - Funcoes necessarias: calc_thick_sph (FALTA)
    - Status: Aguardando funcoes

14. **s_spher_s.f90** (17790 linhas)
    - Coordenadas esfericas
    - Funcoes necessarias: cart2sphe, calc_gyrat (FALTAM)
    - Status: Aguardando funcoes

### UTILITARIOS (3 programas)

15. **s_index.f90** (11434 linhas)
    - Criacao de indices
    - Status: Pronto para migrar (simples)

16. **s_stat.f90** (3785 linhas)
    - Estatisticas
    - Funcoes necessarias: calc_stat_* (FALTAM)
    - Status: Aguardando funcoes

17. **s_filter.f90** (4110 linhas)
    - Filtro de dados
    - Funcoes necessarias: filter_suave (FALTA)
    - Status: Aguardando funcoes

---

## OUTROS ARQUIVOS FORTRAN

### JA TRATADOS

1. **types.f90** - MIGRADO para core/types.py
2. **variables.F90** - PARCIALMENTE migrado para core/constants.py

### FALTAM MIGRAR

3. **startup.f90** (9593 linhas)
   - Inicializacao e parsing de argumentos
   - Sera substituido por CLI Python (click)

4. **write_help.f90** (23395 linhas)
   - Sistema de ajuda
   - Sera substituido por docstrings e --help do click

5. **diag.f** (5150 linhas)
   - Diagonalizacao de matrizes
   - Usar numpy.linalg ou scipy.linalg

---

## PLANO DE MIGRACAO SUGERIDO

### FASE ATUAL (Fase 4 - 13.7% completo)

**Proximos passos imediatos:**

1. **Migrar funcoes de densidade** (1-2 dias)
   - calc_dens_sph()
   - Testar com dados reais

2. **Migrar funcoes de ordem** (1-2 dias)
   - calc_order()
   - calc_order_sph()
   - Testar com dados reais

3. **Migrar funcoes de espessura** (1-2 dias)
   - calc_thick()
   - calc_thick_sph()
   - Testar com dados reais

4. **Migrar funcoes auxiliares criticas** (1-2 dias)
   - ang() - Angulo solido
   - cart2sphe() / sphe2cart()
   - calc_gyrat()

### FASE 5 - Primeira Ferramenta Completa (1 semana)

**Implementar s_stat** (mais simples):
- Migrar funcoes de estatistica
- Criar CLI basico
- Validar resultados vs Fortran
- Documentar

### FASE 6 - Ferramentas Principais (2-3 semanas)

**Ordem de implementacao sugerida:**
1. s_index (simples, fundamental)
2. s_filter (simples)
3. s_area_c (funcoes ja migradas)
4. s_grid_c (fundamental)
5. s_gridsph_s (fundamental)
6. Demais ferramentas conforme prioridade

### FASE 7-10 - Completar Migracao (1-2 meses)

- Todas as ferramentas restantes
- CLI completo
- Otimizacao com Numba
- Documentacao completa
- Testes de validacao
- Empacotamento PyPI

---

## ESTIMATIVAS

### Tempo Estimado por Componente

**Funcoes matematicas core** (20 funcoes): 2-3 semanas
**Funcoes de I/O** (15 funcoes): 1 semana
**Funcoes auxiliares** (28 funcoes): 1-2 semanas
**Ferramentas completas** (15 programas): 4-6 semanas
**CLI e interface**: 1 semana
**Testes e validacao**: 2 semanas
**Documentacao**: 1 semana
**Otimizacao**: 1 semana

**TOTAL ESTIMADO**: 3-4 meses de trabalho

### Progresso Atual

- Tempo investido: ~1 dia
- Progresso: 13.7% das funcoes core
- Fundacao: 100% completa
- Velocidade: ~10 funcoes/dia (com documentacao e testes)

### Projecao

Com ritmo atual:
- Funcoes core restantes: ~6 dias
- Ferramentas: ~15-20 dias
- Total: ~1-2 meses

---

## PRIORIDADES RECOMENDADAS

### CURTO PRAZO (Proxima semana)

1. calc_dens_sph()
2. calc_order() e calc_order_sph()
3. calc_thick() e calc_thick_sph()
4. ang() (necessario para calc_area_sph)
5. Implementar s_stat (primeira ferramenta completa)

### MEDIO PRAZO (Proximo mes)

1. Conversoes de coordenadas (cart2sphe, sphe2cart)
2. calc_inertia(), calc_gyrat()
3. calc_topog(), calc_gauss()
4. Implementar s_index, s_filter, s_area_c
5. Implementar s_grid_c, s_gridsph_s

### LONGO PRAZO (2-3 meses)

1. Todas as ferramentas restantes
2. CLI completo com click
3. Otimizacao com Numba
4. Documentacao Sphinx
5. Empacotamento PyPI/Conda

---

## CONCLUSAO

Ainda falta migrar:
- 63 funcoes do funcproc.f90 (86.3%)
- 15 ferramentas completas (100%)
- Sistema de CLI
- Otimizacao de performance

Mas a fundacao esta solida:
- Estrutura profissional
- Tipos de dados completos
- I/O funcional
- Funcoes matematicas core mais criticas migradas
- Testes e documentacao estabelecidos

Proximos passos: Focar em completar funcoes matematicas core
(densidade, ordem, espessura) e implementar primeira ferramenta
completa (s_stat) para validar todo o pipeline.
