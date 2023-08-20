import cv2



from transformers import LayoutLMv2Processor, AutoTokenizer
from transformers import LayoutLMv2Processor, AutoTokenizer
from transformers import LayoutLMv2ForTokenClassification, AdamW






device = "cpu"
lm_tokenizer = AutoTokenizer.from_pretrained("microsoft/layoutlm-base-uncased")
lm_processor = LayoutLMv2Processor.from_pretrained("microsoft/layoutlmv2-base-uncased", revision="no_ocr")

# list, dir_path and model initialization for Layout LM v2
Labels = []
lm_model_path = '/content/drive/MyDrive/Digitizing Medical Prescription/LM_V2_FT_weights'
lm_model = LayoutLMv2ForTokenClassification.from_pretrained(lm_model_path)

# List and index initialization for labeling
labels = ["NAME","AGE","GENDER","DATE","DIAGNOSIS","HISTORY","BP","TEMP","WEIGHT","MEDICINE TYPE", "MEDICINE NAME","MEDICINE POWER","MEDICINE DOSE","B"] #,"BLOCK"
label2idx ={"NAME": 0,"AGE": 1,"GENDER": 2,"DATE": 3,"DIAGNOSIS": 4,"HISTORY": 5,"BP": 6,"TEMP": 7,"WEIGHT": 8, "MEDICINE TYPE": 9,"MEDICINE NAME": 10,"MEDICINE POWER": 11,"MEDICINE DOSE": 12, "B": 13}
idx2label = {0:"NAME", 1:"AGE", 2:"GENDER", 3:"DATE", 4:"DIAGNOSIS", 5:"HISTORY", 6:"BP", 7:"TEMP", 8:"WEIGHT", 9:"MEDICINE TYPE", 10:"MEDICINE NAME", 11:"MEDICINE POWER", 12:"MEDICINE DOSE", 13:"B"}






def layout_classification(image,text_file,bounding_boxes,org_bbox,dummy_labels):


    encoded_inputs = lm_processor(image, text_file, boxes=bounding_boxes,word_labels = dummy_labels,
                               padding="max_length", truncation=True, return_tensors="pt")



    labels = encoded_inputs.pop("labels").squeeze().tolist()
    for k,v in encoded_inputs.items():
        encoded_inputs[k] = v.long()
        encoded_inputs[k] = v.to(device)



    lm_model.to(device)
    outputs = lm_model(**encoded_inputs)




    predictions = outputs.logits.argmax(-1).squeeze().tolist()
    token_boxes = encoded_inputs.bbox.squeeze().tolist()
    print(predictions, token_boxes)
    print("in layout classification")

    #height = image.shape[0]
    #width = image.shape[1]
    print(predictions)




    valid_predictions = [prediction for prediction in predictions if prediction in idx2label]
    true_predictions = [idx2label[prediction] for prediction, label in zip(valid_predictions, labels) if label != -100]
    print(f'Predictions are :{true_predictions}')

    label2color =  {'NAME': 'blue',
      'AGE': 'green',
      'GENDER': 'orange',
      'DATE': 'red',
      'MEDICINE TYPE': 'pink',
      'MEDICINE NAME': 'black',
      'MEDICINE POWER': 'purple',
      'MEDICINE DOSE': 'red',
      'DIAGNOSIS': 'green',
      'HISTORY': 'green',
      'BP': 'green',
      'TEMP': 'green',
      'WEIGHT': 'green'
      }

    for prediction, box,text in zip(true_predictions, org_bbox,text_file):
        print("box:", box)
        for item in box:
          if not isinstance(item, int):
              print("not an integer")



        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_color = (0, 0, 0)  # Black
        font_thickness = 1
        cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 0, 0), 2)  # Black rectangle
        # Put text
        text_size = cv2.getTextSize(prediction, font, font_scale, font_thickness)[0]
        cv2.putText(image, prediction+":"+text, (box[0] + 10, box[1] - 10),
            font, font_scale, font_color, font_thickness, lineType=cv2.LINE_AA)
    cv2.imwrite("LM.jpg", image) # Uncomment this if you wish to see the LM output!
    print("done so far")


    for prediction, box,text in zip(true_predictions, org_bbox,text_file):
       print("LM Output: ")
       print("BOX values: ",box,"/n")
       print("Prediction ",prediction,"/n")
       print("Text ",text,"/n")
       Labels.append(prediction)

    return true_predictions