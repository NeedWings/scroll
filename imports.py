import requests
from time import sleep, time
from web3 import Web3
from traceback import format_exc
from platform import system
from json import load, dump
from os import getcwd
import asyncio
from threading import Thread
import sys
import os
import random
from os import mkdir
import decimal

import asyncio
import datetime
import datetime as dt
import json
import platform
from pathlib import Path
import re
from decimal import Decimal
from fractions import Fraction

import logging
from web3 import Web3, HTTPProvider
from websockets.client import connect



from eth_account import Account
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth


from eth_account import Account
from decimal import Decimal
import binascii


from flask import Flask, request, jsonify
from flask_cors import CORS
from os import getcwd
import traceback
import subprocess

import json
import subprocess
import uuid, re
import hashlib
import socket

import getpass

from werkzeug.serving import make_server
import string


from loguru import logger

PLATFORM = system()

if PLATFORM != "Darwin":
    import wmi

def get_correct_path(path: str) -> str:
    if PLATFORM == "Windows":
        return path.replace("/", "\\")
    elif PLATFORM == "Darwin":
        return path.replace("\\", "/")

log_path = getcwd() + "/data/app/logs.txt"

logger_format = "<green>{time:HH:mm:ss}</green> - <level>{level}</level> - <level>{message}</level>"
logger.add(log_path, format=logger_format)
#logger.add(sys.stderr, format=logger_format)

decrypt_password = ''