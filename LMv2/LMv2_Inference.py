from PGNet_LMv2_postprocessing import PGNettoLayoutLMv2
from LMLayout_Classification import layout_classification
from After_LMv2_Postprocess import post_treatment_structuring
import numpy as np

def lm_inference(image,text):
    #print("in lm inference")
    temp = []


###### ONLY use this section if there is a sequence in total contour values otherwise DONOT use the code block! #############
    # height = image.shape[0]
    # width = image.shape[1]
    # for contour in Total_contours_values:
    #     x_min,y_min,x_max,y_max,color= contour
    #     #temp.insert(0,x_min)
    #     #temp.insert(1,y_min)
    #     #temp.insert(2,x_max)
    #     #temp.insert(3,y_max)
    #    # Total_contour_values_for_LM.append(temp)
    #     Total_contour_values_for_LM = [Total_contours_values[i:i+3] for i in range(0, len(Total_contours_values), 3)]
    #     normalize_bbox(x_min,y_min,x_max,y_max,width,height)
        # temp.clear()
#################################################################################################################################

    #print("Original Coordinates: ",Total_contour_values_for_LM,"/n")
    #print("Normalizaed coordinates: ",Normalized_Total_contour_values_for_LM,"/n")

    
    imageN, Transcriptions, Normalized_boxes, PGNet_predicted_boxes = PGNettoLayoutLMv2(image, text)

    





    dummy_labels = [np.random.choice(range(12), replace=False) for _ in range(len(text))]

    labels = layout_classification(imageN,Transcriptions,Normalized_boxes,PGNet_predicted_boxes,dummy_labels)
    # Uncomment if you wish to see the current labels list!
    # print("LABELS")
    #print(Labels)
    # Total_contours_values.clear()
    #print("lminferencetolayoutclassification")
    post_treatment_structuring(PGNet_predicted_boxes, imageN, Transcriptions, labels)


    # returns labels
    return labels