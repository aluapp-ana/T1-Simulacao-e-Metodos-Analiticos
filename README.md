# T1 - Simulador de Rede de Filas (topologia genérica)

## Arquitetura

- `fila.py` — classe `Fila` (servidores, capacidade, intervalos de chegada
  e atendimento, estado atual, perdas, tempos acumulados por estado, e a
  tabela de roteamento `rotas`).
- `evento.py` — classe `Evento`: tempo + índice da fila de **origem** e da
  fila de **destino** (`-1` representa o exterior da rede).
- `escalonador.py` — fila de prioridade mínima (heap) pelo tempo do evento.
- `gerador_pseudoaleatorio.py` — gerador congruente linear (`Gerador`),
  M grande (2^32), parâmetros configuráveis.
- `rede.py` — `RedeDeFilas`: guarda a `listaDeFilas` e valida o roteamento
  de cada fila (probabilidades somando 1.0, destinos existentes).
- `simulador_rede.py` — motor da simulação: **um único** procedimento
  (`ProcessaEvento`) generaliza chegada, saída e passagem, porque todos
  os três casos se resumem a "origem perde um cliente (se não for
  exterior) e destino ganha um cliente (se não for exterior)".
- `carregador_yaml.py` — lê um arquivo `.yml` e monta a `RedeDeFilas`.
- `main.py` — ponto de entrada.

## Como rodar

```bash
pip install pyyaml  # única dependência externa 
python3 main.py modelo_exemplo.yml
```

Sem argumento, roda `modelo_exemplo.yml` por padrão. O resultado é
impresso no terminal e gravado em `resultado_simulacao.txt`.

## Como descrever um modelo (.yml)

```yaml
simulacao:
  seed: 7                    # opcional
  limite_aleatorios: 100000  # a simulação encerra ao consumir esse tanto

filas:
  - nome: "Fila 1"
    servers: 1
    capacity: 3
    chegada:                 # OMITIR se a fila não tem chegada externa
      min: 1
      max: 2
      primeiro_cliente: 1.0
    atendimento:
      min: 2
      max: 3
    roteamento:               # OMITIR = 100% para o exterior (padrão)
      - destino: 1             # índice (0-based) de outra fila na lista
        probabilidade: 0.2
      - destino: 2
        probabilidade: 0.3
      - destino: -1             # -1 = exterior (sai do sistema)
        probabilidade: 0.5

  - nome: "Fila 2"
    servers: 2
    capacity: 4
    atendimento:
      min: 3
      max: 5
    # sem "chegada" e sem "roteamento": só recebe de outras filas e
    # sai 100% para o exterior ao terminar o atendimento
```

O índice de cada fila é a posição dela na lista `filas:` (a primeira é 0,
a segunda é 1, etc.) — é esse índice que aparece em `destino:` no
roteamento.

## Arquivos de validação entregues

- `modelo_exemplo.yml` / `resultado_simulacao_modelo_exemplo.txt` — rede
  de 3 filas do enunciado do módulo (Fila 1 roteando 20% → Fila 2, 30% →
  Fila 3, 50% → exterior). **Obs.:** o enunciado não especificou o tempo
  do primeiro cliente nem o nº de aleatórios para esta rede especificamente
  (diferente das etapas anteriores); usamos `primeiro_cliente = 1.0`
  (mínimo do intervalo de chegada) e `limite_aleatorios = 100000`, seguindo
  o padrão das entregas anteriores. Ajuste no `.yml` se o professor pedir
  outros valores.
- `modelo_tandem.yml` / `resultado_tandem.txt` — a rede tandem (Fila 1 →
  Fila 2) já validada na etapa anterior, incluída aqui só como checagem:
  reproduz exatamente o mesmo resultado de antes (tempo global
  100979.0179), confirmando que a generalização não alterou o
  comportamento do simulador.