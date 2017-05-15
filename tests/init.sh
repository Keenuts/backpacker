#!/bin/sh

function dir_creator() {
  local depth=$1
  local dir_count=$2
  local files_count=$3

  for i in $(seq 1 $dir_count); do
    local d="DIR_$RANDOM$RANDOM$RANDOM"
    mkdir $d
    if [ $depth -gt 0 ]; then
      cd $d
      dir_creator $((depth - 1)) $((RANDOM % 5)) $((RANDOM % 5))
      cd ..
    fi
  done

  for i in $(seq 1 $files_count); do
    local f="FILE_$RANDOM$RANDOM$RANDOM"
    touch $f
  done
}

mkdir -p archives archives2 &&
cd archives &&
dir_creator 5 40 300 &&
cd ../archives2 &&
dir_creator 5 40 300

