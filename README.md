# Cactusnotes Sales Portal

## Development

1. Create a venv
2. Install dependencies from requirements.txt
3. In the activate file, set "MODE" to "testing" and "DATABASE_PW". Remember to unset them under the deactivate function as well.

## Production setup (for future self)

1. Follow [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-22-04)
2. `git pull` this repository using Personal Access Token
3. Install Python requirements from `requirements.txt`
4. [Install rclone](https://rclone.org/install/#script-installation)
5. Add `/usr/bin` to PATH so rclone is accessible by the Python app (modify `cactusnotes.service`, [help](https://stackoverflow.com/a/21131629/10546571))
6. Setup rclone on local machine and find config at `~/.config/rclone/rclone.conf`
7. Copy over config to similar path in the VPS
8. Change DNS records to ipv4 address (not "private IP")
