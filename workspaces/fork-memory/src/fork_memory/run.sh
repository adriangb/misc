#!/bin/bash
gunicorn fork_memory.main:app --log-level ERROR --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80 --workers 10 --preload
