# Nesse código tem tudo, nós fizemos utilizando o google colab
import random
import time
import json
import uuid
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Gera um trace ID de 16 bytes no formato hexadecimal
def generate_trace_id():
    return format(random.getrandbits(128), '032x')

# Gera um span ID de 8 bytes no formato hexadecimal
def generate_span_id():
    return format(random.getrandbits(64), '016x')

# Trace ID para toda a execução
TRACE_ID = generate_trace_id()
SERVICE_NAME_VALUE = "sorting-service"

# Lista para armazenar todos os spans gerados
jaeger_spans = []

# Configuração do trace provider com o Jaeger
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: SERVICE_NAME_VALUE})
    )
)

# Configuração do Jaeger Exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Exporter para console (debug)
console_exporter = ConsoleSpanExporter()
console_processor = SimpleSpanProcessor(console_exporter)
trace.get_tracer_provider().add_span_processor(console_processor)

# Tracer
tracer = trace.get_tracer(__name__)

# Função para criar um span no formato Jaeger
def create_jaeger_span(name, span_id, parent_span_id, start_time, end_time, tags=None, references=None):
    if tags is None:
        tags = []
    if references is None:
        references = []
    
    # Adiciona tags padrão
    tags.extend([
        {"key": "span.kind", "type": "string", "value": "internal"},
        {"key": "service.name", "type": "string", "value": SERVICE_NAME_VALUE}
    ])
    
    span = {
        "traceID": TRACE_ID,
        "spanID": span_id,
        "operationName": name,
        "references": references,
        "startTime": int(start_time * 1000000),  # Microssegundos
        "duration": int((end_time - start_time) * 1000000),  # Microssegundos
        "tags": tags,
        "logs": [],
        "processID": "p1",
        "warnings": None
    }
    
    if parent_span_id:
        span["references"].append({
            "refType": "CHILD_OF",
            "traceID": TRACE_ID,
            "spanID": parent_span_id
        })
    
    return span

# Função para gerar dados aleatórios
def gerar_dados(tamanho=10000, nome_arquivo="dados.txt"):
    dados = [random.randint(0, 1000000) for _ in range(tamanho)]
    with open(nome_arquivo, "w") as f:
        f.write("\n".join(map(str, dados)))
    print(f"Arquivo '{nome_arquivo}' criado com {tamanho} números.")
    return dados

# Definindo a classe de Algoritmos de Ordenação
class SortingAlgorithm(ABC):
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0
        self.parent_span_id = None

    @abstractmethod
    def sort(self, data):
        pass

    def reset_metrics(self):
        self.comparisons = 0
        self.swaps = 0

    def measure_time(self, data):
        self.reset_metrics()
        algorithm_name = self.__class__.__name__
        span_id = generate_span_id()
        
        # Registrando tempo de início
        start_time = time.time()
        
        # Tags específicas do algoritmo
        tags = [
            {"key": "algorithm.name", "type": "string", "value": algorithm_name},
            {"key": "data_size", "type": "int64", "value": len(data)}
        ]
        
        # Executando o algoritmo
        sorted_data = self.sort(data.copy())
        
        # Registrando tempo de fim
        end_time = time.time()
        
        # Adicionando métricas às tags
        tags.extend([
            {"key": "metrics.comparisons", "type": "int64", "value": self.comparisons},
            {"key": "metrics.swaps", "type": "int64", "value": self.swaps},
            {"key": "execution_time_ms", "type": "float64", "value": (end_time - start_time) * 1000}
        ])
        
        # Criando span para o Jaeger
        span = create_jaeger_span(
            f"{algorithm_name}.sort",
            span_id,
            self.parent_span_id,
            start_time,
            end_time,
            tags
        )
        
        jaeger_spans.append(span)
        
        execution_time = (end_time - start_time) * 1000
        return sorted_data, execution_time, span_id

# Algoritmos de ordenação
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
    RUN = 32

    def sort(self, data):
        arr = data.copy()
        n = len(arr)
        
        # Passo 1: Insertion sort em pequenos subarrays
        for i in range(0, n, self.RUN):
            self.insertion_sort(arr, i, min((i + self.RUN - 1), n - 1))

        # Passo 2: Merge de subarrays
        size = self.RUN
        while size < n:
            for start in range(0, n, 2 * size):
                mid = min(n - 1, start + size - 1)
                end = min((start + 2 * size - 1), (n - 1))
                if mid < end:
                    self.merge(arr, start, mid, end)
            size *= 2
        
        return arr

    def insertion_sort(self, arr, left, right):
        for i in range(left + 1, right + 1):
            key = arr[i]
            j = i - 1
            while j >= left and arr[j] > key:
                self.comparisons += 1
                arr[j + 1] = arr[j]
                j -= 1
                self.swaps += 1
            arr[j + 1] = key

    def merge(self, arr, left, mid, right):
        left_part = arr[left:mid + 1]
        right_part = arr[mid + 1:right + 1]
        
        i = j = 0
        k = left
        while i < len(left_part) and j < len(right_part):
            self.comparisons += 1
            if left_part[i] <= right_part[j]:
                arr[k] = left_part[i]
                i += 1
            else:
                arr[k] = right_part[j]
                j += 1
            k += 1
        
        while i < len(left_part):
            arr[k] = left_part[i]
            i += 1
            k += 1
        
        while j < len(right_part):
            arr[k] = right_part[j]
            j += 1
            k += 1

class SortingTester:
    def __init__(self, algorithms):
        self.algorithms = algorithms

    def run_test(self, data, repetitions=3):
        test_start_time = time.time()
        test_span_id = generate_span_id()
        
        # Criar span para o teste completo
        test_span = create_jaeger_span(
            "SortingAlgorithmsTest",
            test_span_id,
            None,
            test_start_time,
            test_start_time,  # Será atualizado no final
            [
                {"key": "test.repetitions", "type": "int64", "value": repetitions},
                {"key": "test.data_size", "type": "int64", "value": len(data)},
                {"key": "test.algorithms_count", "type": "int64", "value": len(self.algorithms)}
            ]
        )
        
        jaeger_spans.append(test_span)
        
        results = []
        
        for algorithm in self.algorithms:
            algo_start_time = time.time()
            algorithm_name = algorithm.__class__.__name__
            algo_span_id = generate_span_id()
            
            # Definir o pai do algoritmo como o teste
            algorithm.parent_span_id = test_span_id
            
            times = []
            comparisons = []
            swaps = []
            
            # Tags para o span do algoritmo
            algo_tags = [
                {"key": "algorithm.name", "type": "string", "value": algorithm_name},
                {"key": "test.repetitions", "type": "int64", "value": repetitions}
            ]
            
            for rep in range(repetitions):
                rep_start_time = time.time()
                rep_span_id = generate_span_id()
                
                # Definir o pai temporariamente como o span da repetição
                algorithm.parent_span_id = rep_span_id
                
                # Executar o algoritmo
                sorted_data, time_taken, algo_exec_span_id = algorithm.measure_time(data)
                
                # Restaurar o pai para o algoritmo
                algorithm.parent_span_id = algo_span_id
                
                times.append(time_taken)
                comparisons.append(algorithm.comparisons)
                swaps.append(algorithm.swaps)
                
                rep_end_time = time.time()
                
                # Criar span para a repetição
                rep_span = create_jaeger_span(
                    f"{algorithm_name}.repetition.{rep+1}",
                    rep_span_id,
                    algo_span_id,
                    rep_start_time,
                    rep_end_time,
                    [
                        {"key": "repetition.number", "type": "int64", "value": rep + 1},
                        {"key": "execution_time_ms", "type": "float64", "value": time_taken},
                        {"key": "metrics.comparisons", "type": "int64", "value": algorithm.comparisons},
                        {"key": "metrics.swaps", "type": "int64", "value": algorithm.swaps}
                    ]
                )
                
                jaeger_spans.append(rep_span)
            
            # Calcular médias
            avg_time = sum(times) / len(times) if times else 0
            avg_comparisons = sum(comparisons) / len(comparisons) if comparisons else 0
            avg_swaps = sum(swaps) / len(swaps) if swaps else 0
            
            # Adicionar médias às tags
            algo_tags.extend([
                {"key": "metrics.avg_time_ms", "type": "float64", "value": avg_time},
                {"key": "metrics.avg_comparisons", "type": "int64", "value": int(avg_comparisons)},
                {"key": "metrics.avg_swaps", "type": "int64", "value": int(avg_swaps)}
            ])
            
            algo_end_time = time.time()
            
            # Criar span para o algoritmo
            algo_span = create_jaeger_span(
                f"{algorithm_name}.benchmark",
                algo_span_id,
                test_span_id,
                algo_start_time,
                algo_end_time,
                algo_tags
            )
            
            jaeger_spans.append(algo_span)
            
            # Registro para saída do console
            print(f"\n🔹 {algorithm_name} 🔹")
            print(f"Tempo Médio: {avg_time:.2f} ms")
            print(f"Média de Comparações: {int(avg_comparisons)}")
            print(f"Média de Trocas: {int(avg_swaps)}")
            
            # Adicionar aos resultados
            results.append({
                "algorithm": algorithm_name,
                "avg_time_ms": avg_time,
                "avg_comparisons": int(avg_comparisons),
                "avg_swaps": int(avg_swaps)
            })
        
        # Atualizar o span do teste com o tempo de término
        test_end_time = time.time()
        test_span["duration"] = int((test_end_time - test_start_time) * 1000000)
        
        return results

# Tamanho do conjunto de dados
TAMANHO_DO_CONJUNTO = 10000

# Gerar e carregar dados
dados_gerados = gerar_dados(TAMANHO_DO_CONJUNTO)
dados_teste = dados_gerados

# Definir algoritmos a serem testados
algoritmos = [
    BubbleSort(),
    BubbleSortOptimized(),
    InsertionSort(),
    SelectionSort(),
    QuickSort(),
    MergeSort(),
    TimSort()
]

# Executar testes
print(f"Iniciando testes com {len(algoritmos)} algoritmos em {TAMANHO_DO_CONJUNTO} elementos...")
tester = SortingTester(algoritmos)
results = tester.run_test(dados_teste)

# Criar a estrutura completa do Jaeger JSON
jaeger_data = {
    "data": [
        {
            "traceID": TRACE_ID,
            "spans": jaeger_spans,
            "processes": {
                "p1": {
                    "serviceName": SERVICE_NAME_VALUE,
                    "tags": [
                        {"key": "hostname", "type": "string", "value": os.environ.get('COMPUTERNAME', 'unknown')},
                        {"key": "test.data_size", "type": "int64", "value": TAMANHO_DO_CONJUNTO}
                    ]
                }
            },
            "warnings": None
        }
    ],
    "total": 0,
    "limit": 0,
    "offset": 0,
    "errors": None
}

# Salvar JSON no formato do Jaeger
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
json_filename = f"jaeger_sorting_trace_{timestamp}.json"

with open(json_filename, "w") as f:
    json.dump(jaeger_data, f, indent=2)

print(f"\nArquivo JSON para importação no Jaeger criado: {json_filename}")
print(f"Trace ID: {TRACE_ID}")
print("\nPara usar este arquivo no Jaeger:")
print("1. Acesse a interface do Jaeger (geralmente http://localhost:16686)")
print("2. Vá para o menu 'Search' e clique em 'JSON File'")
print("3. Selecione o arquivo JSON gerado")
print("4. Clique em 'Upload JSON'")

# Aguarde um momento para garantir que todos os exportadores terminaram
print("\nAguardando para garantir que todos os spans foram processados...")
time.sleep(3)
