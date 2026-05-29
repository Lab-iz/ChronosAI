# Pacote `chronos_seguro`

Este diretorio contem o codigo-fonte principal do CHRONOS-SEGURO.

## Organizacao

- `aplicativos`: API FastAPI, interface web e linha de comando.
- `avaliacao`: metricas, comparativos e resumos de validacao.
- `configuracao`: ajustes, caminhos e constantes globais.
- `dados`: carregamento de cenarios, cache, geradores e preprocessamento.
- `dominio`: contratos de estado, resultados e tipos compartilhados.
- `fisica`: unidades, referenciais, invariantes e motores fisicos.
- `modelos`: GNN residual, guarda OOD e estimativas de incerteza.
- `servicos`: fluxos de alto nivel para simulacao e interface.
- `simulacao`: motor hibrido, propagacao, fallback e missao Apophis.
- `treinamento`: treino, perdas, curriculo e pontos de controle.
- `utilitarios`: logs, serializacao, dispositivo e semente.

## Entrada web

O launcher unico fica na raiz do repositorio:

```powershell
python run.py
```

O servidor manual usa:

```powershell
uvicorn chronos_seguro.aplicativos.api.principal:app --reload
```

## Entrada CLI

```powershell
chronos gerar-generalista
chronos gerar-especialista
chronos treinar-generalista
chronos treinar-especialista
chronos simular
chronos validar-apophis
```

## Observacao de compatibilidade

O codigo, pastas e modulos foram traduzidos para PT-BR sempre que isso nao quebra contratos externos. Alguns nomes de campos e artefatos permanecem em ingles por compatibilidade com arquivos existentes, PyTorch, NumPy, FastAPI ou convencoes de serializacao, como `dataset.npz`, `model.pt`, `scaler.json`, `ood_guard.json`, `positions`, `velocities` e `fallback_events`.

Documentacao completa:

- [`../README.md`](../README.md)
- [`../documentacao/como_rodar.md`](../documentacao/como_rodar.md)
- [`../documentacao/arquitetura.md`](../documentacao/arquitetura.md)
