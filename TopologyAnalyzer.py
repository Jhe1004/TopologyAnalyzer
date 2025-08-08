# -*- coding: utf-8 -*-
import os
import sys
import csv
import re  # 导入 re 模块，用于正则表达式操作

# 尝试导入 ete3，如果失败则提示安装
try:
    from ete3 import Tree
except ImportError:
    print("错误：需要 'ete3' 库。请使用 'pip install ete3' 命令安装它。")
    sys.exit(1)

# --- 用户配置区域 ---

# 1. 包含 Newick 树文件的文件夹路径
TREE_DIR = './'

# 2. 树文件名的后缀 (例如，RAxML 输出的 RAxML_bipartitions.result)
#    注意：脚本逻辑是检查文件名是否以这个字符串“结尾”
TREE_SUFFIX = '_cds'

# 3. 关键物种名称列表
SPECIES_A_LIST = [
    "Clematis_repens.fasta.transdecoder.pep",
    "Clematis_otophora.fasta.transdecoder.pep"  # 示例，可替换为实际名称
]

SPECIES_B_LIST = [
    "Clematis_songorica_kashi.fasta.transdecoder.pep", "Clematis_songorica_aleotai.fasta.transdecoder.pep", "Clematis_songorica_hami.fasta.transdecoder.pep", "Clematis_songorica_wulumuqi.fasta.transdecoder.pep"  # 示例，可替换为实际名称
]

# 4. 需要统计亲缘关系的物种列表 (SOI)
SPECIES_OF_INTEREST = [
    "Clematis_glauca_liancheng.fasta.transdecoder.pep", "Clematis_intricata_2019052001.fasta.transdecoder.pep", "Clematis_intricata_weijing.fasta.transdecoder.pep", "Clematis_akebioides_wenchuan.fasta.transdecoder.pep", "Clematis_akebioides_ganzi.fasta.transdecoder.pep", "Clematis_tangutica_yongchang.fasta.transdecoder.pep", "Clematis_tangutica_maerkang.fasta.transdecoder.pep", "Clematis_tenuifolia.fasta.transdecoder.pep"
    # 在这里添加更多物种名称
]

# 5. 【新增功能】节点支持率阈值
# 只有当关键的共同祖先节点支持率 > 此值时，才认为亲缘关系更近
SUPPORT_THRESHOLD = 70

# 6. 输出 CSV 文件的名称
OUTPUT_CSV_FILE = 'relationship_results_with_support.csv'

# 7. 【新增】用于存放修复后树文件的新文件夹名称
MODIFIED_TREE_DIR = './fixed_trees/'


# --- 脚本主逻辑 ---

def find_species_node(tree, species_name):
    """在树中查找指定物种的叶节点"""
    try:
        nodes = tree.search_nodes(name=species_name)
        if len(nodes) == 1:
            return nodes[0]
        elif len(nodes) > 1:
            print(f"警告: 物种 '{species_name}' 在树 '{tree.name if hasattr(tree, 'name') else 'Unnamed'}' 中找到多个节点。将使用第一个。")
            return nodes[0]
        else:
            return None
    except Exception as e:
        print(f"错误: 在查找物种 '{species_name}' 时发生错误: {e}")
        return None

# 【修改】函数签名增加了 modified_tree_dir 参数
def analyze_relationships(tree_dir, tree_suffix, species_a_list, species_b_list, soi_list, support_threshold, output_csv_file, modified_tree_dir):
    """
    分析亲缘关系并将结果保存到 CSV 文件。
    """
    results = []
    total_files_processed = 0
    total_trees_analyzed = 0

    print(f"开始分析目录 '{tree_dir}' 中以 '{tree_suffix}' 结尾的树文件...")
    print(f"支持率阈值设置为: > {support_threshold}")
    print(f"物种 A 列表: {', '.join(species_a_list)}")
    print(f"物种 B 列表: {', '.join(species_b_list)}")
    print(f"待分析物种 (SOI): {', '.join(soi_list)}")
    # 【新增】告知用户修复后的树文件存放位置
    print(f"修复后的树将被保存到: '{os.path.abspath(modified_tree_dir)}'")
    print("-" * 30)

    if not os.path.isdir(tree_dir):
        print(f"错误: 目录 '{tree_dir}' 不存在或不是一个有效的目录。")
        sys.exit(1)
        
    # 【新增】创建用于存放修复后树文件的目录，如果目录已存在则什么也不做
    try:
        os.makedirs(modified_tree_dir, exist_ok=True)
    except OSError as e:
        print(f"错误: 无法创建目录 '{modified_tree_dir}': {e}")
        sys.exit(1)

    # 遍历树文件
    for filename in os.listdir(tree_dir):
        if filename.endswith(tree_suffix):
            filepath = os.path.join(tree_dir, filename)
            total_files_processed += 1
            print(f"\n正在处理文件: {filename}")
            
            try:
                # 1. 读取原始树文件内容
                with open(filepath, 'r', encoding='utf-8') as f:
                    newick_string = f.read().strip()
                
                if not newick_string:
                    print(f"  警告: 文件 '{filename}' 为空，已跳过。")
                    continue

                # 2. 修复 newick 字符串
                modified_newick_string = re.sub(r'\)(?=[:,\)])', r')0', newick_string)

                # 3. 【新增】将修复后的树字符串保存到新文件
                try:
                    output_filepath = os.path.join(modified_tree_dir, filename)
                    with open(output_filepath, 'w', encoding='utf-8') as f_out:
                        f_out.write(modified_newick_string)
                except IOError as e:
                    # 如果保存失败，只打印警告，不中断主程序
                    print(f"  警告: 无法将修复后的树保存到 '{output_filepath}': {e}")

                # 4. 尝试从修复后的字符串加载树
                tree = Tree(modified_newick_string, format=2)

            except Exception as e:
                print(f"  错误: 自动修复并使用 format=2 解析树文件 '{filepath}' 失败。文件可能存在更复杂的格式问题。错误信息: {e}")
                continue

            total_trees_analyzed += 1
            tree.name = filename

            # (后续的分析逻辑保持不变)
            # ...
            # 对每个 (A, B) 组合进行分析
            for a_name in species_a_list:
                node_a = find_species_node(tree, a_name)
                if node_a is None:
                    continue

                for b_name in species_b_list:
                    node_b = find_species_node(tree, b_name)
                    if node_b is None:
                        continue

                    # 对每个 SOI 进行分析
                    for soi_name in soi_list:
                        node_soi = find_species_node(tree, soi_name)
                        if node_soi is None:
                            continue

                        try:
                            mrca_sa = node_soi.get_common_ancestor(node_a)
                            mrca_sb = node_soi.get_common_ancestor(node_b)

                            if mrca_sa == mrca_sb:
                                relationship = 'undetermined'
                            elif mrca_sb in mrca_sa.iter_descendants():
                                if mrca_sb.support > support_threshold:
                                    relationship = 'closer_to_B'
                                else:
                                    relationship = 'undetermined'
                            elif mrca_sa in mrca_sb.iter_descendants():
                                if mrca_sa.support > support_threshold:
                                    relationship = 'closer_to_A'
                                else:
                                    relationship = 'undetermined'
                            else:
                                relationship = 'undetermined'
                                print(f"  警告: SOI '{soi_name}' 在树 '{filename}' 中与 A '{a_name}' 和 B '{b_name}' 遇到意外拓扑。")
                        
                        except Exception as e_mrca:
                            print(f"  错误: 为 SOI '{soi_name}' 与 A '{a_name}' 和 B '{b_name}' 查找 MRCA 时出错: {e_mrca}")
                            relationship = 'error'

                        result_entry = {
                            'SOI': soi_name,
                            'A': a_name,
                            'B': b_name,
                            'tree': filename,
                            'relationship': relationship
                        }
                        results.append(result_entry)

    # --- 汇总统计 (保持不变) ---
    summary = {}
    for soi in soi_list:
        for a in species_a_list:
            for b in species_b_list:
                key = (soi, a, b)
                summary[key] = {
                    'trees_processed': 0,
                    'closer_to_A': 0,
                    'closer_to_B': 0,
                    'undetermined': 0,
                    'errors': 0
                }

    for res in results:
        key = (res['SOI'], res['A'], res['B'])
        if key in summary:
            summary[key]['trees_processed'] += 1
            if res['relationship'] == 'closer_to_A':
                summary[key]['closer_to_A'] += 1
            elif res['relationship'] == 'closer_to_B':
                summary[key]['closer_to_B'] += 1
            elif res['relationship'] == 'undetermined':
                summary[key]['undetermined'] += 1
            elif res['relationship'] == 'error':
                summary[key]['errors'] += 1

    # --- 打印结果到控制台 (保持不变) ---
    print("\n" + "=" * 30)
    print("分析完成。结果摘要:")
    print(f"总共扫描到符合后缀的文件数: {total_files_processed}")
    print(f"成功加载并分析的树文件数: {total_trees_analyzed}")
    print("-" * 30)

    for key, counts in summary.items():
        soi, a, b = key
        print(f"SOI: {soi}, A: {a}, B: {b}")
        print(f"  在 A, B, SOI 均存在的树中的分析次数: {counts['trees_processed']}")
        print(f"  -> 更接近 A '{a}' (支持率 > {support_threshold}) 的次数: {counts['closer_to_A']}")
        print(f"  -> 更接近 B '{b}' (支持率 > {support_threshold}) 的次数: {counts['closer_to_B']}")
        print(f"  -> 关系不确定/等距/支持率不足的次数: {counts['undetermined']}")
        print(f"  处理中遇到错误的次数: {counts['errors']}")
        print("-" * 20)

    # --- 将结果写入 CSV 文件 (保持不变) ---
    print(f"\n正在将结果写入 CSV 文件: {output_csv_file} ...")
    try:
        with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            header = [
                'SOI',
                'A',
                'B',
                'Trees Analyzed (A, B, SOI present)',
                f'Closer to A (Support > {support_threshold})',
                f'Closer to B (Support > {support_threshold})',
                'Undetermined/Equidistant/Low Support',
                'Errors (MRCA issues, etc.)'
            ]
            writer = csv.writer(csvfile)
            writer.writerow(header)

            for key, counts in summary.items():
                soi, a, b = key
                row = [
                    soi,
                    a,
                    b,
                    counts['trees_processed'],
                    counts['closer_to_A'],
                    counts['closer_to_B'],
                    counts['undetermined'],
                    counts['errors']
                ]
                writer.writerow(row)
        print(f"结果已成功保存到 {output_csv_file}")
    except IOError as e:
        print(f"错误: 无法写入 CSV 文件 '{output_csv_file}': {e}")
    except Exception as e_csv:
        print(f"错误: 写入 CSV 时发生未知错误: {e_csv}")

    return summary

# --- 运行脚本 ---
if __name__ == "__main__":
    # 【修改】调用函数时传入新增的目录参数
    final_results = analyze_relationships(
        tree_dir=TREE_DIR,
        tree_suffix=TREE_SUFFIX,
        species_a_list=SPECIES_A_LIST,
        species_b_list=SPECIES_B_LIST,
        soi_list=SPECIES_OF_INTEREST,
        support_threshold=SUPPORT_THRESHOLD,
        output_csv_file=OUTPUT_CSV_FILE,
        modified_tree_dir=MODIFIED_TREE_DIR  # 传入新目录
    )
