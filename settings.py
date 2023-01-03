# coding: UTF-8
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), 'env/.env')
load_dotenv(dotenv_path)

DB_USER = os.environ.get('DB_USER')
DB_HOST = os.environ.get("DB_HOST") 
DB_NAME = os.environ.get("DB_NAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
