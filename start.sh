#!/bin/bash
gunicorn car_booking:app --bind 0.0.0.0:$PORT
