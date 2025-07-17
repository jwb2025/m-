import re
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


def read_Nodes(node_file):
    Nodes = []
    with open(node_file) as f:                # 用 with 自动关闭
        for line in f:
            data = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', line.strip())
            if len(data) >= 2:                # 至少 x y
                x = float(data[0])
                y = float(data[1])
                Nodes.append([x, y])
    return Nodes


def read_Triangles(triangle_file):
    Triangles = []
    Tags = []
    with open(triangle_file) as f:
        for idx, line in enumerate(f, 1):     # 从 1 开始计数方便报错
            data = re.findall(r'\d+', line.strip())
            if len(data) >= 3:
                v1, v2, v3 = map(int, data[:3])
                # 统一把索引改成 0-based
                Triangles.append([v1-1, v2-1, v3-1])
                Tags.append(0.0)
            else:
                print(f"警告：三角形第 {idx} 行格式不对，已跳过。")
    return Triangles, Tags


def plotMesh(Nodes, Triangles, Tags, showNodeId=True, showTriangleId=True, showTriangleTag=False):
    fig, ax = plt.subplots()
    patches = []
    triangleId = 0
    colors = []
    for triangle in Triangles:
        triangleId = triangleId + 1
        polygon = []
        colors.append(Tags[triangleId-1])
        for id in triangle:
            if id-1 < len(Nodes):  # 检查索引是否有效
                polygon.append(Nodes[id-1])
            else:
                print(f"Error: Node ID {id} is out of range for triangle {triangleId}. Skipping this triangle.")
                break
        else:  # 如果没有 break，继续绘制三角形
            for i in range(len(polygon)):
                line_x = []
                line_y = []
                line_x.append(polygon[i][0])
                if i+1 == len(polygon):
                    line_x.append(polygon[0][0])
                else:
                    line_x.append(polygon[i+1][0])
                line_y.append(polygon[i][1])
                if i+1 == len(polygon):
                    line_y.append(polygon[0][1])
                else:
                    line_y.append(polygon[i+1][1])
                plt.plot(line_x, line_y, 'r-')
            patches.append(Polygon(polygon, closed=True))  # 修复这里
            center_x = sum([_[0] for _ in polygon]) / len(polygon)
            center_y = sum([_[1] for _ in polygon]) / len(polygon)
            if showTriangleId:
                ax.annotate(triangleId, (center_x, center_y), color='red', weight='bold', fontsize=7, ha='center', va='center')
    if showNodeId:
        nodeId = 0
        for node in Nodes:
            nodeId = nodeId + 1
            ax.annotate(nodeId, (node[0], node[1]), color='black', weight='bold', fontsize=9, ha='center', va='center')
    collection = PatchCollection(patches)
    if showTriangleTag:
        collection.set_array(np.array(colors))
    ax.add_collection(collection)
    fig.colorbar(collection, ax=ax)
    ax.axis('equal')
    plt.savefig('mesh_plot.png')  # 保存图形到文件


if __name__ == "__main__":
    node_file = "Nodes.txt"
    triangle_file = "Triangles.txt"
    Nodes = read_Nodes(node_file)
    Triangles, Tags = read_Triangles(triangle_file)
    showNodeId = True
    showTriangleId = True
    plotMesh(Nodes, Triangles, Tags, showNodeId, showTriangleId)









