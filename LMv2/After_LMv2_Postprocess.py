import json


outer_boxes = []

output_dir = ""

target_labels = ['DIAGNOSIS', 'MEDICINE DOSE', 'HISTORY']
labels_list = ["NAME","AGE","GENDER","DATE","DIAGNOSIS","HISTORY","BP","TEMP","WEIGHT","MEDICINE TYPE",
               "MEDICINE NAME","MEDICINE POWER","MEDICINE DOSE","B","I","B-U","I-U","PULSE"]
label_index = list()



def post_processing(entry):

    image_path = entry['image_path']

    data = {
        "patient info": {
            "NAME": "",
            "AGE": "",
            "GENDER": "",
            "DATE": ""
        },
        "MEDICINE BLOCK": [],
        "DIAG BLOCK": {
            "DIAGNOSIS": "",
            "BP": "",
            "TEMP": "",
            "WEIGHT": ""
        }
    }


    name = ""
    age = ""
    gender = ""
    date = ""

    for i, label in enumerate(label_index):
        if labels_list[label] == "NAME":
            data["patient info"]["NAME"] = entry['text'][i]
        elif labels_list[label] == "AGE":
            data["patient info"]["AGE"] = entry['text'][i]
        elif labels_list[label] == "GENDER":
            data["patient info"]["GENDER"] = entry['text'][i]
        elif labels_list[label] == "DATE":
            data["patient info"]["DATE"] = entry['text'][i]


    data["MEDICINE BLOCK"] = create_medicine_blocks(entry)


    diagnosis = ""
    bp = ""
    temp = ""
    weight = ""
    history = ""
    pulse = ""


    entities = concatenate_B_I_labels(entry, labels_list, outer_boxes)


    for i, label in enumerate(label_index):
        if labels_list[label] == "DIAGNOSIS":
            if entry['text'][i] != "DIAGNOSIS":
                diagnosis = entry['text'][i]
        elif labels_list[label] == "BP":
            bp = entry['text'][i]
        elif labels_list[label] == "TEMP":
            temp = entry['text'][i]
        elif labels_list[label] == "WEIGHT":
            weight = entry['text'][i]
        elif labels_list[label] == "HISTORY":
            history = entry['text'][i]
        elif labels_list[label] == "PULSE":
            pulse = entry['text'][i]


    for entity in entities:
        if entity['key'] == 'DIAGNOSIS':
            diagnosis = entity['text']
        elif entity['key'] == 'HISTORY':
            history = entity['text']



    diag_block = {
        'DIAGNOSIS': diagnosis,
        'BP': bp,
        'TEMP': temp,
        'WEIGHT': weight
    }

    if history != "":
        diag_block['HISTORY'] = history
    if pulse != "":
        diag_block['PULSE'] = pulse

    data['DIAG BLOCK'] = diag_block




    json_data = json.dumps(data, indent=4, ensure_ascii= False)
    print(json_data)
    output_file_path = "/content/drive/MyDrive/Digitizing Medical Prescription/Pipelines/Pipeline1_Output.json"

    # Write the JSON data to the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(json_data)

    print(f"JSON data saved to {output_file_path}")

    




def post_treatment_structuring(boxes,image,text,lab):
    entry = {"boundedbox":boxes,
            "image_path": image,
            "text": text,"label":lab}
    print(entry["text"])
    labels = entry["label"]
    for i in range(len(labels)):
        index = labels_list.index(labels[i])
        label_index.append(index)

    print("LABEL INDEX ", label_index)


    for label, box in zip(label_index, entry['boundedbox']):
        label_name = label_index[label]
        if label in target_labels:
            outer_boxes[tuple(box)] = label
    post_processing(entry)




def create_medicine_blocks(entry):
    medicine_entries = [{'label': labels_list[label], 'text': text, 'box': box}
                        for label, text, box in zip(label_index, entry['text'], entry['boundedbox'])
                        if labels_list[label] in ['MEDICINE TYPE', 'MEDICINE NAME', 'MEDICINE POWER', 'MEDICINE DOSE']]


    print('medicine_entries ---> ', medicine_entries)

    order = ['MEDICINE TYPE', 'MEDICINE NAME', 'MEDICINE POWER', 'MEDICINE DOSE']

    entities = concatenate_B_I_labels(entry, labels_list, outer_boxes)


    medicine_entries.sort(key=lambda x: (x['box'][1], order.index(x['label'])))

    print('medicine_entries_sorted ---> ', medicine_entries)


    i = 0
    while i < len(medicine_entries) - 1:
        if (medicine_entries[i]['label'] == 'MEDICINE DOSE' and medicine_entries[i + 1]['label'] == 'MEDICINE DOSE') or (medicine_entries[i]['label'] == 'MEDICINE DOSE' and medicine_entries[i + 2]['label'] == 'MEDICINE DOSE'):
            medicine_entries[i]['text'] += ' ' + medicine_entries[i + 1]['text']
            del medicine_entries[i + 1]
        else:
            i += 1

    print('New medicine entries --->>',medicine_entries)

    # Initialize the first block
    new_medicine_blocks = [{'MEDICINE TYPE': '', 'MEDICINE NAME': '', 'MEDICINE POWER': '', 'MEDICINE DOSE': ''}]

    for entry in medicine_entries:
        print('This is the medicine entry',entry)
        current_block = new_medicine_blocks[-1]
        print("CURRENT BLOCK IS THIS --->>",current_block)

        if current_block[entry['label']]:
            current_block = {'MEDICINE TYPE': '', 'MEDICINE NAME': '', 'MEDICINE POWER': '', 'MEDICINE DOSE': ''}
            new_medicine_blocks.append(current_block)

        current_block[entry['label']] = entry['text']


    occurrence = 0
    label_counts = {}


    for entry in medicine_entries:
        label = entry['label']
        if label in label_counts:
            label_counts[label] += 1
        else:
            label_counts[label] = 1



    return new_medicine_blocks




def concatenate_B_I_labels(entry, labels_list, outer_boxes):
    print(outer_boxes)
    entities = []
    current_entity = None

    for label, text, box in zip(label_index, entry['text'], entry['boundedbox']):
        label_name = labels_list[label]

        if label_name == 'B':
            if current_entity is not None:
                entities.append(current_entity)
            current_entity = {'text': text, 'box': box, 'key': None}
        elif label_name == 'I' and current_entity is not None:
            current_entity['text'] += ' ' + text
        else:
            if current_entity is not None:
                entities.append(current_entity)
            current_entity = None

    # Don't forget to add the last entity if it exists
    if current_entity is not None:
        entities.append(current_entity)



    # Assign the entities to their keys
    for entity in entities:
        #print(entity)
        for outer_box, key in outer_boxes.items():
             if box_within(entity['box'], outer_box):
                 entity['key'] = key
                 break

    return entities



def box_within(inner, outer):
    inner_center = [(inner[0] + inner[2]) / 2, (inner[1] + inner[3]) / 2]
    return (outer[0] <= inner_center[0] <= outer[2] and
            outer[1] <= inner_center[1] <= outer[3])



# Save json file
    output_file = os.path.join(output_dir, image_path[:-4] +"_post"+ ".json")
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(json_data)
