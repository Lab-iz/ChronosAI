# Protocolo Apophis

## Protocolo v1.0

- Cenario: `dados/cenarios/apophis/cenario_apophis.json`
- Horizonte: `180 dias`
- Passo: `1 dia`
- Corpos: `Sun`, `Earth`, `Apophis`
- Saidas: relatorio JSON e resumo em texto em `relatorios/validacao/`

## Procedimento

1. Carregar o fixture offline congelado.
2. Executar a propagacao do motor de referencia.
3. Executar a propagacao hibrida com fallback de seguranca ativo.
4. Comparar trajetorias e distancia Terra-Apophis.
5. Salvar metricas de drift, erro, fallback e tempo de execucao.

## Observacao importante

O fixture incluido e um artefato de regressao, nao um produto final de efemerides. Ele existe para validar o comportamento do software e comparar caminhos de execucao hibrido e baseline de forma reproduzivel.
