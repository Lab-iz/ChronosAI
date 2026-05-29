# Como Rodar o CHRONOS-SEGURO

Este guia mostra o caminho recomendado para instalar, executar e avaliar o projeto localmente.

Todos os comandos partem da raiz do repositorio:

```text
<repositorio>
```

O projeto mantem apenas um inicializador web na raiz:

```text
run.py
```

## Rota rapida para avaliacao

Use este fluxo quando o objetivo for apenas abrir a demonstracao e entender o sistema.

1. Instale o projeto:

```powershell
python -m pip install -e ".[ml,science,dev]"
```

2. Rode a interface:

```powershell
python run.py
```

3. Abra no navegador:

```text
http://127.0.0.1:8000/
```

4. Dentro da interface, use:

- `1. Ver demo 3D`
- `2. Rodar teste Apophis`

5. Leia o painel `Relatorio guiado`.

Para deploy publico, veja [Deploy no Render](deploy_render.md).

## Ambiente virtual

Use Python `3.11` ou `3.12`. O projeto declara `>=3.11,<3.14`.

No Windows:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Se a maquina tiver apenas Python `3.13` ou `3.14`, instale uma versao `3.11` ou `3.12` para rodar a stack completa.

## Instalacao

Instalacao minima:

```powershell
python -m pip install -e .
```

Instalacao recomendada para treino, ciencia e desenvolvimento:

```powershell
python -m pip install -e ".[ml,science,dev]"
```

REBOUND e opcional:

```powershell
python -m pip install -r requisitos-rebound.txt
```

Se `rebound` falhar no Windows por compilador C/C++, o sistema continua funcionando com o backend de referencia em NumPy.

## Testes

```powershell
python -m pytest -q
```

## Gerar conjunto generalista

```powershell
python -m chronos_seguro.aplicativos.linha_comando.principal gerar-generalista `
  --diretorio-saida dados/processados/generalista `
  --num-amostras 128 `
  --min-corpos 2 `
  --max-corpos 6 `
  --dt-dias 1.0
```

Arquivos gerados:

- `dados/processados/generalista/dataset.npz`
- `dados/processados/generalista/manifest.json`
- `dados/processados/generalista/scaler.json`

## Gerar conjunto especialista

```powershell
python -m chronos_seguro.aplicativos.linha_comando.principal gerar-especialista `
  --diretorio-saida dados/processados/especialista `
  --cenario apophis/cenario_apophis.json `
  --num-amostras 64 `
  --dt-dias 1.0
```

Arquivos gerados:

- `dados/processados/especialista/dataset.npz`
- `dados/processados/especialista/manifest.json`
- `dados/processados/especialista/scaler.json`

## Treinar modelo generalista

```powershell
python -m chronos_seguro.aplicativos.linha_comando.principal treinar-generalista `
  --diretorio-dataset dados/processados/generalista `
  --diretorio-saida modelos/pontos_controle/generalista `
  --epocas 20 `
  --tamanho-lote 16
```

Arquivos esperados:

- `modelos/pontos_controle/generalista/model.pt`
- `modelos/pontos_controle/generalista/ood_guard.json`
- `modelos/pontos_controle/generalista/scaler.json`
- `modelos/pontos_controle/generalista/training_manifest.json`

## Fazer ajuste especialista

```powershell
python -m chronos_seguro.aplicativos.linha_comando.principal treinar-especialista `
  --diretorio-dataset dados/processados/especialista `
  --diretorio-saida modelos/pontos_controle/especialista `
  --ponto-controle-base modelos/pontos_controle/generalista/model.pt `
  --epocas 10 `
  --tamanho-lote 16
```

## Rodar simulacao hibrida

Sem modelo treinado:

```powershell
python -m chronos_seguro.aplicativos.linha_comando.principal simular `
  --cenario apophis/cenario_apophis.json `
  --passos 30 `
  --dt-dias 1.0 `
  --saida relatorios/validacao/simulacao.json
```

Com modelo treinado:

```powershell
python -m chronos_seguro.aplicativos.linha_comando.principal simular `
  --cenario apophis/cenario_apophis.json `
  --passos 30 `
  --dt-dias 1.0 `
  --ponto-controle modelos/pontos_controle/especialista/model.pt `
  --escalonador modelos/pontos_controle/especialista/scaler.json `
  --guarda-ood modelos/pontos_controle/especialista/ood_guard.json `
  --saida relatorios/validacao/simulacao.json
```

## Rodar validacao Apophis

```powershell
python -m chronos_seguro.aplicativos.linha_comando.principal validar-apophis `
  --passos 180 `
  --dt-dias 1.0
```

Com modelo treinado:

```powershell
python -m chronos_seguro.aplicativos.linha_comando.principal validar-apophis `
  --passos 180 `
  --dt-dias 1.0 `
  --ponto-controle modelos/pontos_controle/especialista/model.pt `
  --escalonador modelos/pontos_controle/especialista/scaler.json `
  --guarda-ood modelos/pontos_controle/especialista/ood_guard.json
```

Relatorios gerados:

- `relatorios/validacao/validacao_apophis.json`
- `relatorios/validacao/resumo_validacao_apophis.txt`

## Subir a interface web

Forma padrao:

```powershell
python run.py
```

Endereco padrao:

```text
http://127.0.0.1:8000/
```

Sem abrir navegador automaticamente:

```powershell
$env:CHRONOS_OPEN_BROWSER="false"
python run.py
```

Forma manual:

```powershell
uvicorn chronos_seguro.aplicativos.api.principal:app --reload
```

## Interface web

A interface oferece:

- visualizacao 3D de orbitas no navegador;
- modo de avaliacao rapida com demo 3D e teste Apophis;
- area avancada recolhida para geracao de dados, treino e simulacao manual;
- validacao Apophis com leitura guiada das metricas;
- catalogo automatico de cenarios, pontos de controle, escalonadores e relatorios.

Para avaliacao rapida:

1. Abra a pagina.
2. Clique em `1. Ver demo 3D`.
3. Clique em `2. Rodar teste Apophis`.
4. Leia o `Relatorio guiado`.

## Problemas comuns

### `torch` nao instala no Windows

Se aparecer erro de caminho longo, habilite Windows Long Paths ou use um caminho curto para o ambiente virtual.

### `rebound` nao instala no Windows

Se falhar por compilador C++, continue sem ele por enquanto. O sistema usa o backend NumPy de referencia.

### `chronos` nao foi reconhecido

Use a entrada direta:

```powershell
python -m chronos_seguro.aplicativos.linha_comando.principal <comando>
```

### `pip install` falhou com `Fatal error in launcher`

Use:

```powershell
python -m pip install -e ".[ml,science,dev]"
```

em vez de chamar `pip` diretamente.
