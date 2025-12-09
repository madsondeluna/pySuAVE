# pySuAVE - Migracao Fortran para Python

## RESUMO EXECUTIVO

Projeto de migracao do software SuAVE (Surface Assessment Via grid Evaluation)
de Fortran 90/95 para Python moderno, mantendo maxima acuracia matematica.

**Status Atual**: Fundacao completa + Funcoes matematicas core em andamento

## PROGRESSO ATUAL

### Completo
- Estrutura do projeto Python
- Tipos de dados (Cartesiano, Esferico)
- Sistema de I/O (PDB, NDX)
- Funcoes de parametros de grid
- Funcoes de RMSD
- Funcoes de calculo de area
- 25+ testes unitarios

### Em Andamento
- Funcoes de densidade
- Funcoes de ordem
- Funcoes de espessura

## ARQUIVOS PYTHON CRIADOS

```
pysuave/                        (Pacote principal)
 __init__.py                 Exports principais
 core/                       Tipos e constantes
    __init__.py
    types.py               AtomData, Coordinate3D, SphericalCoordinate
    constants.py           Constantes matematicas e fisicas
 io/                        Entrada/Saida
    __init__.py
    pdb.py                 Leitor/escritor PDB
    ndx.py                 Leitor/escritor NDX
 geometry/                  Funcoes geometricas
    __init__.py
    grid_params.py         Parametros de grid
    rmsd.py                Calculo de RMSD
    area.py                Calculo de area
 analysis/                  Ferramentas de analise (preparado)
    __init__.py
 cli/                       Interface CLI (preparado)
    __init__.py
 utils/                     Utilitarios (preparado)
     __init__.py

tests/                         Testes unitarios
 __init__.py
 test_types.py              Testes de tipos de dados
 test_grid_params.py        Testes de parametros de grid
 test_area.py               Testes de calculo de area

Total: 18 arquivos Python, ~2016 linhas
```

## FUNCOES MIGRADAS

### Parametros de Grid (grid_params.py)
1. `calculate_grid_parameters_cartesian()` <- param()
2. `calculate_grid_parameters_spherical()` <- param_esf()
3. `calculate_bin_size_cartesian()` <- def_bin()
4. `calculate_bin_size_spherical()` <- def_bin_sph()

### RMSD (rmsd.py)
5. `calculate_rmsd_cartesian()` <- calc_rmsd()
6. `calculate_rmsd_spherical()` <- calc_rmsd_sph()
7. `calculate_rmsd_inertia()` <- calc_rmsd_inert()

### Area (area.py)
8. `calculate_triangle_area_heron()` <- Formula de Heron
9. `calculate_surface_area_cartesian()` <- calc_area()
10. `calculate_surface_area_and_volume_spherical()` <- calc_area_sph()

**Total**: 10 funcoes matematicas migradas de funcproc.f90 (10/73 = 13.7%)

## INSTALACAO

```bash
# Clonar/navegar para o diretorio
cd /Volumes/promethion/pySuAVE

# Executar script de instalacao
./install_dev.sh

# OU manualmente:
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## USO

### Ativar Ambiente
```bash
source venv/bin/activate
```

### Executar Testes
```bash
pytest tests/ -v
```

### Exemplo Programatico
```python
from pysuave.geometry import (
    calculate_grid_parameters_cartesian,
    calculate_surface_area_cartesian
)
from pysuave.io import read_pdb, read_ndx

# Ler dados
atoms = read_pdb("protein.pdb")
indices = read_ndx("selection.ndx")

# Calcular parametros de grid
r_fit, alpha = calculate_grid_parameters_cartesian(
    x_max=100.0, x_min=0.0,
    y_max=100.0, y_min=0.0,
    num_points=1000,
    roughness=1.0
)

print(f"Raio de ajuste: {r_fit:.3f} A")
print(f"Parametro de suavizacao: {alpha:.3f}")
```

## DOCUMENTACAO

- `README_PYTHON.md` - Documentacao principal do projeto
- `MIGRATION_PROGRESS.md` - Relatorio de progresso geral
- `MATH_FUNCTIONS_MIGRATION.md` - Detalhes tecnicos da migracao matematica
- `SESSION_SUMMARY.md` - Resumo desta sessao
- `.agent/workflows/fortran-to-python-migration.md` - Plano completo

## CARACTERISTICAS

### Acuracia Matematica
- Formulas identicas ao Fortran original
- Coeficientes empiricos preservados com precisao total
- Conversao correta de indices (1-based -> 0-based)
- Validacao numerica em testes

### Qualidade do Codigo
- Type hints: 100%
- Docstrings: 100%
- Testes: 25+ testes unitarios
- Validacao de entrada: Todas as funcoes
- Mensagens de erro descritivas

### Melhorias sobre Fortran
- Documentacao inline extensiva
- Validacao robusta de entrada
- Type safety
- Testes automatizados
- Codigo mais legivel

## PROXIMOS PASSOS

1. Migrar funcoes de densidade (calc_dens_sph)
2. Migrar funcoes de ordem (calc_order, calc_order_sph)
3. Migrar funcoes de espessura (calc_thick, calc_thick_sph)
4. Implementar primeira ferramenta completa (s_stat)
5. Adicionar otimizacao com Numba

## METRICAS

- Linhas Python: ~2016 linhas
- Funcoes migradas: 10/73 (13.7%)
- Testes: 25+ testes
- Cobertura: Crescente
- Fases completas: 3/10 (30%)

## CITACAO

Se usar pySuAVE em pesquisas, cite:

```bibtex
@article{santos2022suave,
  title={Surface Assessment via Grid Evaluation (SuAVE) for Every Surface Curvature and Cavity Shape},
  author={Santos, Denys E. S. and Coutinho, Kaline and Soares, Thereza A.},
  journal={Journal of Chemical Information and Modeling},
  volume={62},
  pages={4690--4701},
  year={2022},
  doi={10.1021/acs.jcim.2c00673}
}
```

## CONTATO

- Email: suave.biomat@gmail.com
- Website: https://www.biomatsite.net/suave-software

## LICENCA

GPL-3.0 (mesma licenca do codigo original Fortran)

---

**Codigo Original**: Denys E. S. Santos (Fortran)  
**Migracao Python**: Em andamento (2025)  
**Supervisao**: Thereza A. Soares, Kaline Coutinho
