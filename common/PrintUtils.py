def print_sep(title: str, length=80, sep="=", flush=True):
    """
    带有分隔符的打印，确定打印一行的长度
    :param title: 标题
    :param len: 一行的长度
    :param sep: 分隔符
    """
    len_title = len(title)
    len_left = (length - len_title) // 2
    len_right = length - len_title - len_left
    print(f"{sep * len_left}{title}{sep * len_right}", flush=flush)
