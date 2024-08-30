# FACE RECGONITION APP (Elastic Vector Search) 😊

[SLIDE DECK]([Search%20Project]%20Vectors_%20You%20Know,%20for%20Search.pdf)

### Environment 🖥️

Python 3.12.3

Debian 12 (Packges build-essential, cmake, python3-dev)

`# apt install build-essential cmake python3-dev`

### HOW TO 🔧

* First you need to create the index mapping:

```json
{
  "search_project": {
    "mappings": {
      "properties": {
        "description": {
          "type": "keyword"
        },
        "face_vector": {
          "type": "dense_vector",
          "dims": 128,
          "index": true,
          "similarity": "l2_norm"
        },
        "image_base64": {
          "type": "text"
        }
      }
    }
  }
}
```

* Next step, edit the **connection.txt** file with Elasticsearch endpoint, user and password!

* Create and access a virtual environment:

`$ python -m venv venv && source venv/bin/activate`

* Update pip

`$ pip install --upgrade pip setuptools`

* Now you need to install the requirements: 

`$ pip install requirements.txt`

* After that you will be able to run the app: 🚀 

`$ python app.py`

* Access http://localhost and you need to see this page: 👀

![alt text](image.png)

BUT, you need to upload some images before searching! 😅 

* Click **Register** and you will be redirect to another page, here you can uploading your images.

![alt text](image-5.png)

## ENJOY YOUR FACE RECOGNITION APP 😚🎉
