---
description: Plano de migração do SuAVE de Fortran para Python
---

# Plano de Migração: SuAVE Fortran → Python

## Visão Geral do Projeto

**Objetivo**: Converter o software SuAVE (Surface Assessment Via grid Evaluation) de Fortran 90/95 para Python, mantendo a funcionalidade científica e melhorando a usabilidade.

### Estrutura Atual (Fortran)
- **Módulos principais**: 
  - `types.f90` - Definição de tipos de dados
  - `variables.F90` - Variáveis globais (com preprocessador)
  - `funcproc.f90` - Funções e procedimentos principais (~2063 linhas, 73 funções)
  - `startup.f90` - Inicialização
  - `write_help.f90` - Sistema de ajuda
  - `diag.f` - Diagonalização (para coordenadas esféricas)

- **Ferramentas (s_*.f90)**:
  - Cartesianas (`_c`): `s_area_c`, `s_dens_c`, `s_gauss_c`, `s_grid_c`, `s_order_c`, `s_thick_c`, `s_topog_c`
  - Esféricas (`_s`): `s_bend_s`, `s_count_s`, `s_densph_s`, `s_gridsph_s`, `s_inertia_s`, `s_shell_s`, `s_spher_s`
  - Utilitários: `s_index`, `s_stat`, `s_filter`

- **Dependências**:
  - `libquadmath` (precisão estendida)
  - `libgmxfort` (leitura de trajetórias XTC do GROMACS)
  - OpenMP (paralelização)

## Estratégia de Migração

### Fase 1: Estrutura Base (Fundação)
**Objetivo**: Criar a arquitetura Python equivalente

1. **Criar estrutura de diretórios**
   ```
   pySuAVE/
    pysuave/              # Pacote principal
       __init__.py
       core/             # Módulos centrais
          __init__.py
          types.py      # Dataclasses (equivalente a types.f90)
          constants.py  # Constantes
          config.py     # Configurações
       geometry/         # Funções geométricas
          __init__.py
          cartesian.py  # Geometria cartesiana
          spherical.py  # Geometria esférica
       io/               # Entrada/Saída
          __init__.py
          pdb.py        # Leitura PDB
          ndx.py        # Leitura NDX
          trajectory.py # Leitura trajetórias
       analysis/         # Ferramentas de análise
          __init__.py
          area.py
          density.py
          curvature.py
          statistics.py
       cli/              # Interface de linha de comando
          __init__.py
          commands.py
       utils/            # Utilitários
           __init__.py
           grid.py
           helpers.py
    tests/                # Testes unitários
    examples/             # Exemplos (migrar do original)
    docs/                 # Documentação
    setup.py
    pyproject.toml
    README.md
   ```

2. **Definir dependências Python**
   - `numpy` - arrays e operações numéricas
   - `scipy` - funções científicas
   - `pandas` - manipulação de dados
   - `MDAnalysis` ou `mdtraj` - leitura de trajetórias
   - `numba` - JIT compilation para performance
   - `click` ou `argparse` - CLI
   - `pytest` - testes
   - `h5py` - armazenamento eficiente (opcional)

### Fase 2: Migração de Tipos e Estruturas
**Objetivo**: Converter tipos de dados Fortran para Python

1. **Converter `types.f90` → `core/types.py`**
   - `vet1` → dataclass com coordenadas + metadados atômicos
   - `vet2` → dataclass com coordenadas XYZ
   - `vet3` → dataclass com coordenadas esféricas (ρ, φ, θ)

2. **Converter `variables.F90` → múltiplos módulos**
   - Separar por funcionalidade (não usar variáveis globais)
   - Criar classes de configuração
   - Usar enums para flags

### Fase 3: Migração de Funções Core
**Objetivo**: Converter `funcproc.f90` (73 funções)

**Prioridade Alta** (funções críticas):
1. `calc_area` / `calc_area_sph` - Cálculo de área
2. `calc_rmsd` / `calc_rmsd_sph` - RMSD
3. Grid generation functions
4. Density calculation functions

**Prioridade Média**:
- File I/O functions
- Parameter calculation
- Statistical functions

**Prioridade Baixa**:
- Helper functions
- Formatting functions

### Fase 4: Migração de I/O
**Objetivo**: Leitura/escrita de arquivos

1. **PDB reader** (`abre` function)
2. **NDX reader** (`abre_ndx` function)
3. **Trajectory reader** (`abre_trj` function)
   - Usar MDAnalysis ou mdtraj para XTC
4. **Output writers**

### Fase 5: Migração de Ferramentas
**Objetivo**: Converter cada ferramenta `s_*.f90`

**Ordem sugerida**:
1. `s_index` - Criação de índices (fundamental)
2. `s_stat` - Estatísticas (simples, bom teste)
3. `s_filter` - Filtro (simples)
4. `s_grid_c` - Grid cartesiano
5. `s_gridsph_s` - Grid esférico
6. Demais ferramentas conforme necessidade

### Fase 6: CLI e Interface
**Objetivo**: Interface de usuário

1. **Criar CLI moderna** usando `click`
   - Subcomandos para cada ferramenta
   - Help system integrado
   - Validação de argumentos

2. **Exemplo de uso**:
   ```bash
   pysuave densph --input file.pdb --index1 file1.ndx --index2 file2.ndx --dens dens.ndx
   ```

### Fase 7: Otimização e Performance
**Objetivo**: Garantir performance comparável ao Fortran

1. **Usar NumPy vetorização**
2. **Numba JIT** para loops críticos
3. **Multiprocessing** (equivalente ao OpenMP)
4. **Profiling** e otimização

### Fase 8: Testes e Validação
**Objetivo**: Garantir resultados idênticos

1. **Testes unitários** para cada função
2. **Testes de integração** comparando com saída Fortran
3. **Testes de performance**
4. **Validação científica** com dados reais

### Fase 9: Documentação
**Objetivo**: Documentação completa

1. **Docstrings** (Google style)
2. **Sphinx** documentation
3. **Tutoriais** e exemplos
4. **API reference**

### Fase 10: Empacotamento e Distribuição
**Objetivo**: Facilitar instalação

1. **PyPI package**
2. **Conda package**
3. **Docker image** (opcional)
4. **CI/CD** (GitHub Actions)

##  Ferramentas e Tecnologias

### Stack Python Recomendado
- **Python**: 3.9+ (para type hints modernos)
- **NumPy**: Arrays e álgebra linear
- **SciPy**: Funções científicas (interpolação, integração)
- **Numba**: JIT compilation para performance
- **MDAnalysis**: Leitura de trajetórias moleculares
- **Click**: CLI framework
- **Pytest**: Testing framework
- **Black**: Code formatting
- **MyPy**: Type checking

### Conversões Importantes

#### Fortran → Python
- `real` → `np.float64` ou `float`
- `integer` → `np.int32` ou `int`
- `type` → `@dataclass` ou `class`
- `module` → `.py` file
- `subroutine` → `def function() -> None:`
- `function` → `def function() -> ReturnType:`
- Arrays 1-indexed → 0-indexed
- `do i=1,n` → `for i in range(n):`
- `allocatable` → dynamic Python lists/arrays

#### Performance
- Fortran loops → NumPy vectorization
- OpenMP → `multiprocessing` ou `joblib`
- Fortran I/O → `numpy.loadtxt`, `pandas`, `MDAnalysis`

## Métricas de Sucesso

1. **Funcionalidade**: Todos os 15+ comandos funcionando
2. **Precisão**: Resultados idênticos ao Fortran (tolerância < 1e-6)
3. **Performance**: Tempo de execução < 2x Fortran (com Numba)
4. **Usabilidade**: CLI intuitiva, documentação completa
5. **Manutenibilidade**: Código limpo, testado, type-hinted
6. **Distribuição**: Instalável via `pip install pysuave`

## Próximos Passos Imediatos

1. Criar estrutura de diretórios
2. Configurar `pyproject.toml` e dependências
3. Migrar `types.f90` → `core/types.py`
4. Migrar funções de I/O básicas
5. Migrar primeira ferramenta simples (`s_stat`)
6. Criar testes de validação

## Notas Importantes

- **Manter compatibilidade científica**: Resultados devem ser idênticos
- **Melhorar usabilidade**: Python permite interfaces mais amigáveis
- **Documentar decisões**: Registrar escolhas de design
- **Testes contínuos**: Validar cada componente migrado
- **Performance**: Usar Numba/Cython se necessário para loops críticos