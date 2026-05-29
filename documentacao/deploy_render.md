# Deploy no Render

Este projeto foi preparado para ser avaliado no Render como uma aplicacao web unica, sem build frontend separado.

## Objetivo

Subir o CHRONOS-SEGURO a partir da raiz do repositorio, usando o pacote `chronos_seguro`, a API FastAPI e a interface web integrada.

## O que ja esta pronto

O repositorio possui:

- [`render.yaml`](../render.yaml)
- [`.python-version`](../.python-version)

O `render.yaml` configura:

- `rootDir: .`
- instalacao com `python -m pip install -e .`
- servidor com `uvicorn`
- `healthCheckPath: /health`
- navegador desativado em producao
- modo CPU
- `REBOUND` desativado por padrao no deploy web
- Python `3.12.8`

Esse perfil foi otimizado para:

- subir mais rapido;
- falhar menos no build;
- entregar a demo 3D e a validacao Apophis sem exigir treino pesado;
- manter a interface compreensivel para avaliacao.

## Antes de subir

Lista rapida:

1. Confirme que o repositorio esta atualizado no GitHub.
2. Confirme que [`render.yaml`](../render.yaml) esta na raiz do repositorio.
3. Confirme que [`.python-version`](../.python-version) tambem esta na raiz.
4. Confirme que a interface local abre com `python run.py`.

## Opcao recomendada: Blueprint

1. Suba o repositorio no GitHub.
2. Entre em `https://render.com/`.
3. Clique em `New +`.
4. Clique em `Blueprint`.
5. Conecte sua conta do GitHub ao Render, se ainda nao estiver conectada.
6. Selecione o repositorio do CHRONOS-SEGURO.
7. O Render deve detectar o arquivo `render.yaml`.
8. Confirme a criacao do servico.
9. Aguarde o build e o primeiro deploy.
10. Abra a URL publica gerada pelo Render.

## Opcao manual: Web Service

Se quiser configurar manualmente no painel:

1. Clique em `New +`.
2. Clique em `Web Service`.
3. Selecione o repositorio.
4. Preencha:

- `Name`: `chronos-seguro`
- `Root Directory`: deixe vazio ou use `.`
- `Runtime`: `Python 3`
- `Build Command`: `python -m pip install -e .`
- `Start Command`: `python -m uvicorn chronos_seguro.aplicativos.api.principal:app --host 0.0.0.0 --port $PORT`

5. Adicione estas variaveis de ambiente:

- `PYTHON_VERSION=3.12.8`
- `CHRONOS_OPEN_BROWSER=false`
- `CHRONOS_DEVICE=cpu`
- `CHRONOS_USE_REBOUND_IF_AVAILABLE=false`
- `CHRONOS_LOG_LEVEL=INFO`

6. Defina o `Health Check Path` como:

```text
/health
```

7. Crie o servico e aguarde o deploy.

## O que o avaliador deve fazer

1. Clicar em `1. Ver demo 3D`.
2. Observar a orbita 3D.
3. Clicar em `2. Rodar teste Apophis`.
4. Ler o painel `Relatorio guiado`.

## Por que isso funciona bem para avaliacao

O deploy foi pensado para uma pessoa leiga conseguir usar sem treinamento previo. A interface destaca:

- visualizacao 3D;
- caso Apophis;
- resumo interpretado das metricas.

Assim, o avaliador entende rapidamente:

- o que esta sendo simulado;
- qual e o caso de validacao mais importante;
- como o sistema compara o modo hibrido com a referencia fisica.

## O que fica disponivel no deploy web

No perfil padrao do Render, o foco e demonstracao e validacao.

Fica pronto para uso:

- interface web;
- visualizacao 3D;
- validacao Apophis;
- simulacao com fallback;
- relatorio guiado.

Pode ficar indisponivel ou limitado:

- treino de modelos;
- carregamento de pontos de controle PyTorch muito grandes;
- uso de `REBOUND` compilado no servidor.

Isso e intencional. O deploy publico foi otimizado para avaliacao, nao para treino pesado.

## Persistencia de arquivos

Por padrao, trate o filesystem do Web Service como temporario.

Arquivos gerados em runtime, como:

- relatorios;
- conjuntos de dados;
- pontos de controle;
- caches;

podem nao sobreviver a novo deploy, restart ou troca de instancia.

Para demonstracao publica, isso nao e um problema. Para uso persistente, use disco persistente no Render ou armazene artefatos fora do servico web.

## Validacao pos-deploy

Assim que o Render subir a aplicacao:

1. Abra `/health` e confirme que a resposta esta `ok`.
2. Abra `/`.
3. Clique em `1. Ver demo 3D`.
4. Confirme que o grafico 3D aparece.
5. Clique em `2. Rodar teste Apophis`.
6. Confirme que o `Relatorio guiado` aparece com metricas e semaforo.

## Nova versao

Fluxo recomendado:

1. Fazer commit local.
2. Fazer push para o GitHub.
3. Aguardar o auto deploy do Render.
4. Abrir a URL publica.
5. Validar `demo 3D + Apophis`.

## Observacao sobre REBOUND

O deploy padrao nao depende de `rebound` para funcionar.

Se o ambiente conseguir instalar `rebound`, o sistema usa o baseline fisico oficial automaticamente. Se nao conseguir, o backend continua operando com o motor de referencia em NumPy, permitindo demonstracao e avaliacao funcional.
