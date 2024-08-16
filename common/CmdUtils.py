import subprocess


def run_cmd(cmd, stdout_handler, stderr_handler, check=True, shell=False):
    """
    运行命令并实时处理标准输出和标准错误。

    :param cmd: 要运行的命令 (以列表形式传递)
    :param stdout_handler: 处理标准输出的函数
    :param stderr_handler: 处理标准错误的函数
    :param check: 是否检查命令的返回码并抛出异常 (默认为 True)
    :param shell: 是否使用 shell 运行命令 (默认为 False)
    """
    if stdout_handler is None:
        def stdout_handler(line): return None
    if stderr_handler is None:
        def stderr_handler(line): return None
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=shell
    ) as proc:
        # 实时处理标准输出
        for line in proc.stdout:
            stdout_handler(line.strip())

        # 实时处理标准错误
        for line in proc.stderr:
            stderr_handler(line.strip())

        # 等待进程结束并获取返回码
        proc.wait()
        returncode = proc.returncode

        if check and returncode != 0:
            raise subprocess.CalledProcessError(returncode, cmd)
