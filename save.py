#!/bin/python3

import sys
import json
import datetime
import logging
from subprocess import call


PATH="./"
logging.basicConfig(filename=PATH+'LOGS',
                    format='[%(asctime)s][%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO);
logging.info("Starting backup.")

def check_valid(t):
    if not "directory" in t:
        logging.error("JSON incorrect: champ 'directory' manquant")
    elif not "period" in t:
        logging.error("JSON incorrect: champ 'period' manquant")
    elif not "last_save" in t:
        logging.error("JSON incorrect: champ 'last_save' manquant")
    else:
        if (
            t["period"] != 'year'
            and t["period"] != 'month'
            and t["period"] != 'week'
            and t["period"] != 'day'
            ):
            logging.error("Invalid period %s" % t["period"])
            return False
        return True
    return False

def get_date(data):
    if data == "unknown":
        return datetime.datetime.strptime("1970", "%Y");
    return datetime.datetime.strptime(data, "%Y-%m-%d");

def save(directory, date):
    logging.info("Saving the directory: %s" % directory);
    filename = directory + "_" + date + ".tar.gz"
    call(["tar", "-cf", filename, directory + "/"]);
    call(["mv", filename, "dst/" + filename]);
    

def process():
    try:
        f = open("save.json", "r");
        data = json.loads(f.read());
        f.close();
        for t in data["tasks"]:
            if not check_valid(t):
                return 1;

            last_save = get_date(t["last_save"]);
            directory = t["directory"]
            period = t["period"]

            today = datetime.datetime.now();
            delta = today - last_save;

            if (
                (period == 'year' and delta.week >= 365) or
                (period == 'month' and delta.days >= 30) or
                (period == 'week' and delta.days >= 7) or
                (period == 'day' and delta.days >= 1)
                ):
                save(directory, today.strftime("%Y-%m-%d"));
                last_save = today
            t['last_save'] = last_save.strftime('%Y-%m-%d')

        f = open("save.json", "w+");
        f.write(json.dumps(data, indent=4));
        f.close();

    except json.decoder.JSONDecodeError as err:
        logging.error("An error occured: %s" % str(err));

process()
