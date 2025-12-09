# Relatorio de Migracao - Funcoes Matematicas

Data: 09 de Dezembro de 2025
Fase: 4 - Migracao de Funcoes Core (EM ANDAMENTO)

## Resumo da Sessao

Iniciada a migracao das funcoes matematicas do funcproc.f90 (2063 linhas, 73 funcoes)
com foco em maxima acuracia numerica e documentacao extensiva.

## Funcoes Migradas

### 1. Parametros de Grid (grid_params.py)

#### calculate_grid_parameters_cartesian()
- Fortran: subroutine param()
- Calcula raio de ajuste (r_fit) e parametro de suavizacao (alpha)
- Formula: r_fit = 3 * diagonal / sqrt(num_points - 1)
- Formula: alpha = exp(0.4247 * roughness * log(density) - 1.3501 / roughness)
- Validacao completa de entradas
- Documentacao matematica detalhada

#### calculate_grid_parameters_spherical()
- Fortran: subroutine param_esf()
- Versao esferica dos parametros de grid
- Formula: r_fit = 6 * radius * pi / sqrt(num_points - 1)
- Formula: alpha = exp(0.4984 * roughness * log(density) - 1.06016110229 / roughness)
- Coeficientes empiricos diferentes do caso Cartesiano

#### calculate_bin_size_cartesian()
- Fortran: subroutine def_bin()
- Calcula tamanho otimo de bins para grid retangular
- Formula: bin = round(sqrt(n_index - 1) - 1)

#### calculate_bin_size_spherical()
- Fortran: subroutine def_bin_sph()
- Calcula tamanho otimo de bins para grid esferico
- Formula: bin = round(sqrt(2 * (n_index - 1)))
- Fator de 2 para geometria esferica

### 2. Calculo de RMSD (rmsd.py)

#### calculate_rmsd_cartesian()
- Fortran: function calc_rmsd()
- Calcula RMSD entre atomos e superficie ajustada (Cartesiano)
- Formula: RMSD = sqrt(sum(delta_z^2) / (n1 + n2))
- Conversao de indices 1-based (Fortran) para 0-based (Python)
- Validacao de limites de grid

#### calculate_rmsd_spherical()
- Fortran: function calc_rmsd_sph()
- Calcula RMSD em coordenadas esfericas
- Usa desvio radial (rho) ao inves de z
- Indexacao por angulos (phi, theta)

#### calculate_rmsd_inertia()
- Fortran: function calc_rmsd_inert()
- RMSD para sistema de coordenadas de inercia
- Indexacao modificada: i = round((cos(phi) + 1) / dz + 0.5)
- Usado apenas no programa s_inertia

### 3. Calculo de Area (area.py)

#### calculate_triangle_area_heron()
- Formula de Heron para area de triangulo
- Formula: s = (a + b + c) / 2
- Formula: Area = sqrt(s * (s - a) * (s - b) * (s - c))
- Estavel numericamente para todos os tipos de triangulos
- Trata casos degenerados (pontos colineares)

#### calculate_surface_area_cartesian()
- Fortran: function calc_area()
- Calcula area total por triangulacao
- Cada celula de grid dividida em 2 triangulos
- Triangulo 1: (i-1,j-1), (i-1,j), (i,j-1)
- Triangulo 2: (i-1,j), (i,j-1), (i,j)
- Soma areas usando Heron

#### calculate_surface_area_and_volume_spherical()
- Fortran: subroutine calc_area_sph()
- Calcula area E volume para superficies esfericas
- Volume: integracao de angulo solido
- Formula: V = sum(solid_angle * area * radius / 3)
- Nota: Funcao ang() ainda precisa ser implementada

## Testes Criados

### test_grid_params.py
- TestGridParametersCartesian: 3 testes
- TestGridParametersSpherical: 3 testes
- TestBinSizeCalculations: 6 testes
- Total: 12 testes

### test_area.py
- TestTriangleAreaHeron: 5 testes
- TestSurfaceAreaCartesian: 8 testes
- Total: 13 testes

### test_types.py (anterior)
- Total: 20+ testes

## Estatisticas

### Codigo Migrado
- Linhas Python: ~1200 linhas (novas)
- Arquivos criados: 6 arquivos
- Funcoes migradas: 10 funcoes
- Testes: 25+ novos testes

### Equivalencia Fortran
- param() -> calculate_grid_parameters_cartesian()
- param_esf() -> calculate_grid_parameters_spherical()
- def_bin() -> calculate_bin_size_cartesian()
- def_bin_sph() -> calculate_bin_size_spherical()
- calc_rmsd() -> calculate_rmsd_cartesian()
- calc_rmsd_sph() -> calculate_rmsd_spherical()
- calc_rmsd_inert() -> calculate_rmsd_inertia()
- calc_area() -> calculate_surface_area_cartesian()
- calc_area_sph() -> calculate_surface_area_and_volume_spherical()
- Formula de Heron -> calculate_triangle_area_heron()

## Caracteristicas da Migracao

### Acuracia Matematica
- Formulas identicas ao Fortran original
- Coeficientes empiricos preservados com precisao total
  - Cartesiano: 0.4247, 1.3501
  - Esferico: 0.4984, 1.06016110229
- Conversao correta de indices (1-based -> 0-based)
- Validacao numerica em testes

### Documentacao
- Docstrings completas em todas as funcoes
- Formulacao matematica explicita
- Notas sobre equivalencia Fortran
- Exemplos de uso
- Descricao de parametros e retornos
- Notas sobre casos especiais

### Validacao
- Verificacao de limites de entrada
- Mensagens de erro descritivas
- Tratamento de casos degenerados
- Testes de casos extremos

### Melhorias sobre Fortran
- Type hints completos
- Validacao de entrada robusta
- Mensagens de erro claras
- Documentacao inline
- Testes unitarios extensivos
- Codigo mais legivel

## Proximos Passos

### Funcoes Prioritarias (funcproc.f90)
1. calc_dens_sph() - Calculo de densidade esferica
2. calc_order() - Calculo de parametro de ordem
3. calc_order_sph() - Parametro de ordem esferico
4. calc_thick() - Calculo de espessura
5. calc_thick_sph() - Espessura esferica
6. calc_topog() - Topografia
7. calc_inertia() - Momento de inercia
8. print_pdb() - Escrita de PDB (ja parcialmente em io/pdb.py)

### Funcoes Auxiliares Necessarias
1. ang() - Calculo de angulo solido (usado em calc_area_sph)
2. Funcoes de grid generation
3. Funcoes de interpolacao

### Ferramentas Completas
Apos migrar funcoes core, implementar:
1. s_stat - Estatisticas (mais simples)
2. s_filter - Filtro
3. s_index - Criacao de indices
4. s_grid_c - Grid cartesiano
5. s_gridsph_s - Grid esferico

## Notas Tecnicas

### Conversao de Indices
- Fortran: arrays 1-indexed
- Python: arrays 0-indexed
- Conversao: fortran_index = python_index + 1
- Loops Fortran: do i=2, n+1
- Loops Python: for i in range(1, n)

### Precisao Numerica
- Fortran real: equivalente a np.float64
- Uso de float() para conversao explicita
- max(0, ...) para evitar sqrt de negativos
- Tolerancias: 1e-6 para comparacoes, 1e-10 para zeros

### Performance
- NumPy para operacoes vetoriais
- Loops Python quando necessario (sera otimizado com Numba)
- Validacao de entrada antes de calculos pesados

## Metricas de Qualidade

- Type hints: 100%
- Docstrings: 100%
- Testes: 25+ testes, cobertura crescente
- Validacao: Todas as funcoes validam entradas
- Documentacao matematica: Completa

## Conclusao

Migracao das funcoes matematicas core esta progredindo bem. As funcoes
mais criticas (parametros de grid, RMSD, area) estao implementadas com
maxima acuracia e documentacao extensiva. Proxima etapa: completar
funcoes de densidade, ordem e espessura.

Estimativa: 10/73 funcoes migradas (13.7%)
Tempo estimado para completar funcproc.f90: 15-20 horas
