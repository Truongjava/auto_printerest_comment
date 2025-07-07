#!/usr/bin/env bash

# Cập nhật pip và cài thư viện
pip install --upgrade pip
pip install -r requirements.txt

# Tải trình duyệt Chromium
playwright install chromium
