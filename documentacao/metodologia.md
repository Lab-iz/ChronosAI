# Metodologia

## Alvo de treinamento

O modelo aprende uma aceleracao residual efetiva:

```text
delta_acceleration = (v_professor_proximo - v_rapido_proximo) / dt
```

Esse alvo mantem a rede ligada ao erro de truncamento do integrador rapido, em vez de pedir que a IA aprenda todo o estado fisico do zero.

## Geracao de dados

- Dados generalistas: sistemas orbitais sinteticos com primario de massa solar e corpos secundarios aleatorizados.
- Dados especialistas: perturbacoes em torno de um fixture congelado do Sistema Solar ou do cenario Apophis.
- Todos os estados sao padronizados em coordenadas baricentricas e ordenacao canonica de corpos.

## Avaliacao com seguranca em primeiro lugar

Loss isolada nao e tratada como sucesso. Cada modelo tambem precisa ser avaliado com:

- erro de propagacao em multiplos passos;
- drift de energia;
- drift de momento angular;
- frequencia de fallback;
- tempo de execucao contra o motor de referencia.

## Estrategia OOD

A guarda OOD da v1.0 usa uma pontuacao parecida com Mahalanobis diagonal sobre caracteristicas achatadas do estado, com limiar ajustado no conjunto de treino. O desenho deixa espaco para dropout Monte Carlo e desacordo de ensemble em versoes futuras.
