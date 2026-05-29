# CHRONOS-SAFE

<<<<<<< HEAD
Repositorio do CHRONOS-SAFE, uma plataforma de simulacao orbital hibrida com motor fisico, IA residual, fallback de seguranca e interface web.

O projeto Python principal fica em [`chronos_safe/`](chronos_safe/README.md). Para rodar a interface pela raiz do repositorio:

=======
CHRONOS-SAFE é uma plataforma de simulação orbital híbrida. O sistema combina um motor físico rápido, correção por Inteligência Artificial (rede neural em grafo residual), uma camada de segurança (OOD guard) e um fallback físico para fornecer previsões orbitais com foco em estabilidade, generalização segura e clareza científica.

## Descrição do Sistema

O sistema integra quatro componentes principais:
1. **Motor Físico Rápido**: Um integrador simples para propor o próximo passo da simulação de forma eficiente.
2. **Correção por IA (Residual GNN)**: Aprende a corrigir o erro do integrador rápido em relação a um modelo de referência, atuando apenas na diferença (residual) em vez de prever toda a física do zero.
3. **Guarda de Segurança (OOD Guard)**: Monitora e detecta anomalias, métricas fora de distribuição e violações de conservação de energia ou momento angular.
4. **Fallback Físico**: Quando a predição da rede neural se mostra insegura ou os limites são excedidos, o sistema aborta a predição da IA e recua automaticamente para a execução do motor físico base.

A plataforma também possui o caso "Apophis" como benchmark principal, atuando como um teste de estresse realista e demonstração do comportamento seguro do sistema fora dos dados sintéticos originais.

## Instalação

Para instalar o projeto e suas dependências de Machine Learning e ciência, execute o comando abaixo a partir da raiz do projeto:

```powershell
python -m pip install -e ".[ml,science,dev]"
```

Caso deseje utilizar o integrador `rebound` (opcional):

```powershell
python -m pip install -r requirements-rebound.txt
```

## Instruções de Execução

A forma mais simples de utilizar o projeto e visualizar a simulação é através da interface web.

1. Execute o script principal:
>>>>>>> 3714e51ee15899694ba515e443224b640b045c7d
```powershell
python run.py
```

<<<<<<< HEAD
Documentacao util:

- [Como rodar](chronos_safe/docs/como_rodar.md)
- [Deploy no Render](chronos_safe/docs/render_deploy.md)
- [Arquitetura](chronos_safe/docs/architecture.md)
- [Metodologia](chronos_safe/docs/methodology.md)
- [Protocolo Apophis](chronos_safe/docs/apophis_protocol.md)
=======
2. Abra o seu navegador e acesse a URL:
```text
http://127.0.0.1:8000/
```

Na interface web, você poderá visualizar a demo 3D, conferir o relatório do semáforo de riscos e rodar simulações validando a passagem do asteróide Apophis.

## Interface de Linha de Comando (CLI)

O sistema também inclui ferramentas CLI completas para pesquisadores gerarem dados e treinarem os modelos.

```powershell
# Gerar os dados sintéticos de treinamento
chronos generate-generalist
chronos generate-specialist

# Treinar os modelos de correção
chronos train-generalist
chronos train-specialist

# Executar validações via terminal
chronos simulate
chronos validate-apophis
```

> **Dica**: Caso o comando `chronos` não seja reconhecido no seu PATH, você pode executá-lo diretamente pelo Python executando `python -m chronos_safe.apps.cli.main <comando>`.

## Deploy (Render)

A aplicação inclui um arquivo `render.yaml` na raiz para deploy simplificado em plataformas de nuvem como o Render. A configuração padrão expõe a porta `8000` via Uvicorn. Para mais detalhes, verifique a pasta `docs/`.
>>>>>>> 3714e51ee15899694ba515e443224b640b045c7d
