conda create -n yolo_image_search_gpu python=3.11 -y
conda activate yolo_image_search_gpu
conda install pytorch==2.5.1 torchvision==0.20.1 pytorch-cuda=12.4 -c pytorch -c nvidia
pip install -r requirements.txt