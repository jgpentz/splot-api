from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import List
import os
import tempfile

import rftools as rf

# Generate a route for processing sparams
router= APIRouter()

# Process the sparam files
@router.post('/sparams', tags=['sparams'])
async def process_sparams(files: List[UploadFile] = File(...)):
    processed_data = {}
    for file in files:
        file_contents = await file.read()
        fname = file.filename
        fext = fname.split('.')[-1]

        # Create a temporary file without extension
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_contents)
            temp_file_path = temp_file.name

        # Rename file to include the snp extension
        final_temp_file_path = f'{temp_file.name}.{fext}'
        os.rename(temp_file_path, final_temp_file_path)

        # Read the s params, convert complex voltage to dB, store in dict
        _, s = rf.read_touchstone(final_temp_file_path, xarray=True)
        s = rf.v2db(s)
        s_dict = s.to_dict()

        # Change m and n keys to contain a list of the data
        s_dict['m'] = s.m.data.tolist()
        s_dict['n'] = s.n.data.tolist()

        # Clean up frequency
        s_dict['frequency'] = (s.frequency.data / 1e9).tolist()

        # Pull out all of the Smn permutations into their own key value pair
        for m in s.m.data:
            for n in s.n.data:
                s_dict[f's{m}{n}'] = s.sel(m=m, n=n).data.tolist()

        # Store the data in the final json
        processed_data[fname] = s_dict

        # Remove unused info
        del s_dict['dims']
        del s_dict['attrs']
        del s_dict['data']
        del s_dict['coords']
        del s_dict['name']

        # Delete the temp file
        os.remove(final_temp_file_path)

    return processed_data