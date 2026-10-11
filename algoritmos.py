"""Algoritmos próprios; não alteram a entrada."""

def heap_sort(items, key=lambda x: x, reverse=False):
    data = list(items)
    def greater(a, b):
        return key(a) < key(b) if reverse else key(a) > key(b)
    def sift(root, size):
        while 2 * root + 1 < size:
            child = 2 * root + 1
            if child + 1 < size and greater(data[child + 1], data[child]):
                child += 1
            if not greater(data[child], data[root]):
                break
            data[root], data[child] = data[child], data[root]
            root = child
    for root in range(len(data)//2 - 1, -1, -1):
        sift(root, len(data))
    for end in range(len(data)-1, 0, -1):
        data[0], data[end] = data[end], data[0]
        sift(0, end)
    return data

def merge_sort(items, key=lambda x: x, reverse=False):
    data = list(items)
    if len(data) < 2:
        return data
    middle = len(data)//2
    left = merge_sort(data[:middle], key, reverse)
    right = merge_sort(data[middle:], key, reverse)
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        take_left = key(left[i]) >= key(right[j]) if reverse else key(left[i]) <= key(right[j])
        if take_left:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

def ordenar(livros, campo='titulo', crescente=True, algoritmo='Merge Sort'):
    if campo not in {'id', 'titulo', 'autor', 'genero', 'ano', 'disponiveis', 'popularidade', 'nota_media'}:
        raise ValueError('Campo de ordenação inválido.')
    if algoritmo not in {'Heap Sort', 'Merge Sort'}:
        raise ValueError('Algoritmo inválido.')
    with_value = [x for x in livros if x.get(campo) is not None]
    missing = [x for x in livros if x.get(campo) is None]
    def key(item):
        value = item[campo]
        return value.casefold() if isinstance(value, str) else value
    sort = heap_sort if algoritmo == 'Heap Sort' else merge_sort
    return sort(with_value, key=key, reverse=not crescente) + missing
