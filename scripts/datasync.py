import argparse
import json
import shlex
import shutil
import socket
import subprocess
import tarfile
import tempfile
import tomllib
from pathlib import Path

from pymongo import MongoClient

# Load sync config
with Path(__file__).with_name("datasynccfg.toml").open("rb") as infile:
    CONFIG = tomllib.load(infile)


def remote_free_bytes(path):
    # Check free space on the remote path
    ssh = CONFIG["ssh"]
    quoted_path = shlex.quote(path)
    command = ["ssh", "-p", str(ssh["port"])]
    if ssh.get("key_path"):
        command.extend(["-i", ssh["key_path"]])
    command.extend(
        [
            f'{ssh["user"]}@{ssh["host"]}',
        f"mkdir -p {quoted_path} && df -Pk {quoted_path} | tail -1 | awk '{{print $4 * 1024}}'"
        ]
    )
    return int(subprocess.run(command, check=True, capture_output=True, text=True).stdout.strip())


def import_records(records_path):
    # Open an SSH tunnel to MongoDB
    ssh = CONFIG["ssh"]
    mongo = CONFIG["mongo"]
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        local_port = sock.getsockname()[1]

    tunnel_command = ["ssh", "-p", str(ssh["port"])]
    if ssh.get("key_path"):
        tunnel_command.extend(["-i", ssh["key_path"]])
    tunnel_command.extend(
        [
        "-N",
        "-o",
        "ExitOnForwardFailure=yes",
        "-L",
        f'{local_port}:{mongo["host"]}:{mongo["port"]}',
            f'{ssh["user"]}@{ssh["host"]}',
        ]
    )
    tunnel = subprocess.Popen(tunnel_command)
    try:
        # Load the JSON records
        with records_path.open(encoding="utf-8") as infile:
            records = json.load(infile)

        # Insert records into MongoDB
        client_kwargs = {
            "host": "127.0.0.1",
            "port": local_port,
        }
        if mongo.get("username"):
            client_kwargs["username"] = mongo["username"]
        if mongo.get("password"):
            client_kwargs["password"] = mongo["password"]
        if mongo.get("authentication_database"):
            client_kwargs["authSource"] = mongo["authentication_database"]

        client = MongoClient(**client_kwargs)
        client[mongo["database"]][mongo["collection"]].insert_many(records)
        client.close()
    finally:
        tunnel.terminate()
        tunnel.wait()


def copy_aux_data(aux_data_path):
    # Size the data before making the tar
    ssh = CONFIG["ssh"]
    aux_size = sum(path.stat().st_size for path in aux_data_path.rglob("*") if path.is_file())
    if shutil.disk_usage(tempfile.gettempdir()).free < aux_size:
        raise RuntimeError("Not enough local space to create tar")

    with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as tmp:
        archive_path = Path(tmp.name)

    try:
        # Tar the directory contents without an extra parent folder
        with tarfile.open(archive_path, "w") as archive:
            for path in aux_data_path.iterdir():
                archive.add(path, arcname=path.name)

        files = CONFIG["files"]
        remote_tar_path = f'{files["target_path"].rstrip("/")}/datasync.tar'
        tar_size = archive_path.stat().st_size

        if remote_free_bytes(files["target_path"]) < tar_size:
            raise RuntimeError("Not enough remote space to copy tar")

        # Copy the tar to the server
        scp_command = ["scp", "-P", str(ssh["port"])]
        if ssh.get("key_path"):
            scp_command.extend(["-i", ssh["key_path"]])
        scp_command.extend([str(archive_path), f'{ssh["user"]}@{ssh["host"]}:{remote_tar_path}'])
        subprocess.run(scp_command, check=True)

        if remote_free_bytes(files["target_path"]) < aux_size:
            raise RuntimeError("Not enough remote space to extract data")

        # Extract in place and remove the tar
        target_path = shlex.quote(files["target_path"])
        quoted_remote_tar_path = shlex.quote(remote_tar_path)
        remote_command = (
            f"mkdir -p {target_path} && "
            f"tar -xf {quoted_remote_tar_path} -C {target_path} --overwrite && "
            f"rm {quoted_remote_tar_path}"
        )
        ssh_command = ["ssh", "-p", str(ssh["port"])]
        if ssh.get("key_path"):
            ssh_command.extend(["-i", ssh["key_path"]])
        ssh_command.extend([f'{ssh["user"]}@{ssh["host"]}', remote_command])
        subprocess.run(ssh_command, check=True)
    finally:
        archive_path.unlink(missing_ok=True)


def main():
    # Run either or both sync steps based on args
    parser = argparse.ArgumentParser()
    parser.add_argument("--records")
    parser.add_argument("--aux-data")
    args = parser.parse_args()

    if args.records:
        import_records(Path(args.records))

    if args.aux_data:
        copy_aux_data(Path(args.aux_data))


if __name__ == "__main__":
    main()
