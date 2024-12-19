# Real-time Image Processing Flask App
Real-Time Image Processing with Flask and Docker (Mobile Friendly)
## Preview
asd
## How to run
Run this in your *project-folder/docker* path:
```
docker build -t container_name .
```
Then this:
```
docker run --rm -p 5002:5002 container_name
```
## Libraries
- flask==3.0.1
- gunicorn==21.2.0
- pillow
- opencv-python
- numpy
