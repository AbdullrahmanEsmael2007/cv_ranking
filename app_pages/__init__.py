import streamlit as st
from streamlit_extras.bottom_container import bottom
from app_pages.chatgpt_request import request
from app_pages.get_job_description import get_job_description
import PyPDF2
from openai import OpenAI
import pandas as pd
import numpy as np
from app_pages.extract_docx_pdf_txt import extract_text_from_pdf, extract_text_from_docx, extract_text_from_txt
import base64
import re
import docx