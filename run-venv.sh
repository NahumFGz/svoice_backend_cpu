#!/bin/bash -x
activate () {
    source /home/ubuntu/svoice_backend/venv/bin/activate
}

runbert () {
    sudo python3 /home/ubuntu/svoice_backend/main.py
}

activate
runbert
