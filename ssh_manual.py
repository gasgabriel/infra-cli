
from infra_cli.ssh import SSHClient


ssh = SSHClient(
    hostname="192.168.0.13",
    username="piquitucha",
)

ssh.connect()

result = ssh.execute("hostname")

print(result)

ssh.close()
