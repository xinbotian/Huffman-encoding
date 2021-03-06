"""
Code for compressing and decompressing using Huffman compression.
"""

from nodes import HuffmanNode, ReadNode


# ====================
# Helper functions for manipulating bytes


def get_bit(byte, bit_num):
    """ Return bit number bit_num from right in byte.

    @param int byte: a given byte
    @param int bit_num: a specific bit number within the byte
    @rtype: int

    >>> get_bit(0b00000101, 2)
    1
    >>> get_bit(0b00000101, 1)
    0
    """
    return (byte & (1 << bit_num)) >> bit_num


def byte_to_bits(byte):
    """ Return the representation of a byte as a string of bits.

    @param int byte: a given byte
    @rtype: str

    >>> byte_to_bits(14)
    '00001110'
    """
    return "".join([str(get_bit(byte, bit_num))
                    for bit_num in range(7, -1, -1)])


def bits_to_byte(bits):
    """ Return int represented by bits, padded on right.

    @param str bits: a string representation of some bits
    @rtype: int

    >>> bits_to_byte("00000101")
    5
    >>> bits_to_byte("101") == 0b10100000
    True
    """
    return sum([int(bits[pos]) << (7 - pos)
                for pos in range(len(bits))])


# ====================
# Functions for compression


def make_freq_dict(text):
    """ Return a dictionary that maps each byte in text to its frequency.

    @param bytes text: a bytes object
    @rtype: dict{int,int}

    >>> d = make_freq_dict(bytes([65, 66, 67, 66]))
    >>> d == {65: 1, 66: 2, 67: 1}
    True
    """
    res = {}
    for b in text:
        if b in res:
            res[b] += 1
        else:
            res[b] = 1
    return res


def huffman_tree(freq_dict):
    """ Return the root HuffmanNode of a Huffman tree corresponding
    to frequency dictionary freq_dict.

    @param dict(int,int) freq_dict: a frequency dictionary
    @rtype: HuffmanNode

    >>> freq = {2: 6, 3: 4}
    >>> t = huffman_tree(freq)
    >>> result1 = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> result2 = HuffmanNode(None, HuffmanNode(2), HuffmanNode(3))
    >>> t == result1 or t == result2
    True
    """
    q = []
    for k in freq_dict:
        current_leaf = HuffmanNode(k)
        q.append((freq_dict[k], current_leaf))

    q = sorted(q)
    if len(q) == 1:
        return HuffmanNode(None, HuffmanNode(q[0][1].symbol), None)

    while len(q) > 1:
        (p1, n1) = q.pop(0)
        (p2, n2) = q.pop(0)
        current_node = HuffmanNode(None, n1, n2)
        q.append((p1 + p2, current_node))
        q = sorted(q)

    return q[0][1]


def get_codes_rec(tree, code, d):
    """ Modify the parameter d to include the partial codes from the
    given subtree. This is a recursive method used in get_codes.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @param string code: the current code
    @param dict(int,string): the current code dictionary
    @rtype: None
    """
    if tree is None:
        return

    if tree.symbol is not None:
        d[tree.symbol] = code
    else:
        get_codes_rec(tree.left, code + "0", d)
        get_codes_rec(tree.right, code + "1", d)


def get_codes(tree):
    """ Return a dict mapping symbols from tree rooted at HuffmanNode to codes.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: dict(int,str)

    >>> tree = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> d = get_codes(tree)
    >>> d == {3: "0", 2: "1"}
    True
    """
    d = {}
    get_codes_rec(tree, "", d)
    return d


def number_nodes_rec(tree, num):
    """Number the current subtree recursively in postorder traversal.
    Returns the current number
    @param HuffmanNode tree: the current subtree
    @param int num: the current number
    @rtype: int

    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(None, HuffmanNode(9), HuffmanNode(10))
    >>> tree = HuffmanNode(None, left, right)
    >>> number_nodes_rec(tree,0)
    >>> tree.left.number
    0
    >>> tree.right.number
    1
    >>> tree.number
    2
    """
    if tree is None:
        return num

    num = number_nodes_rec(tree.left, num)
    num = number_nodes_rec(tree.right, num)
    if tree.symbol is None:
        tree.number = num
        return num + 1
    else:
        return num


def number_nodes(tree):
    """ Number internal nodes in tree according to postorder traversal;
    start numbering at 0.

    @param HuffmanNode tree:  a Huffman tree rooted at node 'tree'
    @rtype: NoneType

    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(None, HuffmanNode(9), HuffmanNode(10))
    >>> tree = HuffmanNode(None, left, right)
    >>> number_nodes(tree)
    >>> tree.left.number
    0
    >>> tree.right.number
    1
    >>> tree.number
    2
    """
    number_nodes_rec(tree, 0)


def avg_length(tree, freq_dict):
    """ Return the number of bits per symbol required to compress text
    made of the symbols and frequencies in freq_dict, using the Huffman tree.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @param dict(int,int) freq_dict: frequency dictionary
    @rtype: float

    >>> freq = {3: 2, 2: 7, 9: 1}
    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(9)
    >>> tree = HuffmanNode(None, left, right)
    >>> avg_length(tree, freq)
    1.9
    """
    codes = get_codes(tree)
    total_freq = 0
    avg = 0
    for k in freq_dict:
        avg += len(codes[k]) * freq_dict[k]
        total_freq += freq_dict[k]
    return avg / total_freq


def generate_compressed(text, codes):
    """ Return compressed form of text, using mapping in codes for each symbol.

    @param bytes text: a bytes object
    @param dict(int,str) codes: mappings from symbols to codes
    @rtype: bytes

    >>> d = {0: "0", 1: "10", 2: "11"}
    >>> text = bytes([1, 2, 1, 0])
    >>> result = generate_compressed(text, d)
    >>> [byte_to_bits(byte) for byte in result]
    ['10111000']
    >>> text = bytes([1, 2, 1, 0, 2])
    >>> result = generate_compressed(text, d)
    >>> [byte_to_bits(byte) for byte in result]
    ['10111001', '10000000']
    """
    bstring = ""
    for byte in text:
        bstring += codes[byte]

    while len(bstring) % 8 != 0:
        bstring += "0"

    binary_list = []
    for i in range(0, len(bstring), 8):
        binary_list.append(bits_to_byte(bstring[i: i + 8]))

    return bytes(binary_list)


def tree_to_bytes_rec(tree, res):
    """ Compute the bytes representation of the given subtree. This
        is a recursive method used in tree_to_bytes

    @param HuffmanNode tree: The current subtree
    @param list[int] res: The current representation
    @rtype: None
    """

    if tree is None or tree.symbol is not None:
        return

    tree_to_bytes_rec(tree.left, res)
    tree_to_bytes_rec(tree.right, res)
    if tree.left.symbol is None:
        res.append(1)
        res.append(tree.left.number)
    else:
        res.append(0)
        res.append(tree.left.symbol)
    if tree.right.symbol is None:
        res.append(1)
        res.append(tree.right.number)
    else:
        res.append(0)
        res.append(tree.right.symbol)


def tree_to_bytes(tree):
    """ Return a bytes representation of the tree rooted at tree.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: bytes

    The representation should be based on the postorder traversal of tree
    internal nodes, starting from 0.
    Precondition: tree has its nodes numbered.

    >>> tree = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> number_nodes(tree)
    >>> list(tree_to_bytes(tree))
    [0, 3, 0, 2]
    >>> left = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> right = HuffmanNode(5)
    >>> tree = HuffmanNode(None, left, right)
    >>> number_nodes(tree)
    >>> list(tree_to_bytes(tree))
    [0, 3, 0, 2, 1, 0, 0, 5]
    """
    res = []
    tree_to_bytes_rec(tree, res)
    return bytes(res)


def num_nodes_to_bytes(tree):
    """ Return number of nodes required to represent tree (the root of a
    numbered Huffman tree).

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: bytes
    """
    return bytes([tree.number + 1])


def size_to_bytes(size):
    """ Return the size as a bytes object.

    @param int size: a 32-bit integer that we want to convert to bytes
    @rtype: bytes

    >>> list(size_to_bytes(300))
    [44, 1, 0, 0]
    """
    # little-endian representation of 32-bit (4-byte)
    # int size
    return size.to_bytes(4, "little")


def compress(in_file, out_file):
    """ Compress contents of in_file and store results in out_file.

    @param str in_file: input file whose contents we want to compress
    @param str out_file: output file, where we store our compressed result
    @rtype: NoneType
    """
    with open(in_file, "rb") as f1:
        text = f1.read()
    freq = make_freq_dict(text)
    tree = huffman_tree(freq)
    codes = get_codes(tree)
    number_nodes(tree)
    print("Bits per symbol:", avg_length(tree, freq))
    result = (num_nodes_to_bytes(tree) + tree_to_bytes(tree) +
              size_to_bytes(len(text)))
    result += generate_compressed(text, codes)
    with open(out_file, "wb") as f2:
        f2.write(result)


# ====================
# Functions for decompression


def generate_tree_general(node_lst, root_index):
    """ Return the root of the Huffman tree corresponding
    to node_lst[root_index].

    The function assumes nothing about the order of the nodes in the list.

    @param list[ReadNode] node_lst: a list of ReadNode objects
    @param int root_index: index in the node list
    @rtype: HuffmanNode

    >>> lst = [ReadNode(0, 5, 0, 7), ReadNode(0, 10, 0, 12), \
    ReadNode(1, 1, 1, 0)]
    >>> generate_tree_general(lst, 2)
    HuffmanNode(None, HuffmanNode(None, HuffmanNode(10, None, None), \
HuffmanNode(12, None, None)), \
HuffmanNode(None, HuffmanNode(5, None, None), HuffmanNode(7, None, None)))
    """
    read_node = node_lst[root_index]
    if read_node.l_type == 1:
        left = generate_tree_general(node_lst, read_node.l_data)
    else:
        left = HuffmanNode(read_node.l_data)
    if read_node.r_type == 1:
        right = generate_tree_general(node_lst, read_node.r_data)
    else:
        right = HuffmanNode(read_node.r_data)

    return HuffmanNode(None, left, right)


def generate_tree_postorder_rec(node_lst, root_index):
    """Generates the current subtree in postorder. Used recursively
    in generate_tree_postorder

    @param list[ReadNode] node_lst: a list ot ReadNode objects
    @param int root_index: the current root index
    @rtype: (int,HuffManNode)

    >>> lst = [ReadNode(0, 5, 0, 7), ReadNode(0, 10, 0, 12), \
    ReadNode(1, 0, 1, 0)]
    >>> tree = generate_tree_postorder_rec(lst, 2)
    >>> tree[1]
    HuffmanNode(None, HuffmanNode(None, HuffmanNode(5, None, None), \
HuffmanNode(7, None, None)), \
HuffmanNode(None, HuffmanNode(10, None, None), HuffmanNode(12, None, None)))
    """
    read_node = node_lst[root_index]
    ind = root_index
    if read_node.r_type == 1:
        (ind, right) = generate_tree_postorder_rec(node_lst, ind - 1)
    else:
        right = HuffmanNode(read_node.r_data)
    if read_node.l_type == 1:
        (ind, left) = generate_tree_postorder_rec(node_lst, ind - 1)
    else:
        left = HuffmanNode(read_node.l_data)

    return ind, HuffmanNode(None, left, right)


def generate_tree_postorder(node_lst, root_index):
    """ Return the root of the Huffman tree corresponding
    to node_lst[root_index].

    The function assumes that the list represents a tree in postorder.

    @param list[ReadNode] node_lst: a list of ReadNode objects
    @param int root_index: index in the node list
    @rtype: HuffmanNode

    >>> lst = [ReadNode(0, 5, 0, 7), ReadNode(0, 10, 0, 12), \
    ReadNode(1, 0, 1, 0)]
    >>> generate_tree_postorder(lst, 2)
    HuffmanNode(None, HuffmanNode(None, HuffmanNode(5, None, None), \
HuffmanNode(7, None, None)), \
HuffmanNode(None, HuffmanNode(10, None, None), HuffmanNode(12, None, None)))
    """

    return generate_tree_postorder_rec(node_lst, root_index)[1]


def generate_uncompressed(tree, text, size):
    """ Use Huffman tree to decompress size bytes from text.

    @param HuffmanNode tree: a HuffmanNode tree rooted at 'tree'
    @param bytes text: text to decompress
    @param int size: how many bytes to decompress from text.
    @rtype: bytes
    """
    bstring = ""
    for byte in text:
        bstring += byte_to_bits(byte)

    binary_list = []
    cur = tree
    bytes_decoded = 0
    for bit in bstring:
        if bytes_decoded == size:
            break
        if bit == '0':
            cur = cur.left
        else:
            cur = cur.right

        if cur.symbol is not None:
            binary_list.append(cur.symbol)
            cur = tree
            bytes_decoded += 1

    return bytes(binary_list)


def bytes_to_nodes(buf):
    """ Return a list of ReadNodes corresponding to the bytes in buf.

    @param bytes buf: a bytes object
    @rtype: list[ReadNode]

    >>> bytes_to_nodes(bytes([0, 1, 0, 2]))
    [ReadNode(0, 1, 0, 2)]
    """
    lst = []
    for i in range(0, len(buf), 4):
        l_type = buf[i]
        l_data = buf[i + 1]
        r_type = buf[i + 2]
        r_data = buf[i + 3]
        lst.append(ReadNode(l_type, l_data, r_type, r_data))
    return lst


def bytes_to_size(buf):
    """ Return the size corresponding to the
    given 4-byte little-endian representation.

    @param bytes buf: a bytes object
    @rtype: int

    >>> bytes_to_size(bytes([44, 1, 0, 0]))
    300
    """
    return int.from_bytes(buf, "little")


def uncompress(in_file, out_file):
    """ Uncompress contents of in_file and store results in out_file.

    @param str in_file: input file to uncompress
    @param str out_file: output file that will hold the uncompressed results
    @rtype: NoneType
    """
    with open(in_file, "rb") as f:
        num_nodes = f.read(1)[0]
        buf = f.read(num_nodes * 4)
        node_lst = bytes_to_nodes(buf)
        # use generate_tree_general or generate_tree_postorder here
        tree = generate_tree_general(node_lst, num_nodes - 1)
        size = bytes_to_size(f.read(4))
        with open(out_file, "wb") as g:
            text = f.read()
            g.write(generate_uncompressed(tree, text, size))


# ====================
# Other functions

def improve_tree(tree, freq_dict):
    """ Improve the tree as much as possible, without changing its shape,
    by swapping nodes. The improvements are with respect to freq_dict.

    @param HuffmanNode tree: Huffman tree rooted at 'tree'
    @param dict(int,int) freq_dict: frequency dictionary
    @rtype: NoneType

    >>> left = HuffmanNode(None, HuffmanNode(99), HuffmanNode(100))
    >>> right = HuffmanNode(None, HuffmanNode(101), \
    HuffmanNode(None, HuffmanNode(97), HuffmanNode(98)))
    >>> tree = HuffmanNode(None, left, right)
    >>> freq = {97: 26, 98: 23, 99: 20, 100: 16, 101: 15}
    >>> improve_tree(tree, freq)
    >>> avg_length(tree, freq)
    2.31
    """
    priorities = sorted(list(freq_dict.items()),
                        key=lambda x: x[1],
                        reverse=True)
    q = []
    q.append(tree)
    p_index = 0

    while len(q) > 0:
        cur = q.pop(0)
        if cur.left is not None:
            if cur.left.symbol is not None:
                cur.left.symbol = priorities[p_index][0]
                p_index += 1
            else:
                q.append(cur.left)
        if cur.right is not None:
            if cur.right.symbol is not None:
                cur.right.symbol = priorities[p_index][0]
                p_index += 1
            else:
                q.append(cur.right)


if __name__ == "__main__":
    import python_ta

    python_ta.check_all(config="huffman_pyta.txt")
    # TODO: Uncomment these when you have implemented all the functions
    import doctest

    doctest.testmod()

    import time

    mode = input("Press c to compress or u to uncompress: ")
    if mode == "c":
        fname = input("File to compress: ")
        start = time.time()
        compress(fname, fname + ".huf")
        print("compressed {} in {} seconds."
              .format(fname, time.time() - start))
    elif mode == "u":
        fname = input("File to uncompress: ")
        start = time.time()
        uncompress(fname, fname + ".orig")
        print("uncompressed {} in {} seconds."
              .format(fname, time.time() - start))
