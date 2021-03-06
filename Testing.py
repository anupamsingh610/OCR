import cv2, operator, os, numpy as np

# module level variables ##########################################################################
MIN_CONTOUR_AREA = 50
RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 20
PATH = "test C1.jpg"
DIVISION_FACTOR = 600

allContoursWithData = []
validContoursWithData = []

# SZ=20
# bin_n = 16 # Number of bins
# affine_flags = cv2.WARP_INVERSE_MAP|cv2.INTER_LINEAR
# svm_params = dict( kernel_type = cv2.SVM_LINEAR,svm_type = cv2.SVM_C_SVC,C=2.67, gamma=5.383 )
class ContourWithData():

    def __init__(self):

        self.npaContour = None           # contour
        self.boundingRect = None         # bounding rect for contour
        self.intRectX = 0                # bounding rect top left corner x location
        self.intRectY = 0                # bounding rect top left corner y location
        self.intRectWidth = 0            # bounding rect width
        self.intRectHeight = 0           # bounding rect height
        self.fltArea = 0.0               # area of contour
        self.aspectRatio = 0.0
        self.XCentroid = 0.0
        self.YCentroid = 0.0

    def rectDetails(self):               # calculate bounding rect info
        [intX, intY, intWidth, intHeight] = self.boundingRect
        self.intRectX = intX
        self.intRectY = intY
        self.intRectWidth = intWidth
        self.intRectHeight = intHeight
        self.aspectRatio = float(intWidth) / intHeight
        self.XCentroid = intX + intWidth/2
        self.YCentroid = intY + intHeight/2

    def contourCheck(self):
        if self.fltArea > MIN_CONTOUR_AREA and (0.5 < self.aspectRatio < 2): return True    # much better validity checking would be necessary  
        return False


def knn():
    npaFlattenedImages= np.loadtxt("flattened_alphabets.txt",np.float32) 
    npaClassifications= np.loadtxt("classification_alphabets.txt", np.float32)
    kNearest = cv2.KNearest()
    kNearest.train(npaFlattenedImages, npaClassifications)
    return kNearest

def preprocess(image):
    imgGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imgBlurred = cv2.GaussianBlur(imgGray, (5,5), 0)
    imgThresh = cv2.adaptiveThreshold(imgBlurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,2)
    # cv2.imshow('imgThresh',imgThresh)
    imgThreshCopy = imgThresh.copy()
    return imgThresh, imgThreshCopy

def getContourDetails(npaContours):

    for npaContour in npaContours:
        # print cv2.contourArea(npaContour)
        contourWithData = ContourWithData()                                             # instantiate a contour with data object
        contourWithData.npaContour = npaContour                                         # assign contour to contour with data
        contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)     # get the bounding rect
        contourWithData.rectDetails()                    # get bounding rect info
        contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)           # calculate the contour area
        allContoursWithData.append(contourWithData)


    return allContoursWithData

# def compare(contourWithData1,contourWithData2):
#     if(contourWithData1.intRectY - contourWithData2.intRectY < 10):
#         if(contourWithData1.intRectX < contourWithData2.intRectX):
#             return -1
#         elif(contourWithData1.intRectX > contourWithData2.intRectX):
#             return 1
#         else:
#             return 0
#     else:
#         if(contourWithData1.intRectY < contourWithData2.intRectY):
#             return -1
#         elif(contourWithData1.intRectY > contourWithData2.intRectY):
#             return 1
#         else:
#             return 0

def compare(contourWithData1,contourWithData2):
    if(contourWithData1.intRectY - contourWithData2.intRectY < 10):
        if(contourWithData1.intRectX < contourWithData2.intRectX):
            return -1
        elif(contourWithData1.intRectX > contourWithData2.intRectX):
            return 1
        else:
            return 0
    else:
        return 0

def getValidContours(allContoursWithData):

    for contourWithData in allContoursWithData:
        if contourWithData.contourCheck():
            validContoursWithData.append(contourWithData)

    validContoursWithData.sort(key = operator.attrgetter("intRectY"))
    validContoursWithData.sort(cmp = compare)
    # validContoursWithData.sort(cmp = compare)
    return validContoursWithData

def formattingCheck(contourWithData, i, length): 
        if (i != length):
            nextContour = validContoursWithData[i]
        else:
            nextContour = validContoursWithData[i-1]
            # print strFinalString
        if(nextContour.YCentroid - contourWithData.YCentroid > 30):
            line_change = "\n"
        else:
            line_change = ""
        if (nextContour.XCentroid - contourWithData.XCentroid> 40):
            return " ",line_change     #Much better Check required
        return "",line_change

    
def OCR(img, imgThresh, validContoursWithData):
    
    kNearest = knn()
    strFinalString = ""
    i = 0
    a = 0.0
    length = len(validContoursWithData)
    print length
    for contourWithData in validContoursWithData:
        i += 1
        # if(i > 9 ):
        cv2.rectangle(img, (contourWithData.intRectX, contourWithData.intRectY),(contourWithData.intRectX + contourWithData.intRectWidth, contourWithData.intRectY + contourWithData.intRectHeight),(0, 255, 0),2)
        # if(i == 45):
        # cv2.putText(img, str(i), (contourWithData.XCentroid, contourWithData.YCentroid),  cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        imgROI = imgThresh[contourWithData.intRectY : contourWithData.intRectY + contourWithData.intRectHeight,contourWithData.intRectX : contourWithData.intRectX + contourWithData.intRectWidth]
        imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))
        npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
        #npaROIResized = deskew(npaROIResized)
        npaROIResized = np.float32(npaROIResized)


        retval, npaResults, neigh_resp, dists = kNearest.find_nearest(npaROIResized, k = 1)
        #npaResults = svm.predict_all(npaROIResized)
        strCurrentChar = chr(int(npaResults[0][0]))
        
        space,line_change = formattingCheck(contourWithData, i, length)
        strFinalString = strFinalString + strCurrentChar + space + line_change


        # cv2.namedWindow('Fuck '+str(i), cv2.WINDOW_NORMAL)
        # cv2.imshow('Fuck '+str(i), imgROI)
        # print strCurrentChar

        # if (cv2.waitKey(0) & 255) == 121:  ### For Windows Os remove 255 from this line ###
        #     a = a + 1
        # cv2.destroyAllWindows()
        # print contourWithData.intRectX, contourWithData.intRectY

    # print 'Accuracy:', a/ i
    print strFinalString

def main():

    img = cv2.imread(PATH)
    RP = img.shape[0]/ DIVISION_FACTOR if img.shape[0] <= img.shape[1] else img.shape[1]/ DIVISION_FACTOR
    img = cv2.resize (img, (img.shape[1] / RP, img.shape[0] / RP))
    #cv2.imshow('imgTestingNumber1',img)
    imgThreshCopy, imgThresh = preprocess(img)

    npaContours, npaHierarchy = cv2.findContours(imgThreshCopy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(img,npaContours,-1,(255,255,0),2)

    allContoursWithData = getContourDetails(npaContours)

    validContoursWithData = getValidContours(allContoursWithData)

    OCR(img, imgThresh, validContoursWithData)
    #print "\n" + strFinalString + "\n"

    cv2.imshow("img.jpg", img)
    # cv2.imwrite("photo_ocr_example.jpg",img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return
            
main()