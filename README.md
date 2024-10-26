# Cactusnotes sales portal

Website and extension for managing sales

## Development setup

1. Create a venv; install dependencies from requirements.txt
2. Set environment variables (e.g. in activate file)
   - Set "MODE" to "testing"
   - Set "DATABASE_PW"

## Production setup (for future self)

1. Follow [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-22-04)
2. `git pull` this repository using Personal Access Token
3. Install Python requirements from `requirements.txt`
4. [Install rclone](https://rclone.org/install/#script-installation)
5. Add `/usr/bin` to PATH so rclone is accessible by the Python app (modify `cactusnotes.service`, [help](https://stackoverflow.com/a/21131629/10546571))
6. Setup rclone on local machine and find config at `~/.config/rclone/rclone.conf`
7. Copy over config to similar path in the VPS
8. Change DNS records to ipv4 address (not "private IP")

## Updating notes procedure

1. Update the file in Google Drive (make sure its the same file name, or else change the filename in the database)
2. In database, update chapter pages if necessary, and chapter notes if necessary
3. Restart server (`sudo systemctl restart cactusnotes`) so that files are updated and document info is refreshed
