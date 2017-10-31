def make_freq_dict(text):
    """ Return a dictionary that maps each byte in text to its frequency.

    @param bytes text: a bytes object
    @rtype: dict{int,int}

    >>> d = make_freq_dict(bytes([65, 66, 67, 66]))
    >>> d == {65: 1, 66: 2, 67: 1}
    True
    """
    d = {}
    for i in text:
        if not (i in d):
            d[i] = 1
        else:
            d[i] += 1
    return d


def huffman_tree(freq_dict):
    """ Return the root HuffmanNode of a Huffman tree corresponding
    to frequency dictionary freq_dict.

    @param dict(int,int) freq_dict: a frequency dictionary
    @rtype: HuffmanNode

    >>> freq = {2: 6, 3: 4} #bite : frequency
    >>> t = huffman_tree(freq)
    >>> result1 = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> result2 = HuffmanNode(None, HuffmanNode(2), HuffmanNode(3))
    >>> t == result1 or t == result2
    True
    """

    freq_to_item = [(freq_dict[i], i) for i in freq_dict]

    if len(freq_to_item) == 1:
        return HuffmanNode(freq_to_item[0][1], None, None)

    while len(freq_to_item) > 1:
        freq_to_item.sort()
        item_0 = freq_to_item.pop(0)
        item_1 = freq_to_item.pop(0)

        freq1 = item_0[0]
        freq2 = item_1[0]

        if isinstance(item_0[1], int):
            item_0 = HuffmanNode(item_0[1])
        else:
            item_0 = item_0[1]

        if isinstance(item_1[1], int):
            item_1 = HuffmanNode(item_1[1])
        else:
            item_1 = item_1[1]

        new_huff = HuffmanNode(None, item_0, item_1)

        freq_to_item.append((freq1 + freq2, new_huff))

    return freq_to_item[0][1]


def get_codes(tree):
    """ Return a dict mapping symbols from tree rooted at HuffmanNode to codes.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @rtype: dict(int,str)

    >>> tree = HuffmanNode(None, HuffmanNode(3), HuffmanNode(2))
    >>> d = get_codes(tree)
    >>> d == {3: "0", 2: "1"}
    True
    """
    code = {}

    def get_code(node, default_code=""):
        """
        Return a dictionary of all its bytes as keys and all their corresponding
        codes as values, in a Huffman tree, where moving down left would add a
        "0" and moving down right would add a "1".

        @param HuffmanNode node: a HuffmanNode
        @param str default_code: the default string that will be modified
        @rtype: dict
        """
        if node is None:
            return
        elif (node.left is None) and (node.right is None):
            code[node.symbol] = default_code
        else:
            get_code(node.left, default_code + "0")
            get_code(node.right, default_code + "1")

    if tree.symbol is not None and tree.right is None and tree.left is None:
        code[tree.symbol] = "1"
    else:
        get_code(tree)

    return code


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

    data = []

    def postorder(node):
        """
        Add all the internal nodes (nodes that are not leaves and are not None)
        to a data list in postorder traversal order.
        @param HuffmanNode node: a HuffmanNode that we want to use to get all
        its internal nodes to the data list
        @rtype: None
        """
        if node is None:
            return
        else:
            if not node.is_leaf():
                postorder(node.left)
                postorder(node.right)
                data.append(node)

    postorder(tree)

    for i in range(len(data)):
        data[i].number = i


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

    sum_frequencies = sum(list(freq_dict.values()))
    sum_bits = []
    codes = get_codes(tree)

    for i in codes:
        sum_bits.append((i, len(codes[i])))

    for i in range(len(sum_bits)):
        sum_bits[i] = sum_bits[i][0] * sum_bits[i][1]

    return sum(sum_bits) / sum_frequencies
