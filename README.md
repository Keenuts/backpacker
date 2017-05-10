# Simple backup tool

## Needed

You'll need tar and scp, and an internet connection

## Configuration

- Uses save.json to setup the folders to save

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

- config.json to setup the backup machine (ssh)

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
