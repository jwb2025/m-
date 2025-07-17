import mmap
import os
from multiprocessing import Pool

def read_nodes(nodes_file, start, end):
    """
    读取节点信息
    :param nodes_file: 节点文件路径
    :param start: 映射起始位置
    :param end: 映射结束位置
    :return: 节点列表
    """
    nodes = []
    with open(nodes_file, 'r+b') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        mm.seek(start)
        data = mm.read(end - start)
        lines = data.decode('utf-8').splitlines()
        for line in lines:
            if line.strip():
                try:
                    node = list(map(float, line.split()))
                    if len(node) == 3:  # 确保每行有三个坐标值
                        nodes.append(node)
                    else:
                        print(f"警告：节点行 '{line.strip()}' 格式不正确，跳过该行。")
                except ValueError as e:
                    print(f"警告：无法解析节点行 '{line.strip()}'，错误：{e}")
        mm.close()
    return nodes

def read_triangles(triangles_file, start, end):
    """
    读取三角形信息
    :param triangles_file: 三角形文件路径
    :param start: 映射起始位置
    :param end: 映射结束位置
    :return: 三角形列表
    """
    triangles = []
    with open(triangles_file, 'r+b') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        mm.seek(start)
        data = mm.read(end - start)
        lines = data.decode('utf-8').splitlines()
        for line in lines:
            if line.strip():
                try:
                    triangle = list(map(int, line.split()))
                    if len(triangle) == 3:  # 确保每行有三个顶点索引
                        triangles.append(triangle)
                    else:
                        print(f"警告：三角形行 '{line.strip()}' 格式不正确，跳过该行。")
                except ValueError as e:
                    print(f"警告：无法解析三角形行 '{line.strip()}'，错误：{e}")
        mm.close()
    return triangles

def parallel_read(nodes_file, triangles_file, num_threads):
    """
    并行读取m格式三角网格文件
    :param nodes_file: 节点文件路径
    :param triangles_file: 三角形文件路径
    :param num_threads: 线程数量
    :return: 节点列表和三角形列表
    """
    # 获取文件大小
    nodes_file_size = os.path.getsize(nodes_file)
    triangles_file_size = os.path.getsize(triangles_file)

    # 计算每个线程处理的文件大小
    nodes_chunk_size = nodes_file_size // num_threads
    triangles_chunk_size = triangles_file_size // num_threads

    # 创建线程池
    with Pool(processes=num_threads) as pool:
        # 读取节点信息
        nodes_results = []
        for i in range(num_threads):
            start = i * nodes_chunk_size
            end = start + nodes_chunk_size if i < num_threads - 1 else nodes_file_size
            nodes_results.append(pool.apply_async(read_nodes, (nodes_file, start, end)))

        # 读取三角形信息
        triangles_results = []
        for i in range(num_threads):
            start = i * triangles_chunk_size
            end = start + triangles_chunk_size if i < num_threads - 1 else triangles_file_size
            triangles_results.append(pool.apply_async(read_triangles, (triangles_file, start, end)))
        # 获取结果
        nodes = [node for result in nodes_results for node in result.get()]
        triangles = [triangle for result in triangles_results for triangle in result.get()]
    return nodes, triangles

if __name__ == "__main__":
    nodes_file = "Nodes.txt"
    triangles_file = "Triangles.txt"
    num_threads = 4

    nodes, triangles = parallel_read(nodes_file, triangles_file, num_threads)
    print("Nodes:", nodes)
    print("Triangles:", triangles)

