import paramiko
import os

class SSHClient:
    """Cliente responsável pela comunicação SSH com servidores remotos."""

    def __init__(
        self,
        hostname: str,
        username: str,
        port: int = 22,
        timeout: int = 10,
        key_filename: str | None = None,
    ):
        self.hostname = hostname
        self.username = username
        self.port = port
        self.timeout = timeout
        self.key_filename = key_filename or os.path.expanduser(
            "~/.ssh/id_ed25519"
        )

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.RejectPolicy())

    def connect(self, passphrase: str | None = None):
        """Estabelece uma conexão SSH com o servidor remoto."""
        
        try:
            self.client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                key_filename=self.key_filename,
                passphrase=passphrase,
                timeout=self.timeout,
                allow_agent=True,
                look_for_keys=False,
             )

        except paramiko.AuthenticationException as exc:
            raise ConnectionError(
                f"Falha de autenticação no host {self.hostname}"
            ) from exc

        except paramiko.SSHException as exc:
            raise ConnectionError(
                f"Erro SSH ao conectar ao host {self.hostname}"
            ) from exc

        except TimeoutError as exc:
            raise ConnectionError(
                f"Timeout ao conectar ao host {self.hostname}"
            ) from exc

        except OSError as exc:
            raise ConnectionError(
                f"Erro de rede ao conectar ao host {self.hostname}"
            ) from exc

    def execute(self, command: str):
        """Executa um comando no servidor remoto."""

        stdin, stdout, stderr = self.client.exec_command(command)

        output = stdout.read().decode()
        error = stderr.read().decode()

        exit_code = stdout.channel.recv_exit_status()

        return {
            "stdout": output,
            "stderr": error,
            "exit_code": exit_code,
        }

    def close(self):
        """Fecha a conexão SSH."""

        self.client.close()
