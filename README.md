# captcha-solver
simple captcha solver, based on https://medium.com/@ageitgey/how-to-break-a-captcha-system-in-15-minutes-with-machine-learning-dbebb035a710

## Prerequisite
* Keras
* Tensorflow
* OpenCV 3


## Usage

### Step 1: Generate captcha images
`python start.py start_generate` 

### Step 2: Extract character images from Step 1
`python start.py start_extract` 

### Step 3: Train model with character images
`python start.py start_train`


### Step 4: Predict model
`python start.py start_predict -i path/to/captchas` 


## Notice
* Directories and files prefix with **eopt** are about an example, which just make captcha-sovler more pratical. Ignore them please.