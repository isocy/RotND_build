### How to use the RotND vibe build generator
1. Use Unity Asset Bundle Extractor(UABE) like UABEA to extract all the json files required
    - Required json files are the ones whose path variables are present in RotND_build/Global/const_def.py
2. Set a beatmap json file path in RotND_build/Global/\_\_init\_\_.py
3. Run RotND_build/rift_build.py and inspect the result
4. Change the values in RotND_build/Global/\_\_init\_\_.py appropriately so that the produced vibe build becomes practical