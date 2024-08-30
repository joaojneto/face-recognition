# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, jsonify, url_for
from elasticsearch import Elasticsearch
from PIL import Image, ExifTags
import face_recognition, base64, io, json

connection_file=open("connection.txt")
connection=connection_file.readlines()
connection=[conn.strip() for conn in connection]

es = Elasticsearch(
    connection[0],
    basic_auth=(connection[1],connection[2])
)

def register_Image(image, file_name):
    description = []
    image_base64 = []
    score = []
    try:
        im1 = Image.open(image)  
        im1 = im1.save(file_name)
        
        image = face_recognition.load_image_file(image)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        for face_encoding in face_encodings:
            face_encoding = face_encoding.tolist()

        #print(face_encoding)

        with open(file_name, "rb") as image_file:
            img64 = (base64.b64encode(image_file.read()))
            img64 = img64.decode('utf-8')

        connection_file=open("connection.txt")
        connection=connection_file.readlines()
        connection=[conn.strip() for conn in connection]

        #print(connection)

        es = Elasticsearch(
            connection[0],
            basic_auth=(connection[1],connection[2])
        )

        es.index(
            index="search_project",
            document={
                "face_vector": face_encoding,
                "image_base64": img64,
                "description": file_name,
            }
        )
    
        with open('static/images/awesome.png', "rb") as image_file:
            image_b64 = (base64.b64encode(image_file.read()))
            image_b64 = image_b64.decode("utf-8")

        score.append('-')
        image_base64.append("data:image/png;base64,"+ image_b64)
        description.append("Image was uploaded with success!!")
        
        return description, image_base64, score
        
    except Exception as e:
        print("Upps, error! ", e)
        with open('static/images/notFound.png', "rb") as image_file:
            image_b64 = (base64.b64encode(image_file.read()))
            image_b64 = image_b64.decode("utf-8")

        score.append('-')
        image_base64.append("data:image/png;base64,"+ image_b64)
        description.append("Image upload failed :/!")
        
        return description, image_base64, score

def searchFace(image, search_option):
    description = []
    image_base64 = []
    score = []
    try:
        image = face_recognition.load_image_file(image)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        if len(face_encodings) > 0:
            for face_encoding in face_encodings:
                face_encoding = face_encoding.tolist()
                if search_option != 'cosine':
                    query_elastic = {
                        "size": 1,
                        "_source": False, 
                        "knn": {
                            "field": "face_vector",
                            "query_vector": face_encoding,
                            #"k": 1,
                            "num_candidates": 10
                        },
                        "fields": [ "description","image_base64" ]
                    }
                response = es.search(index='search_project',body=query_elastic)
                response = dict(response)
                response = json.dumps(response)
                response = json.loads(response)
                print("Took time: " + str(response['took']))

                for hits in response['hits']['hits']:
                    if hits['_score'] >= 0.8:
                        score.append(hits['_score'])
                        image_base64.append("data:image/png;base64,"+ hits['fields']['image_base64'][0])
                        cut_description = hits['fields']['description'][0]
                        cut_description = cut_description[-9:]
                        description.append(cut_description)

                return description, image_base64, score
        else:
            raise ValueError('Erro to extract face')
    except Exception as e:
        with open('static/images/notFound.png', "rb") as image_file:
            image_b64 = (base64.b64encode(image_file.read()))
            image_b64 = image_b64.decode("utf-8")

        score.append('-')
        image_base64.append("data:image/png;base64,"+ image_b64)
        description.append("No faces detected")
        
        return description, image_base64, score

def get_orientation(image):
    try:
        exif = image.getexif()
        print("exif fun")
        if exif:
            for orientation in ExifTags.TAGS.keys():
                print("exif for")
                if ExifTags.TAGS[orientation] == 'Orientation':
                    print("exif if tag")
                    orientation_value = exif.get(orientation, None)
                    print(orientation_value)
                    return orientation_value
    except AttributeError:
        return None

app = Flask(__name__, static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

@app.route('/register', methods=['GET','POST'])
def registerImage():
    search_option = 'register'
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify(description='File not found', image_base64='')
        file = request.files['file']
        if file.filename == '':
            return jsonify(description='File not selected', image_base64='')
        if file:
            file_name = file.filename
            img = io.BytesIO(file.read())
            image = Image.open(img)
            
            try:
                orientation = get_orientation(image)
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                    image.save("temp.jpg")
                    img = "temp.jpg"
    
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                    image.save("temp.jpg")
                    img = "temp.jpg"
            
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
                    image.save("temp.jpg")
                    img = "temp.jpg"
            except AttributeError:
                print("Not to do here!")
        
            img_size = image.size
            description, image_base64, score = register_Image(img, file_name)

            return jsonify(description=description, image_base64=image_base64, score=score)
            
        else:
            return jsonify(description='Extension not allowed!', image_base64='')
        
    return render_template('indexRegister.html')

@app.route('/', methods=['GET','POST'])
def vectorSearch():
    search_option = 'vector'
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify(description='File not found', image_base64='')
        file = request.files['file']
        if file.filename == '':
            return jsonify(description='File not selected', image_base64='')
        if file:
            img = io.BytesIO(file.read())
            image = Image.open(img)
            image.save("temp.jpg")
        
            try:
                orientation = get_orientation(image)
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                    image.save("temp.jpg")
                    img = "temp.jpg"
    
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                    image.save("temp.jpg")
                    img = "temp.jpg"
            
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
                    image.save("temp.jpg")
                    img = "temp.jpg"
            except AttributeError:
                print("Not to do here!")
        
            img_size = image.size
            print(orientation)
            description, image_base64, score = searchFace(img, search_option)

            return jsonify(description=description, image_base64=image_base64, score=score)
            
        else:
            return jsonify(description='Extension not allowed!', image_base64='')
        
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)