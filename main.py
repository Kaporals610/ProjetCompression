import matplotlib.pyplot as plt
import numpy as np
import math as mp
from PIL import Image
from copy import copy
import time
from numpy import linalg as LA
import sys


#####################################################################
#                                                                   #
#                         CONSTANTES DU PRGRAMME                    #
#                                                                   #
#####################################################################


IMG_PATH_1 = 'im1.jpg'
IMG_PATH_2 = 'im2.jpg'
IMG_PATH_3 = 'im3.jpg'
IMG_PATH_4 = 'im4.jpg'
IMG_PATH_5 = 'im5.jpg'
IMG_PATH_6 = '4K.jpg'

MATRIX_Q = np.array([[16.0,11.0,10.0,16.0,24.0,40.0,51.0,61.0],
                    [12.0,12.0,13.0,19.0,26.0,58.0,60.0,55.0],
                    [14.0,13.0,16.0,24.0,40.0,57.0,69.0,56.0],
                    [14.0,17.0,22.0,29.0,51.0,87.0,80.0,62.0],
                    [18.0,22.0,37.0,56.0,68.0,109.0,103.0,77.0],
                    [24.0,35.0,55.0,64.0,81.0,104.0,113.0,92.0],
                    [49.0,64.0,78.0,87.0,103.0,121.0,120.0,101.0],
                    [72.0,92.0,95.0,98.0,112.0,100.0,103.0,99.0]])


#####################################################################################################
#                                                                                                   #
#             PETITE VERIFICATION DE L'EXTENSION    (MAIS PAS UTILISE DANS LE MAIN)                 #
#                                                                                                   #
#####################################################################################################



def checkExtension(path_image):
    
    path = path_image.split("/")
    name_image = path[-1].split(".")[0]
    extension = path[-1].split(".")[-1]
    path.pop(-1)
    path_folder = "/".join(path)
    

    return extension , path_folder, name_image


#####################################################################
#                                                                   #
#                    RECUPERATION DE L'IMAGE                        #
#                                                                   #
#####################################################################


    

def getImage(path_image):
    
    """ récupération de l'image et conversion si pas d'extension .jpg

    Args:
        path_image (string): chemin absolue vers l'image ou relatif

    Returns:
        tableau de tableau de pixels (et pas une matrice)
        
    """
    
    res = checkExtension(path_image)
    if(res[0] != "jpg"  or res[0] != "JPG"):
        im_bad_ext = Image.open(path_image)
        im_bad_ext.convert('RGB')
        good_img = im_bad_ext.save(res[2]+'.jpg')
    return plt.imread(res[2]+'.jpg') # renvoie un tableau de tableau de pixels




#####################################################################
#                                                                   #
#                             TRONCAGE                              #
#                                                                   #
#####################################################################





def DCTII_AND_COMPRESS(path_image,P,Pt,methode,frequence):
    """ Fonction appliquant une DCTII et une Compression (avec perte ici)

    Args:
        path_image (string): 
        P (np.array := matrix 2D): la matrice orthogonale P
        Pt (np.array := matrix 2D): la transposée de la de P
        methode (boolean): True si uniquement changement de base, False si changement de base + filtre hautes fréquences
        frequence (int): fréquence de coupure des hautes fréquences :
        
    Returns:
        (np.array := dim(x,y,z) = dim(largeur,hauteur,3)): matrice "3D" de l'image compressée
    """
    
    img_matrix = np.array(getImage(path_image))
    
    dim = np.shape(img_matrix) 
    width = dim[0] # largeur de l'image
    height = dim[1] # hauteur de l'image
    
    new_width = width - (width%8) # après troncage
    new_height = height - (height%8) # après troncage
    
    print("Résolution de l'image =",new_height,'*',new_width )
    
    for i in range(width-1, new_width-1,-1): # suppression des lignes en trop
        img_matrix = np.delete(img_matrix,i,0) # supression des colonnes en trop
    
    for j in range(height-1, new_height-1,-1):
        img_matrix = np.delete(img_matrix,j,1)
        
    
    img_matrix = img_matrix - 128.0  # centrage sur octet
    

    # COMPRESSION DE CHAQUE CANAL

    if(methode == True):
        
        print("Sans filtrage hautes fréquences")
  
        for i in range(0,new_width,8): 
            
            for j in range(0,new_height,8):
                
                # COMPRESSION DU CANAL R
                M = img_matrix[i:i+8,j:j+8,0]
                D = np.dot(np.dot(P,M),Pt)
                d_by_q = np.divide(D,MATRIX_Q)
                img_matrix[i:i+8,j:j+8,0] = d_by_q
                
                # COMPRESSION DU CANAL G
                M = img_matrix[i:i+8,j:j+8,1]
                D = np.dot(np.dot(P,M),Pt)
                d_by_q = np.divide(D,MATRIX_Q)
                img_matrix[i:i+8,j:j+8,1] = d_by_q
                
                # COMPRESSION DU CANAL B
                M = img_matrix[i:i+8,j:j+8,2]
                D = np.dot(np.dot(P,M),Pt)
                d_by_q = np.divide(D,MATRIX_Q)
                img_matrix[i:i+8,j:j+8,2] = d_by_q

        return img_matrix.astype(int),new_height,new_width # end function
    
    else:

        k, p = np.indices((8,8))
        print(k)
        print(p)
        print(k+p)
        for i in range(0,new_width,8): 
            
            for j in range(0,new_height,8):
                
                # COMPRESSION DU CANAL R
                
                M = img_matrix[i:i+8,j:j+8,0]
                D = np.dot(np.dot(P,M),Pt)
                d_by_q = np.divide(D,MATRIX_Q)
                d_by_q[k+p > frequence] = 0
                img_matrix[i:i+8,j:j+8,0] = d_by_q
                
                # COMPRESSION DU CANAL G
                M = img_matrix[i:i+8,j:j+8,1]
                D = np.dot(np.dot(P,M),Pt)
                d_by_q = np.divide(D,MATRIX_Q)
                d_by_q[k+p > frequence] = 0
                img_matrix[i:i+8,j:j+8,1] = d_by_q
                
                
                # COMPRESSION DU CANAL B
                M = img_matrix[i:i+8,j:j+8,2]
                D = np.dot(np.dot(P,M),Pt)
                d_by_q = np.divide(D,MATRIX_Q)
                d_by_q[k+p > frequence] = 0
                img_matrix[i:i+8,j:j+8,2] = d_by_q

        return img_matrix.astype(int),new_height,new_width # end function
    

    
                


#####################################################################
#                                                                   #
#                        MATRICE ORTHOGONALE                        #
#                                                                   #
#####################################################################


def matrixPassageOrtho(n):
    """Calcul de la matrice orthogonale

    Args:
        n pour la taille de la matrice carré (ici 8 pour notre algorithme)

    Returns (np.array := dim(x,y) = dim(8,8)):
        
    """
    P = np.array([[0.0]*n]*n)
    C0 = 1/(mp.sqrt(2))
    for i in range(0,n):
        for j in range(0,n):
            if (i == 0 ):
                P[i,j] = (1.0/2.0) * C0 * np.cos((2.0*float(j) + 1.0) * float(i) * mp.pi/16.0)
            else:
                P[i,j] = (1.0/2.0) * mp.cos((2.0*float(j) + 1.0) * float(i) * mp.pi/16.0)
    return P



def Filtre(bloc, filtre):
    """filtrage du bloc donné en argument

    Args:
        bloc (np.array := matrix 2D): le bloc non-filtré
        filtre (int): la fréquence du filtre

    Returns:
        np.array := matrix 2D : le même bloc mais filtré
    """
    
    new_bloc = np.array([[0.0]*8]*8)
    
    for i in range(8):
        for j in range(8):
            if((i+j) >= filtre):
                new_bloc[i,j] = 0.0
            else:
                new_bloc[i,j] = bloc[i,j]
                
    return new_bloc


#####################################################################
#                                                                   #
#                         DECOMPRESSION                             #
#                                                                   #
#####################################################################



def DECOMPRESSION(matrix_compress,P ,Pt):
    """ Fonction de décompression de l'image :
        Le choix a été fait de renvoyer une copie de la matrice et de ne pas modififier la référence.

    Args:
        matrix_compress (np.array := matrix 3D := dim(largeur,hauteur,3)): la matrice compressé de l'image
        P (np.array := matrix 2D): la matrice orthogonale P
        Pt (np.array := matrix 2D): la transposée de la de P

    Returns:
        (np.array := dim(x,y,z) = dim(largeur,hauteur,3)): matrice "3D" de l'image décompressé
    """
    
    dim = np.shape(matrix_compress) # on récupère les attributs de dimension de la matrice
    width = dim[0]                  # largeur de l'image (int)
    height = dim[1]                 # hauteur de l'image (int)
    
    matrix_decompress = np.empty((width,height,3))  
    

    for i in range(0,width,8):
        
        for j in range(0,height,8):
            
            # DECOMPRESSION DU CANAL R
            D = matrix_compress[i:i+8,j:j+8,0]
            Q = (np.multiply(D,MATRIX_Q)) 
            M = np.dot(np.dot(Pt,Q),P) + 128.00
            matrix_decompress[i:i+8,j:j+8,0] = M
            
            # DECOMPRESSION DU CANAL G
            D = matrix_compress[i:i+8,j:j+8,1]
            Q = (np.multiply(D,MATRIX_Q)) 
            M = np.dot(np.dot(Pt,Q),P) + 128.00
            matrix_decompress[i:i+8,j:j+8,1] = M
            
            # DECOMPRESSION DU CANAL B
            D = matrix_compress[i:i+8,j:j+8,2]
            Q = (np.multiply(D,MATRIX_Q)) 
            M = np.dot(np.dot(Pt,Q),P) + 128.00
            matrix_decompress[i:i+8,j:j+8,2] = M
        
    return matrix_decompress.astype(int)





            
#####################################################################
#                                                                   #
#                   MAIN LANCEMENT DU PROGRAMME                     #
#                                                                   #
#####################################################################



P = matrixPassageOrtho(8)
Pt = P.transpose()

arg = sys.argv[1]
img = np.array(getImage(arg))

filtre = int(sys.argv[2])

start_time_compression = time.time()

image_compress = DCTII_AND_COMPRESS(arg,P,Pt,False,filtre)

final_time_compression = time.time()

start_time_decompression = time.time()

image_decompress = DECOMPRESSION(image_compress[0],P,Pt)

final_time_decompression = time.time()



#####################################################################
#                                                                   #
#                   AFFICHAGE DE QUELQUES INFOS UTILES              #
#                                                                   #
#####################################################################


print('Compression Ratio =',(1-((np.count_nonzero(image_compress[0]))/(image_compress[1]*image_compress[2]*3)))*100,' %')

print('Erreur en Norme L2 =',(LA.norm(img-image_decompress)/LA.norm(img))*100,' %')

print("Nombres de blocs traités =", (image_compress[1]*image_compress[2])/64)

print("Temps Exécution Compression =",(final_time_compression - start_time_compression), " secondes")

print("Temps Exécution Décompression =",(final_time_decompression - start_time_decompression), " secondes")

print("Temps Exécution Compression + Décompression =", final_time_decompression - start_time_compression, " secondes")


#####################################################################
#                                                                   #
#     AFFICHAGE DE L'IMAGE APRES COMPRESSION - DECOMPRESSION        #
#                                                                   #
#####################################################################

# COMPRESSION - DECOMPRESSION
# plt.figure("image compressée puis décompressée")
# plt.imshow(image_decompress)

# # ORIGINELLE
# plt.figure("image de base")
# plt.imshow(img)
# plt.show()









        
    
    
    
    




                
            
            













