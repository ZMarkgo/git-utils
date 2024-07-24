def print_sep(title: str, len=80, sep="="):
    """
    带有分隔符的打印，确定打印一行的长度
    :param title: 标题
    :param len: 一行的长度
    :param sep: 分隔符
    """
    len_title = len(title)
    len_left = (len - len_title) // 2
    len_right = len - len_title - len_left
    print(f"{sep * len_left}{title}{sep * len_right}")
