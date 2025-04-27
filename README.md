# Mulapin data 

### Building_Blocks_Processing.py
Check and clean the building blocks data (e.g. VOC, painpoints)
- Check that the required fields are not empty based on type
- Remove duplicates and standardise text
- Check the missing value
- Sentiment analysis that matches the rates and comments

### Component_Model_Processing.py
Check and clean the uploaded component model files.
- Check the uploaded file size and format.
- Check the missing value
- Check the validation of the ID
- Clean the duplicate and sort the ID.

### faiss.ipynb
Use FAISS+ HSNW to speed up the search between embedding vectors.
Test with the VOC data banking77 from Hugging Face https://huggingface.co/datasets/PolyAI/banking77
