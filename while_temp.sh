#!/bin/bash

touch .lock

while [ -f ".lock" ]
do
    {TASK_COMMANDS}
    echo "rm .lock"
    sleep 2
done
