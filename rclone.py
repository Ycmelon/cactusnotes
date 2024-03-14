import subprocess


def rclone_pull():
    subprocess.run(
        [
            "rclone",
            "copy",
            # f"{os.environ['RCLONE_S3_CONN_STRING']}:{os.environ['S3_BUCKET']}",
            "cactusnotes:",
            "./drive",
            "--max-depth",
            "1",
        ]
    )


# def rclone_push():
#     subprocess.run(["rclone", "copy", "./drive", "cactusnotes:", "--max-depth", "1"])
