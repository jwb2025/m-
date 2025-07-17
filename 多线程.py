import threading
import queue
import re

def read_nodes(file_path, start, end, result_queue):
    """
    读取节点信息
    :param file_path: 文件路径
    :param start: 起始行
    :param end: 结束行
    :param result_queue: 结果队列
    """
    nodes = []
    with open(file_path, 'r') as f:
        lines = f.readlines()[start:end]
        for line in lines:
            data = re.findall(r'\d+\.?\d*', line)
            if len(data) == 3:
                node = list(map(float, data))
                nodes.append(node)
    result_queue.put(nodes)

def read_triangles(file_path, start, end, result_queue):
    """
    读取三角形信息
    :param file_path: 文件路径
    :param start: 起始行
    :param end: 结束行
    :param result_queue: 结果队列
    """
    triangles = []
    with open(file_path, 'r') as f:
        lines = f.readlines()[start:end]
        for line in lines:
            data = re.findall(r'\d+', line)
            if len(data) == 3:
                triangle = list(map(int, data))
                triangles.append(triangle)
    result_queue.put(triangles)

def parallel_read(nodes_file, triangles_file, num_threads):
    """
    并行读取m格式三角网格文件
    :param nodes_file: 节点文件路径
    :param triangles_file: 三角形文件路径
    :param num_threads: 线程数量
    :return: 节点列表和三角形列表
    """
    nodes_queue = queue.Queue()
    triangles_queue = queue.Queue()

    # 读取节点文件
    with open(nodes_file, 'r') as f:
        total_lines = sum(1 for _ in f)
    lines_per_thread = total_lines // num_threads
    threads = []
    for i in range(num_threads):
        start = i * lines_per_thread
        end = start + lines_per_thread if i < num_threads - 1 else total_lines
        thread = threading.Thread(target=read_nodes, args=(nodes_file, start, end, nodes_queue))
        threads.append(thread)
        thread.start()

    # 读取三角形文件
    with open(triangles_file, 'r') as f:
        total_lines = sum(1 for _ in f)
    lines_per_thread = total_lines // num_threads
    for i in range(num_threads):
        start = i * lines_per_thread
        end = start + lines_per_thread if i < num_threads - 1 else total_lines
        thread = threading.Thread(target=read_triangles, args=(triangles_file, start, end, triangles_queue))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 整合结果
    nodes = []
    while not nodes_queue.empty():
        nodes.extend(nodes_queue.get())
    triangles = []
    while not triangles_queue.empty():
        triangles.extend(triangles_queue.get())

    return nodes, triangles

if __name__ == "__main__":
    nodes_file = "Nodes.txt"
    triangles_file = "Triangles.txt"
    num_threads = 4

    nodes, triangles = parallel_read(nodes_file, triangles_file, num_threads)
    print("Nodes:", nodes)
    print("Triangles:", triangles)