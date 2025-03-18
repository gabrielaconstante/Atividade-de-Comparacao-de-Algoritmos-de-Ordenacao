# Nesse código tem tudo, nós fizemos utilizando o google colab, por 
# conta disso, preferimos trabalhar com todos os códigos no mesmo arquivo, 
# mas, para "facilitar" a leitura, criamos um arquivo com cada código também

import random
import time
from abc import ABC, abstractmethod
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter  # Novo import
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Configuração do trace provider com o Jaeger
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "sorting-service"})
    )
)

# Configuração do Jaeger Exporter para enviar traces para o Jaeger local
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",  # Jaeger está rodando localmente
    agent_port=5775,  # Porta padrão do Jaeger Agent
)

# Adicionando o exporter à pipeline de processamento de spans
span_processor = SimpleSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Criando o tracer
tracer = trace.get_tracer(__name__)

# Função para gerar dados aleatórios
def gerar_dados(tamanho=10000, nome_arquivo="dados.txt"):
    dados = [random.randint(0, 1000000) for _ in range(tamanho)]
    with open(nome_arquivo, "w") as f:
        f.write("\n".join(map(str, dados)))
    print(f"Arquivo '{nome_arquivo}' criado com {tamanho} números.")

TAMANHO_DO_CONJUNTO = 10000
gerar_dados(TAMANHO_DO_CONJUNTO)

# Função para carregar os dados do arquivo
def carregar_dados(nome_arquivo="dados.txt"):
    with open(nome_arquivo, "r") as f:
        return [int(line.strip()) for line in f.readlines()]

dados_teste = carregar_dados()
print(f"{len(dados_teste)} números carregados para os testes!")

# Definindo a classe de Algoritmos de Ordenação
class SortingAlgorithm(ABC):
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0

    @abstractmethod
    def sort(self, data):
        pass

    def reset_metrics(self):
        self.comparisons = 0
        self.swaps = 0

    def measure_time(self, data):
        self.reset_metrics()
        start_time = time.time()
        with tracer.start_as_current_span(f"Sorting Algorithm Execution"):
            sorted_data = self.sort(data)
        end_time = time.time()
        return sorted_data, (end_time - start_time) * 1000

# Definindo os algoritmos de ordenação (BubbleSort, InsertionSort, etc)
class BubbleSort(SortingAlgorithm):
    def sort(self, data):
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                self.comparisons += 1
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    self.swaps += 1
        return arr

class BubbleSortOptimized(SortingAlgorithm):
    def sort(self, data):
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                self.comparisons += 1
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    self.swaps += 1
                    swapped = True
            if not swapped:
                break
        return arr

class InsertionSort(SortingAlgorithm):
    def sort(self, data):
        arr = data.copy()
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                self.comparisons += 1
                arr[j + 1] = arr[j]
                j -= 1
                self.swaps += 1
            arr[j + 1] = key
        return arr

class SelectionSort(SortingAlgorithm):
    def sort(self, data):
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                self.comparisons += 1
                if arr[j] < arr[min_idx]:
                    min_idx = j
            if min_idx != i:
                arr[i], arr[min_idx] = arr[min_idx], arr[i]
                self.swaps += 1
        return arr

class QuickSort(SortingAlgorithm):
    def sort(self, data):
        arr = data.copy()
        self._quicksort(arr, 0, len(arr) - 1)
        return arr

    def _quicksort(self, arr, low, high):
        if low < high:
            pi = self._partition(arr, low, high)
            self._quicksort(arr, low, pi - 1)
            self._quicksort(arr, pi + 1, high)

    def _partition(self, arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            self.comparisons += 1
            if arr[j] < pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                self.swaps += 1
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        self.swaps += 1
        return i + 1

class MergeSort(SortingAlgorithm):
    def sort(self, data):
        arr = data.copy()
        self._mergesort(arr)
        return arr

    def _mergesort(self, arr):
        if len(arr) > 1:
            mid = len(arr) // 2
            left_half = arr[:mid]
            right_half = arr[mid:]

            self._mergesort(left_half)
            self._mergesort(right_half)

            i = j = k = 0
            while i < len(left_half) and j < len(right_half):
                self.comparisons += 1
                if left_half[i] < right_half[j]:
                    arr[k] = left_half[i]
                    i += 1
                else:
                    arr[k] = right_half[j]
                    j += 1
                    self.swaps += 1
                k += 1

            while i < len(left_half):
                arr[k] = left_half[i]
                i += 1
                k += 1
            while j < len(right_half):
                arr[k] = right_half[j]
                j += 1
                k += 1

class TimSort(SortingAlgorithm):
    def sort(self, data):
        arr = data.copy()
        arr.sort()
        return arr
class SortingTester:
    def __init__(self, algorithms):
        self.algorithms = algorithms

    def run_test(self, data, repetitions=3):
        for algorithm in self.algorithms:
            times = []
            comparisons = []
            swaps = []
            algorithm_name = algorithm.__class__.__name__

            for _ in range(repetitions):
                with tracer.start_as_current_span(f"Test {algorithm_name}") as span:
                    sorted_data, time_taken = algorithm.measure_time(data)
                    times.append(time_taken)
                    comparisons.append(algorithm.comparisons)
                    swaps.append(algorithm.swaps)

            print(f"\n🔹 {algorithm_name} 🔹")
            print(f"Tempo Médio: {sum(times) / len(times):.2f} ms")
            print(f"Média de Comparações: {int(sum(comparisons) / len(comparisons))}")
            print(f"Média de Trocas: {int(sum(swaps) / len(swaps))}")

# Inicializando e rodando o teste
algoritmos = [
    BubbleSort(),
    BubbleSortOptimized(),
    InsertionSort(),
    SelectionSort(),
    QuickSort(),
    MergeSort(),
    TimSort()]

tester = SortingTester(algoritmos)
tester.run_test(dados_teste)
