# pySuAVE - Python Implementation

**Status**: 🚧 **Em Desenvolvimento Ativo** - Migração de Fortran para Python

## 📖 Sobre o Projeto

Este é o **pySuAVE**, uma reimplementação em Python do software [SuAVE (Surface Assessment Via grid Evaluation)](https://www.biomatsite.net/suave-software), originalmente escrito em Fortran 90/95.

O SuAVE é uma ferramenta científica para análise de propriedades estruturais de interfaces químicas usando técnicas de geometria diferencial, amplamente utilizada em simulações de dinâmica molecular.

## 🎯 Objetivo da Migração

Converter o código Fortran para Python moderno, mantendo:
- ✅ **Precisão científica**: Resultados idênticos ao código original
- ✅ **Performance**: Uso de NumPy, Numba e paralelização
- ✅ **Usabilidade**: Interface mais amigável e pythônica
- ✅ **Manutenibilidade**: Código limpo, testado e documentado

## 📊 Progresso da Migração

### ✅ Fase 1: Estrutura Base (COMPLETO)
- [x] Estrutura de diretórios criada
- [x] `pyproject.toml` configurado
- [x] Dependências definidas

### ✅ Fase 2: Tipos e Estruturas (COMPLETO)
- [x] `types.f90` → `core/types.py` (dataclasses)
- [x] `variables.F90` → `core/constants.py`
- [x] Conversão Cartesiano ↔ Esférico
- [x] Testes unitários para tipos

### 🚧 Fase 3: I/O (EM ANDAMENTO)
- [x] Leitor/escritor de arquivos PDB
- [x] Leitor/escritor de arquivos NDX
- [ ] Leitor de trajetórias (XTC/TRR via MDAnalysis)
- [ ] Testes de I/O

### ⏳ Fase 4: Funções Core (PENDENTE)
- [ ] Migrar `funcproc.f90` (~73 funções)
  - [ ] Cálculo de área (Heron)
  - [ ] RMSD
  - [ ] Geração de grid
  - [ ] Densidade
  - [ ] Curvatura

### ⏳ Fase 5-10: Ferramentas, CLI, Otimização (PENDENTE)

## 🏗️ Estrutura do Projeto

```
pySuAVE/
├── pysuave/              # Pacote Python
│   ├── core/             # Tipos e constantes ✅
│   ├── io/               # Leitura/escrita de arquivos ✅
│   ├── geometry/         # Funções geométricas ⏳
│   ├── analysis/         # Ferramentas de análise ⏳
│   ├── cli/              # Interface de linha de comando ⏳
│   └── utils/            # Utilitários ⏳
├── tests/                # Testes unitários ✅
├── examples/             # Exemplos (do Fortran original)
├── docs/                 # Documentação
├── [Código Fortran original...]
└── pyproject.toml        # Configuração do projeto ✅
```

## 🚀 Instalação (Desenvolvimento)

```bash
# Clone o repositório
cd /Volumes/promethion/pySuAVE

# Crie um ambiente virtual
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Instale em modo desenvolvimento
pip install -e ".[dev]"
```

## 🧪 Executar Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=pysuave --cov-report=html
```

## 📚 Documentação Original

Para entender o SuAVE original em Fortran, consulte:
- **README.md** (original): Instruções de instalação Fortran
- **Citações**: Ver pasta `Citation/`
- **Exemplos**: Ver pasta `examples/`

## 📄 Citações

Se você usar o pySuAVE em pesquisas, por favor cite:

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

## 👥 Desenvolvedores

- **Código Fortran Original**: Denys E. S. Santos
- **Migração Python**: [Em andamento]
- **Supervisão**: Thereza A. Soares, Kaline Coutinho

## 📧 Contato

- Email: suave.biomat@gmail.com
- Website: https://www.biomatsite.net/suave-software

## 📝 Licença

GPL-3.0 (mesma licença do código original)

---

**Nota**: Este é um projeto em desenvolvimento ativo. Contribuições são bem-vindas!
