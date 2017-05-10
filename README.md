# Basic backup tool

## Features

Can save some directories on a given interval. The save is just a .tar sent over
ssh to your remote server with the name 'folder_DATE.tar.gz'.
If a backup fails, an email is sent.

This is designed to save some files from an eventual ransomware.
The backup directory should obviously not be accessible from your shared folders.

## Needed

You'll need tar and scp, and an internet connection

## Installation

Use a scheduler to run this once per day

## Configuration

### Uses save.json to setup the folders to save

 * *directory* : path to the folder to save
 * *period*    : frequency to save year/month/week/day
 * *last_save* : last save date. default to unknown

```json
{
    "tasks": [
        {
            "directory": "save_a",
            "period": "month",
            "last_save": "unknown"
        },
        {
            "directory": "save_b",
            "period": "day",
            "last_save": "2017-05-10"
        }
    ]
}
```

### config.json to setup the backup machine (ssh)

 * *ssh-host* : ssh hostname (see your ~/.ssh/config)
 * *remote-dir* : remote directory to save in
 * *save-to-keep*    : not used for now
 * *mail-smtp*    : smtp to use
 * *mail-from*    : from email
 * *mail-to*    : address to send the alert to

```json
{
    "ssh-host":"host",
    "remote-dir":"~",
    "save-to-keep":3,

    "mail-smtp":"smtp.test.com",
    "mail-from":"nas@test.org",
    "mail-to":"me@test.org"
}
```
