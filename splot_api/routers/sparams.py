from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import List
import io

import rftools as rf

# Generate a route for processing sparams
router= APIRouter()

# Process the sparam files
@router.post('/sparams', tags=['sparams'])
async def process_sparams(files: List[UploadFile] = File(...)):
    for file in files:
        file_contents = await file.read()
        fname = file.filename
        print(fname)
        # fi = io.StringIO(file_contents)
        # f, s = rf.read_touchstone(fi)
        decoded_content = file_contents.decode('utf-8')
        string_io = io.StringIO(decoded_content)
        f, s = rf.read_touchstone(string_io)
        print(f)
        print(s)

    return {}