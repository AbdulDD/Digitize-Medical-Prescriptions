from PIL import Image
import numpy as np
import json



# Post Processing 1 - PGNet to Layout LLM V2
def Org_points(V):
    x1, y1 = V[0]
    x2, y2 = V[2]
    coordinates = [int(x1), int(y1), int(x2), int(y2)]
    return coordinates


# Normalize the bounding box values in 0-1000 range
def Nor_points(V, W, H):
    x1, y1 = V[0]
    x2, y2 = V[2]

    Nor_x1 = int(1000 * (x1 / W))
    Nor_y1 = int(1000 * (y1 / H))
    Nor_x2 = int(1000 * (x2 / W))
    Nor_y2 = int(1000 * (y2 / H))
    coordinates = [Nor_x1, Nor_y1, Nor_x2, Nor_y2]
    return coordinates


def PGNettoLayoutLMv2(image, PGNet_predictions):
    text = []
    Nor_bboxes = []
    Org_bboxes = []

    image = Image.open(image)
    width, height = image.size

    with open(PGNet_predictions, 'r') as file:
        content = file.read()
    entries = content.strip().split('\n')

    # Loop through each entry
    for entry in entries:
        # Split the entry into image path and JSON data
        image_path, json_data = entry.split('\t')

        # Parse the JSON data
        data = json.loads(json_data)

        # Extract and print the transcriptions
        for item in data:
            #print(item)
            for key, value in item.items():
                if key == "transcription":
                    text.append(value)
                if key == "points":
                    #print(value)
                    O_cor = Org_points(value)
                    N_cor = Nor_points(value, width, height)
                    Org_bboxes.append(O_cor)
                    Nor_bboxes.append(N_cor)

    numpy_image = np.array(image)

    return numpy_image, text, Nor_bboxes, Org_bboxes