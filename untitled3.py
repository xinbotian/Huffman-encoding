def avg_length(tree, freq_dict):
    """ Return the number of bits per symbol required to compress text
    made of the symbols and frequencies in freq_dict, using the Huffman tree.

    @param HuffmanNode tree: a Huffman tree rooted at node 'tree'
    @param dict(int,int) freq_dict: frequency dictionary
    @rtype: float

    >>> freq = {'a': 2, 'b': 7, 'c': 1}
    >>> left = HuffmanNode(None, HuffmanNode('a'), HuffmanNode('b'))
    >>> right = HuffmanNode('c')
    >>> tree = HuffmanNode(None, left, right)
    >>> avg_length(tree, freq)
    1.9
    """
    sum_frequencies = sum(list(freq_dict.values()))
    sum_bits = []
    codes = get_codes(tree)

    len_codes = [len(codes[k]) for k in codes]
    freq_list = [freq_dict[k] for k in freq_dict]
    for i in range(len(len_codes)):
        sum_bits.append(len_codes[i] * freq_list[i])

    return sum(sum_bits) / sum_frequencies
