#!/bin/bash
gunicorn car_booking3:app --bind 0.0.0.0:$PORT
