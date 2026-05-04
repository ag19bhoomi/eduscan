import json

def export_to_label_studio(filename, text_blocks, predictions):
    """
    Converts OCR results into a Label Studio compatible JSON task.
    """
    task = {
        "data": {"image": f"/data/local-files/?d={filename}"},
        "predictions": [{
            "model_version": "eduscan-v1-ocr",
            "result": []
        }]
    }

    for block in text_blocks:
        # text_blocks would come from reader.readtext(image)
        bbox = block[0] # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        text = block[1]
        
        # Convert coordinates to percentages (required by many tools)
        # Note: You'll need the image width/height for this math
        
        task["predictions"][0]["result"].append({
            "from_name": "label",
            "to_name": "image",
            "type": "rectanglelabels",
            "value": {
                "x": bbox[0][0], "y": bbox[0][1],
                "width": bbox[1][0] - bbox[0][0],
                "height": bbox[2][1] - bbox[1][1],
                "rectanglelabels": ["student_name" if text in predictions['NAME'] else "text"]
            }
        })
    
    return task
