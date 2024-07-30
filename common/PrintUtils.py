def get_sep(title: str, length=80, sep="="):
    """
    带有分隔符的字符串
    :param title: 标题
    :param len: 一行的长度
    :param sep: 分隔符
    """
    len_title = len(title)
    len_left = (length - len_title) // 2
    len_right = length - len_title - len_left
    return f"{sep * len_left}{title}{sep * len_right}"

def print_sep(title: str, length=80, sep="=", flush=True):
    """
    带有分隔符的打印，确定打印一行的长度
    :param title: 标题
    :param len: 一行的长度
    :param sep: 分隔符
    """
    sep_str = get_sep(title, length, sep)
    print(sep_str, flush=flush)
