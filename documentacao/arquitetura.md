# Arquitetura

O CHRONOS-SEGURO e organizado em quatro camadas operacionais:

1. Camada de fisica: representacao canonica de estado, transformacoes baricentricas, monitoramento de invariantes, integrador rapido e motor de referencia confiavel.
2. Camada de dados: cenarios offline, geracao sintetica generalista, geracao especialista por perturbacao, preprocessamento e escalonamento.
3. Camada de aprendizado: GNN residual, pontuacao OOD e treinamento supervisionado em duas fases.
4. Camada de execucao: propagacao hibrida, guarda de seguranca, orquestracao de recuo fisico, comparativos e interfaces.

O contrato principal de execucao e `SystemState`, que transporta `ids`, `masses`, `positions`, `velocities` e metadados. Esses nomes continuam em ingles por compatibilidade com artefatos, API e arquivos ja gerados.

## Sequencia de um passo hibrido

1. O integrador rapido propoe o proximo estado.
2. A GNN residual estima `delta_acceleration`.
3. O estado candidato corrigido e montado.
4. A guarda de seguranca valida a proposta.
5. Se estiver segura, a correcao e aceita.
6. Se estiver insegura, o sistema recua para o motor de referencia e registra um `FallbackEvent`.

## Organizacao atual

- `chronos_seguro/dominio`: contratos de estado e resultados.
- `chronos_seguro/fisica`: unidades, referenciais, integradores e invariantes.
- `chronos_seguro/dados`: cenarios, geracao de conjuntos, cache e escalonadores.
- `chronos_seguro/modelos`: GNN residual, guarda OOD e incerteza.
- `chronos_seguro/treinamento`: treino, perdas, curriculo e pontos de controle.
- `chronos_seguro/simulacao`: motor hibrido, propagacao, chave segura e missao Apophis.
- `chronos_seguro/servicos`: servicos de alto nivel usados por API, CLI e interface.
- `chronos_seguro/aplicativos`: API web, interface visual e linha de comando.
