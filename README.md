# Cactusnotes sales management platform

Website to handle sales, track payments, split PDFs, password-protect & distribute PDFs

https://github.com/user-attachments/assets/3363f6a7-a66a-4ba8-be90-488ad51f2af9

## Features

- Track customer payments and team payouts
- Password protect file downloads
- Split PDFs automatically by predefined chapters, e.g. distribute only chapters 3-5 of a given file

## Production setup (for future self)

1. Follow [this tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-22-04)
2. `git clone` this repository
3. Install Python requirements from `requirements.txt`
4. [Install rclone](https://rclone.org/install/#script-installation)
5. Add `/usr/bin` to PATH so rclone is accessible by the Python app (modify `cactusnotes.service`, [help](https://stackoverflow.com/a/21131629/10546571))
6. Setup rclone on local machine and find config at `~/.config/rclone/rclone.conf`
7. Copy over config to similar path in the VPS
8. Change DNS records to ipv4 address (not "private IP")

## Updating notes procedure

1. Update the file in Google Drive (make sure it's the same file name, or else change the filename in the database)
2. In database, update chapter pages if necessary, and chapter notes if necessary
3. Restart server so that files are updated and document info is refreshed
