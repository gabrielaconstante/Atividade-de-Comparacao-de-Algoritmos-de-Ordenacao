# Atividade-de-Comparacao-de-Algoritmos-de-Ordenacao

# Código-Fonte Documentado e Organizado

O código implementa diferentes algoritmos de ordenação para avaliar seu desempenho com base em tempo de execução, comparações e trocas realizadas. Além disso, utiliza o padrão de design Strategy para permitir a troca de algoritmos de ordenação sem alterar o código cliente.

## Estrutura do Código

1. Função gerar\_dados: Cria um arquivo de dados aleatórios para testar os algoritmos de ordenação.
1. Função carregar\_dados: Carrega os dados a partir de um arquivo de texto para execução dos testes.
1. Classe SortingAlgorithm: Define a interface para os algoritmos de ordenação e métodos para medir o desempenho (tempo, comparações, trocas).
1. Classe BubbleSort: Implementa o algoritmo de ordenação BubbleSort.
1. Classe SortingTester: Executa os testes de desempenho para os algoritmos de ordenação e coleta as métricas.
1. OpenTelemetry: Utilizado para geração de logs e rastreamento do tempo de execução dos algoritmos.

## Explicação do Uso do Padrão Strategy

O padrão Strategy é utilizado para permitir que diferentes algoritmos de ordenação sejam aplicados sem que seja necessário modificar o código que executa os testes. O código define uma interface SortingAlgorithm com um método abstrato sort, e cada classe de algoritmo, como BubbleSort, QuickSort, etc., implementa esse método. O cliente, SortingTester, pode então alterar a estratégia de ordenação ao fornecer diferentes instâncias de algoritmos.

Este padrão proporciona flexibilidade e facilita a manutenção do código, permitindo adicionar ou modificar algoritmos de ordenação sem afetar o código de teste.

Descrição do Processo de Geração dos Dados

1. A função gerar\_dados gera uma lista de números aleatórios entre 0 e 1.000.000.
1. Esses números são salvos em um arquivo de texto, que é posteriormente carregado para o teste de algoritmos de ordenação.

## Métricas e Gráficos Comparativos de Desempenho

A seguir estão as métricas coletadas para cada algoritmo de ordenação, em um cenário de 10.000 números:


| Algoritmo             | Tempo Médio (ms) | Comparações  | Trocas      |
|----------------------|----------------|-------------|------------|
| BubbleSort          | 8455.43        | 49.995.000  | 25.116.117 |
| BubbleSortOptimized | 8426.84        | 49.994.810  | 25.116.117 |
| InsertionSort       | 4241.61        | 25.116.117  | 25.116.117 |
| SelectionSort       | 4214.03        | 49.995.000  | 9.989      |
| QuickSort          | 21.51          | 155.507     | 77.379     |
| MergeSort          | 31.09          | 120.458     | 61.295     |
| TimSort           | 34.57          | 163.084     | 116.681    |

## Descrição da Ferramenta Utilizada para Logs e Análise dos Resultados

O OpenTelemetry foi utilizado para monitoramento e rastreamento de execução. Ele permite registrar e analisar o tempo de execução dos algoritmos, coletando métricas como tempo de execução, número de comparações e trocas, além de facilitar a análise em tempo real.

No código, o ConsoleSpanExporter foi usado para exportar os logs para o console. Isso proporciona visibilidade sobre cada operação realizada durante a execução dos testes.

## Conclusão: Qual Algoritmo Apresentou Melhor Desempenho em Diferentes Cenários?

Analisando os resultados, o QuickSort apresentou o melhor desempenho, com um tempo médio de 21,51 ms, seguido de MergeSort e TimSort. Esses algoritmos têm uma complexidade de tempo mais baixa em comparação aos algoritmos de ordenação quadrática, como BubbleSort e InsertionSort.

* QuickSort: Destacou-se devido à sua implementação eficiente, com complexidade média de O(n log n). Ele executa com muito mais rapidez do que os algoritmos de complexidade O(n²), como o BubbleSort.
* MergeSort: Também eficiente, mas com um overhead devido ao uso de espaço adicional para a união de sublistas.

## Vale a Pena Usar "Dividir e Conquistar"?

Sim, vale a pena. Algoritmos baseados na técnica de "Dividir e Conquistar", como QuickSort e MergeSort, são mais eficientes, principalmente em cenários com grandes volumes de dados, como o caso deste teste. Esses algoritmos têm uma complexidade de tempo O(n log n), o que os torna significativamente mais rápidos do que os algoritmos O(n²) como BubbleSort.

Portanto, se a aplicação exige desempenho em larga escala, a utilização de algoritmos como QuickSort ou MergeSort é altamente recomendada, enquanto algoritmos como BubbleSort ou InsertionSort devem ser evitados para grandes conjuntos de dados.
